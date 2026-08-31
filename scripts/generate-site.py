#!/usr/bin/env python3
"""Generate GitHub Pages index from lecture meta.yaml files and built PDFs."""

from __future__ import annotations

import html
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = REPO_ROOT / "lectures"
SITE_DIR = REPO_ROOT / "_site"


def parse_meta(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_]+):\s*(.+)$", line)
        if not match:
            continue
        key, raw = match.group(1), match.group(2).strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        elif raw.startswith("'") and raw.endswith("'"):
            raw = raw[1:-1]
        data[key] = raw
    return data


def lecture_sort_key(slug: str) -> tuple:
    match = re.match(r"^(\d+)", slug)
    num = int(match.group(1)) if match else 9999
    return (num, slug)


def discover_lectures() -> list[dict]:
    entries: list[dict] = []
    for lecture_dir in sorted(LECTURES_DIR.iterdir()):
        if not lecture_dir.is_dir():
            continue
        slug = lecture_dir.name
        if slug.startswith("_"):
            continue
        meta_path = lecture_dir / "meta.yaml"
        if not meta_path.exists():
            continue
        meta = parse_meta(meta_path)
        if meta.get("build", "true").lower() == "false":
            continue
        if meta.get("hidden", "false").lower() == "true":
            continue
        pdf = SITE_DIR / "pdfs" / f"{slug}.pdf"
        if not pdf.exists():
            continue
        thumb = SITE_DIR / "thumbs" / f"{slug}.png"
        entries.append(
            {
                "slug": slug,
                "title": meta.get("title", slug),
                "subtitle": meta.get("subtitle", ""),
                "date": meta.get("date", ""),
                "description": meta.get("description", ""),
                "pdf": f"pdfs/{slug}.pdf",
                "thumb": f"thumbs/{slug}.png" if thumb.exists() else "",
            }
        )
    entries.sort(key=lambda e: lecture_sort_key(e["slug"]))
    return entries


def render_card(entry: dict) -> str:
    title = html.escape(entry["title"])
    subtitle = html.escape(entry["subtitle"])
    date = html.escape(entry["date"])
    description = html.escape(entry["description"])
    pdf = html.escape(entry["pdf"])

    thumb_html = ""
    if entry["thumb"]:
        thumb = html.escape(entry["thumb"])
        thumb_html = f'<img class="card-thumb" src="{thumb}" alt="">'

    subtitle_html = f'<p class="card-subtitle">{subtitle}</p>' if subtitle else ""
    desc_html = f'<p class="card-desc">{description}</p>' if description else ""

    return f"""
    <article class="card">
      <a class="card-link" href="{pdf}">
        {thumb_html}
        <div class="card-body">
          <h2 class="card-title">{title}</h2>
          {subtitle_html}
          <p class="card-date">{date}</p>
          {desc_html}
          <span class="card-action">Download PDF</span>
        </div>
      </a>
    </article>"""


def render_index(entries: list[dict]) -> str:
    cards = "\n".join(render_card(e) for e in entries)
    if not cards.strip():
        cards = '<p class="empty">No presentations built yet.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Presentations</title>
  <style>
    :root {{
      --ac-dark: #172a4a;
      --ac-mid: #3e547a;
      --ac-gray: #6c737c;
      --ac-light: #eff1f4;
      --ac-rule: #c6cbd2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      background: var(--ac-light);
      color: #222;
      line-height: 1.5;
    }}
    header {{
      background: #fff;
      border-bottom: 1px solid var(--ac-rule);
      padding: 2rem 1.5rem;
    }}
    header h1 {{
      margin: 0;
      color: var(--ac-dark);
      font-size: 1.75rem;
    }}
    header p {{
      margin: 0.5rem 0 0;
      color: var(--ac-gray);
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 2rem 1.5rem 3rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.5rem;
    }}
    .card {{
      background: #fff;
      border: 1px solid var(--ac-rule);
      border-radius: 6px;
      overflow: hidden;
      transition: box-shadow 0.15s ease;
    }}
    .card:hover {{ box-shadow: 0 4px 16px rgba(23, 42, 74, 0.12); }}
    .card-link {{
      display: block;
      color: inherit;
      text-decoration: none;
    }}
    .card-thumb {{
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
      display: block;
      background: var(--ac-light);
      border-bottom: 1px solid var(--ac-rule);
    }}
    .card-body {{ padding: 1rem 1.1rem 1.2rem; }}
    .card-title {{
      margin: 0;
      font-size: 1.1rem;
      color: var(--ac-dark);
    }}
    .card-subtitle {{
      margin: 0.35rem 0 0;
      font-size: 0.9rem;
      color: var(--ac-mid);
    }}
    .card-date {{
      margin: 0.5rem 0 0;
      font-size: 0.8rem;
      color: var(--ac-gray);
    }}
    .card-desc {{
      margin: 0.6rem 0 0;
      font-size: 0.875rem;
      color: #444;
    }}
    .card-action {{
      display: inline-block;
      margin-top: 0.75rem;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--ac-mid);
    }}
    .empty {{ color: var(--ac-gray); }}
  </style>
</head>
<body>
  <header>
    <h1>Presentations</h1>
    <p>LaTeX Beamer decks built from this repository.</p>
  </header>
  <main>
    <div class="grid">
      {cards}
    </div>
  </main>
</body>
</html>
"""


def main() -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    entries = discover_lectures()
    index_path = SITE_DIR / "index.html"
    index_path.write_text(render_index(entries), encoding="utf-8")
    print(f"Wrote {index_path} ({len(entries)} presentation(s))")


if __name__ == "__main__":
    main()
