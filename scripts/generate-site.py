#!/usr/bin/env python3
"""Generate GitHub Pages index from lecture meta.yaml files and built PDFs."""

from __future__ import annotations

import html
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = REPO_ROOT / "lectures"
SITE_DIR = REPO_ROOT / "_site"

SITE = {
    "lang": "ru",
    "title": "Учебные материалы — Java",
    "tagline": "Презентации к лекциям курса. Собраны из LaTeX Beamer и публикуются в PDF.",
    "download": "Скачать PDF",
    "updated": "Обновлено",
    "lecture_label": "Лекция",
    "empty": "Пока нет опубликованных презентаций.",
    "count_one": "{} лекция",
    "count_few": "{} лекции",
    "count_many": "{} лекций",
}

MONTHS_RU = (
    "",
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)


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


def lecture_number(slug: str) -> str:
    match = re.match(r"^(\d+)", slug)
    return match.group(1).lstrip("0") or match.group(1) if match else ""


def format_date_ru(iso_date: str) -> str:
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", iso_date.strip())
    if not match:
        return iso_date
    year, month, day = match.groups()
    month_idx = int(month)
    if not 1 <= month_idx <= 12:
        return iso_date
    return f"{int(day)} {MONTHS_RU[month_idx]} {year}"


def plural_lectures(count: int) -> str:
    n = abs(count) % 100
    n1 = n % 10
    if 11 <= n <= 19:
        return SITE["count_many"].format(count)
    if n1 == 1:
        return SITE["count_one"].format(count)
    if 2 <= n1 <= 4:
        return SITE["count_few"].format(count)
    return SITE["count_many"].format(count)


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
                "number": lecture_number(slug),
                "title": meta.get("title", slug),
                "subtitle": meta.get("subtitle", ""),
                "date": meta.get("date", ""),
                "date_display": format_date_ru(meta.get("date", "")),
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
    date_display = html.escape(entry["date_display"])
    description = html.escape(entry["description"])
    pdf = html.escape(entry["pdf"])
    lecture_no = html.escape(entry["number"])
    thumb_alt = html.escape(f"{SITE['lecture_label']} {entry['number']}: {entry['title']}")

    thumb_html = ""
    if entry["thumb"]:
        thumb = html.escape(entry["thumb"])
        thumb_html = f'<img class="card-thumb" src="{thumb}" alt="{thumb_alt}">'

    badge_html = ""
    if lecture_no:
        badge_html = f'<span class="card-badge">{SITE["lecture_label"]} {lecture_no}</span>'

    subtitle_html = f'<p class="card-subtitle">{subtitle}</p>' if subtitle else ""
    desc_html = f'<p class="card-desc">{description}</p>' if description else ""

    return f"""
    <article class="card">
      <a class="card-link" href="{pdf}">
        {thumb_html}
        <div class="card-body">
          {badge_html}
          <h2 class="card-title">{title}</h2>
          {subtitle_html}
          {desc_html}
          <p class="card-meta"><span class="card-date-label">{SITE["updated"]}:</span> {date_display}</p>
          <span class="card-action">{SITE["download"]}</span>
        </div>
      </a>
    </article>"""


def render_index(entries: list[dict]) -> str:
    cards = "\n".join(render_card(e) for e in entries)
    if not cards.strip():
        cards = f'<p class="empty">{SITE["empty"]}</p>'

    count_html = ""
    if entries:
        count_html = f'<p class="site-count">{html.escape(plural_lectures(len(entries)))}</p>'

    return f"""<!DOCTYPE html>
<html lang="{SITE["lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(SITE["title"])}</title>
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
      font-family: system-ui, -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      background: var(--ac-light);
      color: #222;
      line-height: 1.55;
    }}
    header {{
      background: #fff;
      border-bottom: 1px solid var(--ac-rule);
      padding: 2rem 1.5rem;
    }}
    .header-inner {{
      max-width: 1100px;
      margin: 0 auto;
    }}
    header h1 {{
      margin: 0;
      color: var(--ac-dark);
      font-size: 1.85rem;
      font-weight: 700;
    }}
    header p {{
      margin: 0.55rem 0 0;
      color: var(--ac-gray);
      max-width: 42rem;
    }}
    .site-count {{
      margin: 0.75rem 0 0;
      font-size: 0.9rem;
      color: var(--ac-mid);
      font-weight: 600;
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 2rem 1.5rem 3rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }}
    .card {{
      background: #fff;
      border: 1px solid var(--ac-rule);
      border-radius: 8px;
      overflow: hidden;
      transition: box-shadow 0.15s ease, transform 0.15s ease;
    }}
    .card:hover {{
      box-shadow: 0 6px 20px rgba(23, 42, 74, 0.12);
      transform: translateY(-1px);
    }}
    .card-link {{
      display: block;
      color: inherit;
      text-decoration: none;
      height: 100%;
    }}
    .card-thumb {{
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
      display: block;
      background: var(--ac-light);
      border-bottom: 1px solid var(--ac-rule);
    }}
    .card-body {{ padding: 1rem 1.15rem 1.25rem; }}
    .card-badge {{
      display: inline-block;
      margin-bottom: 0.45rem;
      padding: 0.15rem 0.55rem;
      border-radius: 999px;
      background: var(--ac-light);
      color: var(--ac-mid);
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    .card-title {{
      margin: 0;
      font-size: 1.15rem;
      color: var(--ac-dark);
      line-height: 1.3;
    }}
    .card-subtitle {{
      margin: 0.4rem 0 0;
      font-size: 0.92rem;
      color: var(--ac-mid);
    }}
    .card-desc {{
      margin: 0.65rem 0 0;
      font-size: 0.9rem;
      color: #3a3a3a;
    }}
    .card-meta {{
      margin: 0.75rem 0 0;
      font-size: 0.8rem;
      color: var(--ac-gray);
    }}
    .card-date-label {{
      color: var(--ac-gray);
    }}
    .card-action {{
      display: inline-block;
      margin-top: 0.85rem;
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--ac-mid);
    }}
    .empty {{ color: var(--ac-gray); }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <h1>{html.escape(SITE["title"])}</h1>
      <p>{html.escape(SITE["tagline"])}</p>
      {count_html}
    </div>
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
