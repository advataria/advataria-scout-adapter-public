#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AdvaScout uAgent (MVP) – Windows friendly
----------------------------------------

- obalí tvoju funkciu run_scout(job) z 01_adva_agent_scout.py
- agent prijme URL a vráti štruktúrovaný obsah o stránke
- funguje s Agentverse Mailbox aj na Windows (SelectorEventLoop)
"""

import os
import time
import importlib.util
import asyncio
from pathlib import Path

from uagents import Agent, Context

# SPOLOČNÉ MODELY (JEDINÝ ZDROJ PRAVDY)
from adva_scout_models import ScoutRequest, ScoutResponse, ScoutResponseClient


# =====================================================================
# 0) Windows fix pre aiodns / asyncio
# =====================================================================

if os.name == "nt":
    # aiodns / aiohttp na Windows vyžaduje SelectorEventLoop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# =====================================================================
# 1) ENVIRONMENT VARIABLES (seed, port, endpoint)
# =====================================================================

ADVA_SCOUT_AGENT_SEED = os.getenv(
    "ADVA_SCOUT_AGENT_SEED",
    "demo-seed-not-for-production-12345"  # fallback pre public repo / lokálne testy
)

ADVA_SCOUT_AGENT_PORT = int(os.getenv("ADVA_SCOUT_AGENT_PORT", "8010"))

ADVA_SCOUT_AGENT_ENDPOINT = os.getenv(
    "ADVA_SCOUT_AGENT_ENDPOINT",
    "http://127.0.0.1:8010/submit"
)


# =====================================================================
# 2) Dynamický import run_scout z 01_adva_agent_scout.py
# =====================================================================

ROOT_DIR = Path(__file__).resolve().parent
SCOUT_PATH = ROOT_DIR / "01_adva_agent_scout.py"


def load_run_scout():
    """Načíta run_scout(job) aj keď súbor začína číslom."""
    if not SCOUT_PATH.exists():
        raise FileNotFoundError(f"Súbor {SCOUT_PATH} neexistuje")

    spec = importlib.util.spec_from_file_location("adva_scout_mod", SCOUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    if not hasattr(module, "run_scout"):
        raise AttributeError("V 01_adva_agent_scout.py chýba funkcia run_scout(job).")

    return module.run_scout


run_scout = load_run_scout()


# =====================================================================
# 3) Konfigurácia uAgenta (mailbox + lokálny endpoint)
# =====================================================================

agent = Agent(
    name="adva_scout_uagent",
    seed=ADVA_SCOUT_AGENT_SEED,
    port=ADVA_SCOUT_AGENT_PORT,
    endpoint=[ADVA_SCOUT_AGENT_ENDPOINT],
    mailbox=True,
    publish_agent_details=True,
)


# =====================================================================
# 4) Helper – konverzia request → job dict
# =====================================================================

def build_job(req: ScoutRequest) -> dict:
    """
    Prevedie ScoutRequest -> job dict pre run_scout(job).

    Výsledná štruktúra zodpovedá tvojmu pôvodnému job_input.json:
    {
      "job_id": "...",
      "client_url": "...",
      "competitor_urls": [...],
      "uploaded_docs": [...],
      "client_form": {...}
    }
    """
    return {
        "job_id": f"scout-{int(time.time())}",
        "client_url": req.url,
        "competitor_urls": [],
        "uploaded_docs": [],
        "client_form": {},
    }


# =====================================================================
# 5) Eventy a message handlers
# =====================================================================

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("AdvaScout uAgent štartuje...")
    ctx.logger.info(f"ADRESA agenta: {agent.address}")
    ctx.logger.info("Agent pripravený na spracovanie ScoutRequest")


@agent.on_message(model=ScoutRequest)
async def handle_request(ctx: Context, sender: str, req: ScoutRequest):
    """
    Hlavný handler:
    - prijme ScoutRequest { url }
    - pripraví job dict
    - zavolá run_scout(job) → Content Pack
    - zabalí výsledok do ScoutResponse a odošle späť
    """
    ctx.logger.info(f"Prijatá požiadavka od {sender}: {req.url}")

    try:
        job = build_job(req)
        result = run_scout(job)

        client = result["client"]
        meta = result["meta"]

        response = ScoutResponse(
            job_id=result["job_id"],
            client=ScoutResponseClient(
                url=client["url"],
                title=client["title"],
                meta=client["meta"],
                headings=client["headings"],
                top_text=client["top_text"],
            ),
            scraped_at=meta["scraped_at"],
            status=result["status"],
        )

        await ctx.send(sender, response)
        ctx.logger.info("Odoslaná odpoveď")

    except Exception as e:
        ctx.logger.exception("Chyba pri spracovaní požiadavky")

        err = ScoutResponse(
            job_id=f"error-{int(time.time())}",
            client=ScoutResponseClient(
                url=req.url,
                title="",
                meta="",
                headings="",
                top_text="",
            ),
            scraped_at="",
            status="error",
            error=str(e),
        )
        await ctx.send(sender, err)


# =====================================================================
# 6) Štart agenta
# =====================================================================

if __name__ == "__main__":
    agent.run()
