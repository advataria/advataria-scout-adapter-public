# AdvaScout uAgent (Advataria Scout Adapter – Public MVP)

AdvaScout uAgent is a Fetch.ai uAgent that transforms any website URL into a structured
"content pack" suitable for marketing, analytics, and autonomous creative pipelines.

This repository contains the minimal open-source adapter extracted from the Advataria project
and published under the MIT license as a reusable building block for the Fetch agent ecosystem.

---------------------------------------------------------------------

WHAT ADVASCOUT DOES

Input message:
{
  "url": "https://example.com"
}

The agent performs:
1. HTML fetch of the provided URL.
2. Extraction of key marketing-relevant signals:
   - <title>
   - meta description (including og:description / twitter:description)
   - H1–H3 headings (up to 10)
   - main body text condensed into top_text
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

5. Returns a compact ScoutResponse message to any calling agent.

---------------------------------------------------------------------

MESSAGE SCHEMAS (PYDANTIC)

Defined in adva_scout_models.py and reused on both server and client
to guarantee identical schema digest.

ScoutRequest:
    url: str (min_length=4)

ScoutResponseClient:
    url: str
    title: str
    meta: str
    headings: str
    top_text: str

ScoutResponse:
    job_id: str
    client: ScoutResponseClient
    scraped_at: str
    status: str
    error: Optional[str] = None

---------------------------------------------------------------------

ARCHITECTURE OVERVIEW

  adva_scout_test_client  ----ScoutRequest---->  adva_scout_uagent
  ^                                                           |
  |                                                           |
  ----------ScoutResponse--------------------------------------


adva_scout_uagent.py
- Listens for ScoutRequest
- Calls run_scout(job)
- Extracts webpage content
- Sends ScoutResponse
- Compatible with Fetch Agentverse Mailbox

02_scout_client_test.py
- Demo client uAgent
- Sends ScoutRequest
- Prints ScoutResponse

---------------------------------------------------------------------

REPOSITORY STRUCTURE

adva_scout_agent.py           – run_scout(job) → Content Pack
adva_scout_models.py          – shared Pydantic models
adva_scout_uagent.py          – Fetch.ai uAgent wrapper
p01_data_acquisition.py       – HTML fetch + BeautifulSoup extraction
02_scout_client_test.py       – optional test client
job_input.json                – example job payload
demo_*.adva_scout.json        – example Content Pack output
requirements.txt
LICENSE
README.md

---------------------------------------------------------------------

RUNNING LOCALLY

1. Install dependencies:

    pip install -r requirements.txt


2. Run the AdvaScout uAgent (server):

    python adva_scout_uagent.py

The agent will:
- start on http://127.0.0.1:8010/submit
- print its Fetch address
- connect to Agentverse Mailbox (if configured)


3. Run the test client:

    python 02_scout_client_test.py

The client will:
- send a ScoutRequest to AdvaScout
- print the returned ScoutResponse

You can verify both agents in Agentverse using the inspector links printed in logs.

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

You may configure the agent using environment variables:

export ADVA_SCOUT_AGENT_SEED="demo-seed-not-for-production-12345"
export ADVA_SCOUT_AGENT_PORT=8010
export ADVA_SCOUT_AGENT_ENDPOINT="http://127.0.0.1:8010/submit"

If not provided, the agent will automatically fall back to safe defaults.

---------------------------------------------------------------------

LICENSE

Released under the MIT License.
This adapter can be freely reused in any Fetch.ai or agentic project.

---------------------------------------------------------------------

CONTRIBUTIONS & FUTURE WORK

This public MVP is part of the Advataria project. Future work includes:

- AdvaCore orchestrator uAgent
- On-chain registration via Almanac contract
- DeltaV discoverability
- Integration with Brief and Story generation agents (private layer)

Feel free to open an issue or create a pull request.
