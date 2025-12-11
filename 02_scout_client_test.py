#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
02_scout_client_test.py
-----------------------

Klientsky uAgent, ktorý:
1. sa pripojí cez mailbox
2. pošle ScoutRequest tvojmu AdvaScout uAgentovi
3. počká na ScoutResponse a vypíše ho

Funguje aj na Windows (SelectorEventLoop fix).
"""

import os
import asyncio
from uagents import Agent, Context

# SPOLOČNÉ MODELY – rovnaké ako na serveri
from adva_scout_models import ScoutRequest, ScoutResponse

# ===============================================================
# 0) Windows fix – aiodns potrebuje SelectorEventLoop
# ===============================================================

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ===============================================================
# 1. ADRESA SCOUT AGENTA – z logu servera
# ===============================================================

SCOUT_AGENT_ADDRESS = "agent1qgvjuxzkjcqc04nxedtdn525cw623y59xgy9ftnmzd3ha2mermh72qqw5pl"

# ===============================================================
# 2. DEFINÍCIA KLIENTA
# ===============================================================

client = Agent(
    name="adva_scout_test_client",
    seed="advataria scout client seed DO NOT USE IN PROD",
    mailbox=True,              # nech vie prijať odpoveď
    publish_agent_details=False,
)

# ===============================================================
# 3. PRI ŠTARTE: pošli ScoutRequest
# ===============================================================

@client.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Test client starting, sending ScoutRequest...")

    req = ScoutRequest(url="https://fetch.ai")
    await ctx.send(SCOUT_AGENT_ADDRESS, req)
    ctx.logger.info(f"ScoutRequest sent to {SCOUT_AGENT_ADDRESS}")

# ===============================================================
# 4. HANDLER NA ODPOVEĎ
# ===============================================================

@client.on_message(model=ScoutResponse)
async def handle_response(ctx: Context, sender: str, response: ScoutResponse):
    ctx.logger.info(f"Received response from {sender}")

    print("\n\n================ SCOUT RESPONSE ================")
    print(f"Job ID:     {response.job_id}")
    print(f"Status:     {response.status}")
    print(f"Scraped at: {response.scraped_at}")
    print("--- Client Content ---")
    print(f"URL:   {response.client.url}")
    print(f"Title: {response.client.title}")
    print(f"Meta:  {response.client.meta[:300]}...")
    print(f"Headings: {response.client.headings}")
    print("Top text (first 500 chars):")
    print(response.client.top_text[:500])
    print("=================================================\n")

    ctx.logger.info("Test complete. Stopping client.")
    await ctx.stop()

# ===============================================================
# 5. SPUSTENIE
# ===============================================================

if __name__ == "__main__":
    client.run()
