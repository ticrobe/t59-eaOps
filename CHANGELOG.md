# Changelog

All notable changes to eaOps are documented here. Versions follow `YY.M.patch`. Each release is tagged in git as `vYY.M.patch`, and `dist/` holds the latest build.

## [Unreleased]

### Added
- README, `CLAUDE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and issue and pull request templates.
- Per-Op YAML source in `content/`, and `tools/build_html.py` with a page template to generate `dist/eaOps.html` from it. The generated 26.9.1 page matches the finalized one.
- `tools/build_block_diagram.py`, which draws the block diagram (`dist/eaOps.png`) from `content/` and `VERSION`.
- `Makefile` with `make check` and `make preview`, which create the Python virtual environment and install the requirements on first use.
- Dual license: content under CC BY 4.0 (`LICENSE-CONTENT`), code under MIT (`LICENSE`).

## [26.9.1] - 2026-09-17

### Added
- Initial release of the eaOps document: 10 Ops, 42 Functions and 279 Parameters, each Parameter described for Azure, GCP, AWS and open source, grounded in the Customer, Products & Orders (CPO) use case.
- Block diagram of the 10 Ops around the Enterprise Architect.
