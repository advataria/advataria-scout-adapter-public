#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
01_adva_uagent_scout.py
-----------------------

This is my AdvaScout uAgent (MVP) adapter.

What I do here:
- I wrap my existing run_scout(job) function (from 01_adva_agent_scout.py).
- I expose it as a uAgent service:
    ScoutRequest(url)  ->  ScoutResponse(structured website content)

Why this matters for Fetch:
- I can demonstrate:
  1) A real agent endpoint that processes a request and returns structured JSON.
  2) Optional on-chain presence (testnet) + Almanac registration (discoverability).

Notes:
- This file is written to be Windows friendly (SelectorEventLoop policy).
- I include explicit "FETCH EVIDENCE" logs for screen recording.
"""

import os
import time
import importlib.util
import asyncio
from pathlib import Path

from uagents import Agent, Context

# Optional (only needed if you want auto-funding for testnet)
try:
    from uagents.setup import fund_agent_if_low
except Exception:
    fund_agent_if_low = None

# Shared models (single source of truth)
from adva_scout_models import ScoutRequest, ScoutResponse, ScoutResponseClient

# ===============================================================
# 0) Windows asyncio fix
# ===============================================================

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ===============================================================
# 1) Env configuration
# ===============================================================

ADVA_SCOUT_AGENT_SEED = os.getenv(
    "ADVA_SCOUT_AGENT_SEED",
    "demo-seed-not-for-production-12345",
)

ADVA_SCOUT_AGENT_PORT = int(os.getenv("ADVA_SCOUT_AGENT_PORT", "8010"))

ADVA_SCOUT_AGENT_ENDPOINT = os.getenv(
    "ADVA_SCOUT_AGENT_ENDPOINT",
    "http://127.0.0.1:8010/submit",
)

# If you want on-chain testnet registration:
# set ADVA_SCOUT_NETWORK=testnet
ADVA_SCOUT_NETWORK = os.getenv("ADVA_SCOUT_NETWORK", "").strip().lower()

# ===============================================================
# 2) Console helpers (bold logs for video)
# ===============================================================

ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

def bold(text: str) -> str:
    if os.getenv("NO_COLOR") == "1":
        return text
    return f"{ANSI_BOLD}{text}{ANSI_RESET}"

# ===============================================================
# 3) Dynamic import: load run_scout(job) from 01_adva_agent_scout.py
# ===============================================================

ROOT_DIR = Path(__file__).resolve().parent
SCOUT_PATH = ROOT_DIR / "01_adva_agent_scout.py"

def load_run_scout():
    """
    I dynamically load run_scout(job) because the module name starts with digits in my project structure.
    """
    if not SCOUT_PATH.exists():
        raise FileNotFoundError(f"Missing file: {SCOUT_PATH}")

    spec = importlib.util.spec_from_file_location("adva_scout_mod", SCOUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    if not hasattr(module, "run_scout"):
        raise AttributeError("01_adva_agent_scout.py must export run_scout(job).")

    return module.run_scout

run_scout = load_run_scout()

# ===============================================================
# 4) Agent configuration
# ===============================================================

agent_kwargs = dict(
    name="adva_scout_uagent",
    seed=ADVA_SCOUT_AGENT_SEED,
    port=ADVA_SCOUT_AGENT_PORT,
    endpoint=[ADVA_SCOUT_AGENT_ENDPOINT],
    mailbox=True,                 # shows Agentverse inspector link
    publish_agent_details=True,   # publish metadata for discoverability
)

# If network=testnet is enabled, pass it explicitly
if ADVA_SCOUT_NETWORK == "testnet":
    agent_kwargs["network"] = "testnet"

agent = Agent(**agent_kwargs)

# Auto-fund on testnet (optional but recommended for Starter Grant demos)
if ADVA_SCOUT_NETWORK == "testnet" and fund_agent_if_low is not None:
    # This triggers testnet faucet funding if my balance is low.
    # It helps with Almanac contract registration.
    fund_agent_if_low(agent.wallet.address())

# ===============================================================
# 5) Request -> job dict helper
# ===============================================================

def build_job(req: ScoutRequest) -> dict:
    """
    I convert ScoutRequest to the original job schema used by my internal scout pipeline.
    """
    return {
        "job_id": f"scout-{int(time.time())}",
        "client_url": req.url,
        "competitor_urls": [],
        "uploaded_docs": [],
        "client_form": {},
    }

# ===============================================================
# 6) Startup log (FETCH EVIDENCE)
# ===============================================================

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(bold("=== [FETCH EVIDENCE] AdvaScout uAgent starting ==="))
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] Agent address: {agent.address} ==="))
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] Endpoint: {ADVA_SCOUT_AGENT_ENDPOINT} ==="))

    if ADVA_SCOUT_NETWORK == "testnet":
        ctx.logger.info(bold("=== [FETCH EVIDENCE] Network mode: TESTNET (Almanac on-chain registration enabled) ==="))
    else:
        ctx.logger.info(bold("=== [FETCH EVIDENCE] Network mode: LOCAL (set ADVA_SCOUT_NETWORK=testnet to enable on-chain registration) ==="))

    ctx.logger.info("Agent is ready to process ScoutRequest messages.")

# ===============================================================
# 7) Main handler: ScoutRequest -> run_scout -> ScoutResponse
# ===============================================================

@agent.on_message(model=ScoutRequest)
async def handle_request(ctx: Context, sender: str, req: ScoutRequest):
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] Incoming ScoutRequest from {sender} ==="))
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] Target URL: {req.url} ==="))

    try:
        job = build_job(req)
        result = run_scout(job)

        client = result["client"]
        meta = result["meta"]

        response = ScoutResponse(
            job_id=result["job_id"],
            client=ScoutResponseClient(
                url=client.get("url", ""),
                title=client.get("title", ""),
                meta=client.get("meta", ""),
                headings=client.get("headings", ""),
                top_text=client.get("top_text", ""),
            ),
            scraped_at=meta.get("scraped_at", ""),
            status=result.get("status", "success"),
        )

        await ctx.send(sender, response)
        ctx.logger.info(bold("=== [FETCH EVIDENCE] ScoutResponse sent successfully ==="))

    except Exception as e:
        ctx.logger.exception("Error while processing ScoutRequest")

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
        ctx.logger.info(bold("=== [FETCH EVIDENCE] Error response sent ==="))

# ===============================================================
# 8) Run
# ===============================================================

if __name__ == "__main__":
    agent.run()
