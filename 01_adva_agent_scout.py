# adva_scout_agent.py
"""
AdvaScout AI Agent (Data Acquisition)
-------------------------------------

Úloha:
- Zoberie client_url, competitor_urls, uploaded_docs a client_form
- Zo stránok klienta a konkurencie spraví štruktúrovaný výstup
- Dokumenty spracuje zatiaľ ako STUB
- Výsledok uloží ako jeden JSON "Content Pack" pre AdvaBrief

Použitie z CLI:
    python adva_scout_agent.py job_input.json

Format job_input.json:
{
  "job_id": "scout-2025-000123",
  "client_url": "https://client-website.com",
  "competitor_urls": [
    "https://competitor1.com",
    "https://competitor2.com"
  ],
  "uploaded_docs": [
    {
      "doc_id": "doc-001",
      "filename": "brand_book.pdf",
      "mime_type": "application/pdf"
    }
  ],
  "client_form": {
    "goals": ["increase bookings"],
    "kpi": ["bookings", "conversion_rate"],
    "brand_tone": "friendly, expert, human",
    "notes": "We want to look modern but trustworthy."
  }
}

Výstup:
- out_basic/<safe_job_id>.adva_scout.json
"""

import json
import pathlib
import re
import sys
from datetime import datetime
from typing import Any, Dict, List

from p01_data_acquisition import nacitaj_html, extrahuj_texty

OUT_DIR = pathlib.Path("out_basic")


def _safe_id(value: str) -> str:
    """Bezpečný identifikátor pre názvy súborov."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_") or "job"


def process_url(url: str) -> Dict[str, Any]:
    """
    Stiahne stránku, extrahuje texty pomocou existujúceho scrape_basic2
    a vráti štruktúrovaný dict pripravený pre AdvaBrief.
    """
    html_raw = nacitaj_html(url)
    data = extrahuj_texty(html_raw)

    # Môžeš doplniť aj cestu k TXT/JSON, ak ich chceš používať ďalej
    return {
        "url": url,
        "title": data.get("title") or "",
        "meta": data.get("meta") or "",
        "headings": data.get("headings") or "",
        "top_text": data.get("top_text") or "",
    }


def process_competitors(urls: List[str]) -> List[Dict[str, Any]]:
    """Spracuje zoznam konkurentov. Aktuálne robí plný scrape, ale kľudne
    môžeš začať aj ako placeholder."""
    competitors: List[Dict[str, Any]] = []
    for url in urls:
        try:
            competitors.append(process_url(url))
        except Exception as e:
            competitors.append(
                {
                    "url": url,
                    "title": "",
                    "meta": "",
                    "headings": "",
                    "top_text": "",
                    "error": f"Failed to process competitor: {e}",
                }
            )
    return competitors


def process_uploaded_documents(uploaded_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Stub pre nahrané dokumenty.

    Teraz:
    - nezískava obsah,
    - len zaznamená, že dokument existuje a je pripravený na spracovanie.

    Neskôr (Phase 2):
    - sem pridáme PDF/DOCX/PPTX parsing (Textract, Document AI atď.).
    """
    docs_out: List[Dict[str, Any]] = []
    for d in uploaded_docs:
        docs_out.append(
            {
                "doc_id": d.get("doc_id"),
                "filename": d.get("filename"),
                "mime_type": d.get("mime_type"),
                "status": "stub_only",
                "text": "",
                "notes": "Full parsing (PDF/DOCX/PPTX) will be implemented in Phase 2 with Fetch grant.",
            }
        )
    return docs_out


def run_scout(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hlavná funkcia AdvaScout agenta.

    Vstup: job dict (client_url, competitor_urls, uploaded_docs, client_form)
    Výstup: jeden JSON payload pre AdvaBrief + uloženie do out_basic/
    """
    OUT_DIR.mkdir(exist_ok=True)

    job_id = job.get("job_id") or f"scout-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    client_url = job["client_url"]
    competitor_urls = job.get("competitor_urls", []) or []
    uploaded_docs = job.get("uploaded_docs", []) or []
    client_form = job.get("client_form", {}) or {}

    # 1) klient
    client_data = process_url(client_url)

    # 2) konkurencia
    competitors_data = process_competitors(competitor_urls)

    # 3) dokumenty (stub)
    docs_data = process_uploaded_documents(uploaded_docs)

    # 4) result payload
    result: Dict[str, Any] = {
        "job_id": job_id,
        "status": "success",
        "client": client_data,
        "competitors": competitors_data,
        "uploaded_docs": docs_data,
        "client_inputs": client_form,
        "meta": {
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "agent": "AdvaScout AI Agent",
            "agent_version": "0.8.0",
        },
    }

    safe_job_id = _safe_id(job_id)
    out_path = OUT_DIR / f"{safe_job_id}.adva_scout.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[AdvaScout] Job {job_id} completed.")
    print(f"[AdvaScout] JSON uložený do: {out_path}")

    return result


def main() -> None:
    if len(sys.argv) != 2:
        print("Použitie: python adva_scout_agent.py job_input.json")
        sys.exit(1)

    job_path = pathlib.Path(sys.argv[1])
    if not job_path.exists():
        print(f"Job input file neexistuje: {job_path}")
        sys.exit(1)

    job_data = json.loads(job_path.read_text(encoding="utf-8"))
    run_scout(job_data)


if __name__ == "__main__":
    main()
