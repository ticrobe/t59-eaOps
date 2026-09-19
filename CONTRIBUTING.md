# Contributing to eaOps

Thanks for helping improve eaOps. This is a reference checklist for enterprise architects, so the most valuable contributions are corrections, missing capabilities, and better vendor-specific detail.

By taking part you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## How to contribute

**Edit the YAML in `content/`, never the generated page.** Each Op is one file (`01-business.yaml`, `02-stake-holders.yaml`, ...) and `dist/eaOps.html` is generated from them by `tools/build_html.py`, so don't edit anything in `dist/` by hand.

- Numbers are derived from file order and position, so don't type them into titles.
- Item numbers typed inside prose (for example "8.7") are not updated automatically. If your change moves or inserts an item, fix those references too.
- Before opening a pull request, run `make check` to validate your YAML and `make preview` to see the result without touching `dist/`. The first run sets up its own Python environment. Details, and the steps without `make`, are in the [README](README.md#setup-validate-and-preview).
- You don't choose the version. After a merge, a maintainer bumps `VERSION`, rebuilds `dist/` and tags the release.

Every release is tagged in git (for example `v26.9.1`). Tagged files never change, and fixes ship in the next version.

If you'd rather not edit YAML, open an issue using the templates:

- **Content suggestion**: add, change or remove a Function or Parameter.
- **Vendor line**: improve a Parameter's Azure, GCP, AWS or open-source description.
- **Error report**: a factual error, broken cross-reference, typo or layout problem.
- **Tooling bug**: a problem with `make` or the build scripts.

For questions and open-ended ideas, use Discussions instead.

Refer to items by their number (for example `1.2.1` or `8.7`) and say which version you are looking at.

## Your first pull request, step by step

This walks through adding one Parameter to *1.1 Business Architecture*. Keep each pull request to one topic.

**1. Fork and clone.** Click **Fork** on the repository page, then clone your fork:

```
git clone <URL of your fork>
cd <the cloned folder>
```

**2. Check you have Python 3 and `make`.** There is nothing else to set up: the first `make` command creates a `.venv` folder and installs the requirements by itself. Steps without `make` are in the [README](README.md#setup-validate-and-preview). Python is only used to validate and preview your change, but nothing else checks your YAML before review.

**3. Create a branch**, one per change:

```
git checkout -b content/add-exit-strategy
```

**4. Edit `content/`.** Open the file for the Op, here `content/01-business.yaml`, and add the entry to the Function's `parameters:` list. Adding it at the end of the list gives it the next free number without renumbering anything else, so no typed references break:

```yaml
      - title: Exit Strategy
        all: Documented plan to migrate away from a platform or vendor — data export, cutover, cost
```

Use `all:` when the wording is the same for every vendor. Otherwise give `azure:`, `gcp:`, `aws:` and `oss:` separately. Don't type numbers anywhere.

**5. Validate and preview.**

```
make check
```

The Parameter count it prints should go up by one. Then build a preview, which leaves `dist/` untouched, and open `preview/eaOps.html` in a browser:

```
make preview
```

**6. Check that only your change is included.**

```
git status
git diff
```

Only files under `content/` should appear. Don't commit `dist/` or `VERSION`.

**7. Commit and push.**

```
git add content/01-business.yaml
git commit -m "Add Exit Strategy parameter to 1.1 Business Architecture"
git push -u origin content/add-exit-strategy
```

**8. Open the pull request.** After the push, GitHub shows a **Compare & pull request** button. The base is the `main` branch of the original repository. Say what you changed and why, link any related issue, and tick the checklist.

**9. After you open it.** A maintainer reviews it. If changes are requested, commit to the same branch and push again, and the pull request updates itself. All conversations must be resolved before it can merge. Maintainers squash-merge, then bump `VERSION`, rebuild `dist/` and tag the release, so you don't need to.

## What makes a good contribution

- **Vendor-neutral.** A capability must make sense on Azure, GCP, AWS and open source. Don't tie it to one vendor.
- **Four descriptions per Parameter**, in this order: Azure, GCP, AWS, open-source. Name a real service where the vendors differ. Identical wording across all four is intentional where the capability is vendor-agnostic, so please don't propose changes to it just to differentiate the vendors.
- **Grounded in CPO.** Examples use the single hypothetical Customer, Products & Orders use case. Please don't introduce other domains.
- **No marketing language.** Describe the capability, not the product pitch. Link a public source when you claim something specific.
- **Don't renumber.** Suggest where an item belongs and maintainers will handle the numbering and cross-references.

## Licensing of contributions

This repository is dual-licensed: content under [CC BY 4.0](LICENSE-CONTENT) and code under the [MIT License](LICENSE). By submitting a contribution you agree to license it under the same terms, content under CC BY 4.0 and code under MIT. There is no separate CLA.

Only contribute text you wrote yourself or have the right to license this way. Don't paste vendor documentation or material from your employer or clients.

## Disclaimer

eaOps is educational and is not professional, architectural, security or compliance advice. See the disclaimer in the document and in the [README](README.md).
