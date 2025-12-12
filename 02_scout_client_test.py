#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
02_scout_client_test.py
----------------------

This is my one-shot test client for the AdvaScout uAgent.

What I do in this script:
1) I start a small uAgent locally (TESTNET mode).
2) I publish my endpoint so the Scout agent can reply to me.
3) I send a ScoutRequest with a target URL.
4) I wait for exactly one ScoutResponse.
5) I print the result in a very explicit, video-friendly format.
6) I terminate the process cleanly.

Important design decisions:
- I do NOT use the Agentverse mailbox here.
  Local endpoints are enough and this avoids 401 credential errors.
- I do NOT call ctx.stop().
  ExternalContext does not support stop() in my uAgents version.
- This script is intentionally simple and deterministic,
  ideal for screen recording and Fetch grant evidence.
"""

import os
import signal
import asyncio
from uagents import Agent, Context

# Shared models (same as Scout agent)
from adva_scout_models import ScoutRequest, ScoutResponse

# ===============================================================
# 0) Windows asyncio fix
# ===============================================================

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ===============================================================
# 1) Configuration
# ===============================================================

SCOUT_AGENT_ADDRESS = os.getenv(
    "SCOUT_AGENT_ADDRESS",
    "agent1qd599ru4jc6z9dtjh03uypr6epxry43rflf72lzhmz6tetj7m9vpwc0ff3x",
)

TEST_URL = os.getenv("SCOUT_TEST_URL", "https://fetch.ai")

CLIENT_PORT = int(os.getenv("ADVA_SCOUT_CLIENT_PORT", "8000"))
CLIENT_ENDPOINT = os.getenv(
    "ADVA_SCOUT_CLIENT_ENDPOINT",
    "http://127.0.0.1:8000/submit",
)

CLIENT_SEED = os.getenv(
    "ADVA_SCOUT_CLIENT_SEED",
    "advataria-scout-client-seed-demo",
)

# ===============================================================
# 2) Console helpers (bold output for video)
# ===============================================================

ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

def bold(text: str) -> str:
    if os.getenv("NO_COLOR") == "1":
        return text
    return f"{ANSI_BOLD}{text}{ANSI_RESET}"

def hard_exit_ok() -> None:
    """
    Clean one-shot exit after receiving the response.
    """
    try:
        os.kill(os.getpid(), signal.SIGINT)
    except Exception:
        raise SystemExit(0)

# ===============================================================
# 3) Client agent definition
# ===============================================================

client = Agent(
    name="adva_scout_test_client",
    seed=CLIENT_SEED,
    port=CLIENT_PORT,
    endpoint=[CLIENT_ENDPOINT],
    mailbox=False,               # no Agentverse mailbox → no 401 errors
    publish_agent_details=True,  # important: publish endpoint to Almanac
    network="testnet",           # must match Scout agent network
)

# ===============================================================
# 4) Startup: send ScoutRequest
# ===============================================================

@client.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(bold("=== [FETCH EVIDENCE] AdvaScout TEST CLIENT started ==="))
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] Client endpoint: {CLIENT_ENDPOINT} ==="))
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] Target Scout agent: {SCOUT_AGENT_ADDRESS} ==="))
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] URL under test: {TEST_URL} ==="))

    request = ScoutRequest(url=TEST_URL)
    await ctx.send(SCOUT_AGENT_ADDRESS, request)

    ctx.logger.info(bold("=== [FETCH EVIDENCE] ScoutRequest sent. Waiting for response... ==="))

# ===============================================================
# 5) Response handler
# ===============================================================

@client.on_message(model=ScoutResponse)
async def handle_response(ctx: Context, sender: str, response: ScoutResponse):
    ctx.logger.info(bold(f"=== [FETCH EVIDENCE] ScoutResponse received from {sender} ==="))

    print("\n" + bold("================ [FETCH EVIDENCE] SCOUT RESPONSE ================"))
    print(bold(f"Job ID:     {response.job_id}"))
    print(bold(f"Status:     {response.status}"))
    print(bold(f"Scraped at: {response.scraped_at}"))
    print("--- Client Content ---")
    print(f"URL:      {response.client.url}")
    print(f"Title:    {response.client.title}")
    print(f"Meta:     {(response.client.meta or '')[:300]}...")
    print(f"Headings: {response.client.headings}")
    print("Top text (first 500 chars):")
    print((response.client.top_text or "")[:500])
    print(bold("==============================================================\n"))

    ctx.logger.info(bold("=== [FETCH EVIDENCE] One-shot test completed successfully ==="))
    ctx.logger.info(bold("=== [FETCH EVIDENCE] Client shutting down ==="))

    hard_exit_ok()

# ===============================================================
# 6) Run
# ===============================================================

if __name__ == "__main__":
    client.run()
