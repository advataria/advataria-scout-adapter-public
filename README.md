# AdvaScout uAgent (Advataria Scout Adapter – Public MVP)

AdvaScout is a Fetch.ai uAgent that transforms a website URL into a structured
Content Pack JSON for marketing analysis and autonomous creative pipelines.

This repository contains a minimal open-source adapter extracted from the
Advataria project and released under the MIT License as a reusable building
block for the Fetch agent ecosystem.

---------------------------------------------------------------------

WHY THIS REPOSITORY EXISTS (FOR FETCH REVIEWERS)

This demo is intentionally small and focused:

- Real uAgent runtime (not mocked)
- Deterministic JSON message contracts
- Inspectable message flow via Agentverse Inspector
- Reusable “Scout” building block for agent-to-agent pipelines

---------------------------------------------------------------------

WHAT ADVASCOUT DOES

INPUT MESSAGE (ScoutRequest)

{
  "url": "https://example.com"
}

THE AGENT PERFORMS

1. Fetches the HTML of the provided URL.
2. Extracts marketing-relevant signals:
   - <title>
   - meta description (including og:description / twitter:description)
   - H1–H3 headings (up to 10)
   - main body condensed into top_text
3. Builds a structured Content Pack JSON:

{
  "job_id": "demo-...",
  "status": "success",
  "client": {
    "url": "...",
    "title": "...",
    "meta": "...",
    "headings": "...",
    "top_text": "..."
  },
  "competitors": [],
  "uploaded_docs": [],
  "client_inputs": {},
  "meta": {
    "scraped_at": "...",
    "agent": "AdvaScout AI Agent",
    "agent_version": "0.8.0"
  }
}

4. Optionally saves the full Content Pack to:
   out_basic/<job_id>.adva_scout.json

5. Returns a compact ScoutResponse message to the calling agent or client.

---------------------------------------------------------------------

ARCHITECTURE OVERVIEW

High-level message flow between the demo client and the uAgent:

---------------------------------------------------------------
Client (02_scout_client_test.py)  ---- ScoutRequest ---->  Server (01_adva_uagent_scout.py)
Client (02_scout_client_test.py)  <--- ScoutResponse <---  Server (01_adva_uagent_scout.py)
---------------------------------------------------------------

COMPONENTS

01_adva_uagent_scout.py
- Listens for incoming ScoutRequest
- Calls run_scout(job)
- Extracts webpage content
- Sends ScoutResponse
- Compatible with Fetch Agentverse Mailbox

02_scout_client_test.py
- Simple demo client
- Sends a ScoutRequest to the running uAgent
- Prints the returned ScoutResponse

---------------------------------------------------------------------

LIVE INSPECTION (AGENTVERSE INSPECTOR)

When running, both the server and client print an Inspector link in logs.

Using Agentverse Inspector you can:
- Inspect the received ScoutRequest message and its JSON payload
- Inspect the sent ScoutResponse message and its JSON payload

These JSON payloads are machine-readable contracts intended for reuse by
downstream agents (Scout → Brief → Story → …).

---------------------------------------------------------------------

MESSAGE SCHEMAS (PYDANTIC)

Defined in adva_scout_models.py and reused on both server and client.

ScoutRequest
- url: str (min_length=4)

ScoutResponseClient
- url: str
- title: str
- meta: str
- headings: str
- top_text: str

ScoutResponse
- job_id: str
- client: ScoutResponseClient
- scraped_at: str
- status: str
- error: Optional[str]

---------------------------------------------------------------------

REPOSITORY STRUCTURE

adva_scout_agent.py        – run_scout(job) → Content Pack
adva_scout_models.py      – shared Pydantic models
adva_scout_uagent.py      – Fetch.ai uAgent wrapper
p01_data_acquisition.py   – HTML fetch + BeautifulSoup extraction
02_scout_client_test.py   – optional test client
job_input.json            – example job payload
scout_request.json        – ScoutRequest contract example
scout_response.json       – ScoutResponse contract example
requirements.txt
DISCLAIMER.md
LICENSE
README.md

---------------------------------------------------------------------

RUNNING LOCALLY

1) Install dependencies

pip install -r requirements.txt

2) Run the AdvaScout uAgent (server)

python 01_adva_uagent_scout.py

The agent will:
- start on http://127.0.0.1:8010/submit
- print its Fetch agent address
- connect to Agentverse Mailbox (if configured)
- print Inspector links in logs

3) Run the test client

python 02_scout_client_test.py

The client will:
- send a ScoutRequest to AdvaScout
- print the ScoutResponse

---------------------------------------------------------------------

EXAMPLE OUTPUT (SCOUTRESPONSE)

{
  "job_id": "scout-1765452055",
  "status": "success",
  "scraped_at": "2025-12-11T10:05:44Z",
  "client": {
    "url": "https://pekneprezky.sk",
    "title": "Pekné prežky",
    "meta": "...",
    "headings": "...",
    "top_text": "..."
  },
  "error": null
}

---------------------------------------------------------------------

ENVIRONMENT VARIABLES (OPTIONAL)

ADVA_SCOUT_AGENT_SEED="demo-seed-not-for-production-12345"
ADVA_SCOUT_AGENT_PORT=8010
ADVA_SCOUT_AGENT_ENDPOINT="http://127.0.0.1:8010/submit"

If not provided, the agent falls back to safe defaults.

---------------------------------------------------------------------

LICENSE

Released under the MIT License.
This adapter can be freely reused in Fetch.ai and agentic projects.

---------------------------------------------------------------------

CONTRIBUTIONS & ROADMAP NOTES

This public MVP is part of the Advataria project.

Potential future extensions:
- AdvaCore orchestrator uAgent
- On-chain registration via Almanac contract
- DeltaV discoverability
- Integration with Brief and Story agents (private layer)

Pull requests and issues are welcome.
