import re, html, sys, json, pathlib
import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (X11; Linux x86_64)"

def nacitaj_html(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    return r.text

def extrahuj_texty(html_str: str) -> dict:
    soup = BeautifulSoup(html_str, "html.parser")

    # odstráň neviditeľné časti
    for t in soup(["script","style","noscript","iframe","template"]):
        t.decompose()

    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""

    meta = ""
    for m in soup.find_all("meta"):
        name = (m.get("name") or "").lower()
        prop = (m.get("property") or "").lower()
        if name == "description" or prop in {"og:description","twitter:description"}:
            meta += " " + m.get("content", "")

    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1","h2","h3"])[:10]]
    headings_join = " | ".join(headings)

    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) >= 40]
    top_paras = " ".join(paras[:8])  # viac odsekov ako predtým
    top_paras = html.unescape(re.sub(r"\s+", " ", top_paras)).strip()

    return {
        "title": title,
        "meta": meta.strip(),
        "headings": headings_join,
        "top_text": top_paras
    }

def uloz_vystup(url: str, html_str: str, data: dict):
    outdir = pathlib.Path("out_basic")
    outdir.mkdir(exist_ok=True)

    safe = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_")
    (outdir / f"{safe}.html").write_text(html_str, encoding="utf-8")
    (outdir / f"{safe}.txt").write_text(
        f"{data['title']}\n{data['meta']}\n{data['headings']}\n{data['top_text']}",
        encoding="utf-8"
    )
    (outdir / f"{safe}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Súbory uložené do priečinka out_basic ako {safe}.*")

def run(url: str):
    html_raw = nacitaj_html(url)
    data = extrahuj_texty(html_raw)
    uloz_vystup(url, html_raw, data)

    print("\n=== URL ===")
    print(url)
    print("\n=== TITLE ===")
    print(data["title"] or "-")
    print("\n=== META ===")
    print(data["meta"] or "-")
    print("\n=== H1–H3 ===")
    print(data["headings"] or "-")
    print("\n=== TOP TEXT (náhľad 3000 znakov) ===")
    text = data["top_text"]
    print(text[:3000] + ("..." if len(text) > 3000 else ""))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Použitie: python scrape_basic.py <URL>")
        sys.exit(1)
    run(sys.argv[1])
