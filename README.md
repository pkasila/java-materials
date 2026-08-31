# Java Materials — LaTeX Presentations

Beamer presentations for teaching materials, built with a shared **Academic** theme and published to GitHub Pages as PDFs with a browsable index.

## Quick start

```bash
# Copy the template
cp -R lectures/_template lectures/02-my-topic

# Edit meta.yaml (set build: true), main.tex, and slides/*
make lecture DIR=lectures/02-my-topic

# Build all publishable decks and generate the site index
make
```

Requires TeX Live with Cyrillic support for Russian decks (`texlive-lang-cyrillic`), or rely on CI.

## Repository layout

| Path | Purpose |
| ---- | ------- |
| [`latex/tex/latex/`](latex/tex/latex/) | Beamer theme (`.sty`) and `academicbeamer` package |
| [`lectures/[NN]-name/`](lectures/) | One folder per presentation |
| [`scripts/`](scripts/) | Build and site-generation scripts |
| [`_site/`](_site/) | Generated site (gitignored) |

See [`lectures/README.md`](lectures/README.md) for naming, `meta.yaml`, and slide modularisation.

## Theme usage

```latex
\documentclass[aspectratio=169,11pt,t]{beamer}
\usepackage[english]{academicbeamer}
\setshorttitle{Java \textbar\ Lecture 3}

\title{...}
\begin{document}
\input{slides/01-title}
\end{document}
```

Use `\usepackage[russian]{academicbeamer}` for Cyrillic content. Helper macros: `\lead{}`, `\tbd{}`, `\photoframe{}{}{}`, `\orient`.

Images: place files in `assets/` and add `\graphicspath{{assets/}}` in `main.tex`.

## Make targets

| Target | Description |
| ------ | ----------- |
| `make` / `make all` | Build all decks + generate `_site/index.html` |
| `make lecture DIR=lectures/01-java-intro` | Build one deck |
| `make site` | Same as `make all` |
| `make clean` | Remove aux files, PDFs, and `_site/` |

## GitHub Pages

1. Push to GitHub.
2. Enable **Settings → Pages → Source: GitHub Actions**.
3. On push to `main`, [`.github/workflows/presentations.yml`](.github/workflows/presentations.yml) builds PDFs, thumbnails, and deploys `_site/`.

Published URL: `https://<user>.github.io/java-materials/`

## Example decks

- [`lectures/00-ai-olympiad-example/`](lectures/00-ai-olympiad-example/) — full Russian reference deck
- [`lectures/01-java-intro/`](lectures/01-java-intro/) — short English Java intro
- [`lectures/_template/`](lectures/_template/) — copy-paste scaffold (not built by CI)
