# AdvaScout uAgent (Advataria Scout Adapter – Public MVP)

AdvaScout uAgent is a **Fetch.ai uAgent** that transforms any website URL into a structured
"content pack" suitable for marketing, analytics, and autonomous creative pipelines.

This repository contains the **minimal open‑source adapter** extracted from the Advataria project
and published under the MIT license as a reusable building block for the Fetch agent ecosystem.

---

## What AdvaScout Does

Input message:

```json
{
  "url": "https://example.com"
}
```

The agent performs:

1. **HTML fetch** of the provided URL.
2. **Extraction** of key marketing‑relevant signals:

   * `<title>`
   * meta description (including `og:description` / `twitter:description`)
   * H1–H3 headings (up to 10)
   * main body text condensed into `top_text`
3. Builds a structured **Content Pack JSON**:

```json
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
```

4. Optional: saves the raw Content Pack to `out_basic/<job_id>.adva_scout.json`.
5. Returns a compact `ScoutResponse` message to any calling agent.

---

## 📡 Message Schemas (Pydantic)

Defined in `adva_scout_models.py` and reused on both server and client to guarantee identical schema digest.

```python
class ScoutRequest(BaseModel):
    url: str = Field(
        ...,
        description="Client website URL to analyze, e.g. https://example.com",
        min_length=4,
    )

class ScoutResponseClient(BaseModel):
    url: str
    title: str
    meta: str
    headings: str
    top_text: str

class ScoutResponse(BaseModel):
    job_id: str
    client: ScoutResponseClient
    scraped_at: str
    status: str
    error: Optional[str] = None
```

---

## 🧠 Architecture Overview

```
┌─────────────────────────┐        ScoutRequest       ┌─────────────────────────┐
│  adva_scout_test_client │ ───────────────────────▶ │    adva_scout_uagent    │
└─────────────────────────┘                           │  (Fetch.ai uAgent)      │
        ▲                                             └───────────┬─────────────┘
        │                          ScoutResponse                 │
        └────────────────────────────────────────────────────────┘
```

**adva_scout_uagent.py**

* Listens for `ScoutRequest`
* Calls internal `run_scout(job)` (from `adva_scout_agent.py`)
* Extracts page content
* Sends back `ScoutResponse`
* Is compatible with Fetch Agentverse Mailbox

**adva_scout_test_client.py**

* Simple demo client uAgent
* Sends test `ScoutRequest`
* Prints `ScoutResponse`

---

## 📁 Repository Structure

```
.
├── adva_scout_agent.py           # run_scout(job) → Content Pack
├── adva_scout_models.py          # shared Pydantic models
├── adva_scout_uagent.py          # main uAgent wrapper
├── p01_data_acquisition.py       # HTML fetch + BeautifulSoup extraction
├── 02_scout_client_test.py       # optional local demo client
├── job_input.json                # example job payload (optional)
├── demo_scout_output.json        # example Content Pack output (optional)
├── requirements.txt
├── LICENSE                       # MIT
└── README.md
```

---

## 🏃 Running Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the AdvaScout uAgent (server)

```bash
python adva_scout_uagent.py
```

The agent will:

* start on `http://127.0.0.1:8010/submit`
* print its Fetch address
* connect to Agentverse Mailbox (if configured)

### 3. Run the test client (optional)

```bash
python 02_scout_client_test.py
```

The client will:

* send a `ScoutRequest` to AdvaScout
* print the returned `ScoutResponse`

You can verify both agents in Agentverse using the inspector links printed in logs.

---

## 🌐 Example Output (return message)

```json
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
```

---

## 🔧 Environment Variables

These variables are optional but recommended for secure configuration.

# Agent seed (test only — replace in production)
export ADVA_SCOUT_AGENT_SEED="demo-seed-not-for-production-12345"

# Network settings
export ADVA_SCOUT_AGENT_PORT=8010
export ADVA_SCOUT_AGENT_ENDPOINT="http://127.0.0.1:8010/submit"


The agent will automatically fall back to safe defaults if these variables are not provided.

## 📜 License

Released under the **MIT License**. See `LICENSE` for full text.

This adapter can be freely reused in any Fetch.ai or agentic project.

---

## 🤝 Contributions & Future Work

This public MVP is part of the Advataria project. Future work includes:

* AdvaCore orchestrator uAgent
* On‑chain registration via Almanac contract
* DeltaV discoverability
* Integration with Brief and Story generation agents (private layer)

For any questions feel free to reach out or open an issue.
