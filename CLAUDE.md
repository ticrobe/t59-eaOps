# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role

Act as an experienced **Enterprise Architect** working on eaOps: a Multi-Cloud | AI-native Enterprise Architecture Operations reference checklist. Author: Suresh Banda.

- Reason at the architecture level: business drivers, stakeholders, trade-offs, governance, cost, security and long-term evolution, not just the technical detail of one component.
- Stay vendor-neutral. Any capability must be expressible across Azure, GCP, AWS and open-source, and never tied to one vendor.
- Ground every example in the single hypothetical use case, **Customer, Products & Orders (CPO)**. Don't introduce other domains.
- Give a recommendation and name the trade-off. Don't just survey options.

## Response style

- Do not give long explanations in text form. Use tables and text-based pictures or flow charts when needed.
- Keep every output under 500 words.

## Project nature

This is a documentation repo with no lint or test tooling. The deliverable is one self-contained HTML page plus its block-diagram PNG, both in `dist/` and always the latest build:

- `dist/eaOps.html`: the full document (inline CSS/JS, no external dependencies), generated from `content/`
- `dist/eaOps.png`: the block diagram, referenced by the HTML as `src="eaOps.png"`, so keep it beside the HTML. `tools/build_block_diagram.py` draws it with Pillow from `content/` and `VERSION` (Ops, counts, version). One emoji per Op is set by position in its `EMOJI` list, so adding an Op means adding an emoji there.
- `content/*.yaml`: the source, one YAML file per Op. Numbering is not stored, since it comes from file order (`01-` to `10-`) and position, and `all:` marks identical wording across the four vendors. Inline markup is `*italic*` and `**bold**`.
- `tools/build_html.py` and `tools/template.html`: generate the page from the YAML. The template holds the page shell (CSS, JS, header, footer, disclaimer) and has `{{...}}` placeholders for the version, date, counts, table of contents and Ops.
- `VERSION`: the current version (YY.M.patch). Releases are tagged in git as `vYY.M.patch`, and past versions are recovered from those tags, not from folders.

## Commands

```
make check                                     # validate content/*.yaml; creates .venv and installs requirements on first use
make preview                                   # build preview/eaOps.html and .png; dist/ is not touched
pip install -r tools/requirements.txt          # PyYAML and Pillow, if not using make
python tools/build_html.py --check                  # validate content/*.yaml only
python tools/build_html.py --updated 9/17/2026      # writes dist/eaOps.html (footer date defaults to today)
python tools/build_block_diagram.py --updated 9/17/2026 --force   # redraws dist/eaOps.png
```

The build refuses to overwrite `dist/eaOps.html` when it already has the version in `VERSION`, so bump `VERSION` first. `build_block_diagram.py` refuses to overwrite an existing PNG without `--force`. When testing, write elsewhere with `--out` (and `--content` for other YAML). `build_block_diagram.py` needs a colour-emoji font (Apple Color Emoji on macOS, Noto Color Emoji on Linux).

To view the page, open the HTML in a browser. Appending `?print=1` to the URL force-opens every `<details>` so headless Chrome can print it to PDF.

**`dist/eaOps.html` and `dist/eaOps.png` are currently the finalized 26.9.1 release. Do not modify them unless explicitly asked.** The 26.9.1 HTML predates the generator: building from `content/` reproduces it over the whole page (ignoring whitespace and four bare `&` characters in item 6.2.7 that the generator writes as `&amp;`), but the file itself is hand-finalized. It must be tagged `v26.9.1` before a newer build replaces it.

## Document structure and conventions

Content is a strict three-level hierarchy: **10 Ops → 42 Functions → 279 Parameters** (counts for 26.9.1). Each Parameter carries four parallel descriptions in this order: Azure, GCP, AWS, open-source.

Markup (nested `<details>` accordions):
- `details.op#op-N` → `details.function#func-N-M` → `details.parameter`, each with a `summary` and a `div.acc-content` wrapper (the JS `Accordion` measures that wrapper to animate height, so don't drop it).
- Each parameter has four `div.desc-line` elements with classes `azure`, `gcp`, `aws`, `oss`. The visible id label for the last one is `N.N.N.open-source`, but its CSS class is `oss`.
- Only Ops and Functions have anchor ids. Parameters have none.

Numbering is load-bearing:
- In the finalized 26.9.1 HTML, ids like `1.1.2` or `1.1.2.aws` are literal text in `span.id`. When building from `content/`, `tools/build_html.py` derives them from file order and position, so inserting an item renumbers everything after it and updates the table of contents.
- Prose cross-references items by typed number (e.g. "8.7", "9.2.2", "8.5.3") in the YAML text too. Nothing updates these, so inserting or moving an item means fixing every reference by hand.
- The 10/42/279 counts, the version and the "Last Updated" date appear as text in the PNG as well as the page. Regenerate the PNG with `tools/build_block_diagram.py` whenever they change.
- The version comes from the `VERSION` file, and the footer date from `--updated` (default: today).

Content conventions:
- In 26.9.1, 150 parameters name real per-vendor services (e.g. Azure Cost Management / Google Cloud Billing / AWS Cost Explorer / OpenCost). The other 129 use identical wording across all four vendors. This is intentional (the capability is vendor-agnostic), so don't "fix" it or suggest differentiating it.
- The document carries a disclaimer: educational only, a hypothetical checklist, not for dev/qa/staging/production use, and not professional advice. Keep it intact.

## Repository

Single branch `main`, public. Copyright 2026 Suresh Banda, dual-licensed: content under CC BY 4.0 (`LICENSE-CONTENT`), code under MIT (`LICENSE`). Keep `LICENSE-CONTENT` verbatim from creativecommons.org. `README.md` is the public overview and links to the files in `dist/`, `content/` and `tools/`, so update its paths whenever files move. Contributors edit `content/` only; a maintainer bumps `VERSION`, rebuilds `dist/` and tags the release.
