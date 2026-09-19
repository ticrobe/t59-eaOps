#!/usr/bin/env python3
"""Build dist/eaOps.html from the per-Op YAML files in content/.

    python tools/build_html.py                        # version from the VERSION file, date = today
    python tools/build_html.py --updated 9/17/2026    # set the footer date explicitly
    python tools/build_html.py --check                # validate the YAML only

The version comes from the VERSION file at the repo root. The build refuses to
overwrite an output that already carries the same version (use --force). The
block diagram dist/eaOps.png is drawn by tools/build_block_diagram.py and is not touched.

Numbers are never stored in the content: Ops are numbered by file order
(01-, 02-, ...), Functions and Parameters by their position. Inline markup in
text is *italic* and **bold**. `all:` on a Parameter means the same wording for
Azure, GCP, AWS and open-source. The page shell (CSS, JS, header, footer,
disclaimer) lives in tools/template.html.
"""
import argparse
import datetime
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VENDORS = [("azure", "azure"), ("gcp", "gcp"), ("aws", "aws"), ("oss", "open-source")]
VENDOR_KEYS = [key for key, _ in VENDORS]
PLACEHOLDERS = ["VERSION", "UPDATED", "OP_COUNT", "DIAGRAM_ALT", "TOC", "OPS"]


class ContentError(Exception):
    pass


def inline(text, where=""):
    """Escape text and turn **bold** / *italic* into HTML."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\*(.+?)\*", r"<em>\1</em>", out)
    if "*" in out:
        raise ContentError(f"{where}: unbalanced * (use *italic* or **bold**)")
    return out


def text_of(where, value):
    if not isinstance(value, str) or not value.strip():
        raise ContentError(f"{where}: must be non-empty text (quote it if it looks like a number or true/false)")
    inline(value, where)
    return value.strip()


def mapping(where, value, required, optional=()):
    if not isinstance(value, dict):
        raise ContentError(f"{where}: expected a mapping")
    missing = [k for k in required if k not in value]
    unknown = [k for k in value if k not in (*required, *optional)]
    problems = []
    if missing:
        problems.append(f"missing {', '.join(missing)}")
    if unknown:
        problems.append(f"unknown key {', '.join(map(str, unknown))} (check the spelling)")
    if problems:
        raise ContentError(f"{where}: {'; '.join(problems)}")
    return value


def nonempty_list(where, value):
    if not isinstance(value, list) or not value:
        raise ContentError(f"{where}: expected a non-empty list")
    return value


def load_parameter(where, raw):
    raw = mapping(where, raw, ["title"], ["all", *VENDOR_KEYS])
    title = text_of(f"{where} title", raw["title"])
    where = f"{where} '{title}'"
    if "all" in raw:
        if any(k in raw for k in VENDOR_KEYS):
            raise ContentError(f"{where}: use either `all` or the four vendor keys, not both")
        lines = {k: text_of(f"{where} all", raw["all"]) for k in VENDOR_KEYS}
    else:
        absent = [k for k in VENDOR_KEYS if k not in raw]
        if absent:
            raise ContentError(f"{where}: missing {', '.join(absent)} (or use `all`)")
        lines = {k: text_of(f"{where} {k}", raw[k]) for k in VENDOR_KEYS}
    return {"title": title, "lines": lines}


def load_op(path, raw):
    where = path.name
    raw = mapping(where, raw, ["title", "intro", "functions"])
    op = {"title": text_of(f"{where} title", raw["title"]), "intro": text_of(f"{where} intro", raw["intro"]), "functions": []}
    for i, fraw in enumerate(nonempty_list(f"{where} functions", raw["functions"]), 1):
        fraw = mapping(f"{where} function #{i}", fraw, ["title", "parameters"])
        ftitle = text_of(f"{where} function #{i} title", fraw["title"])
        fwhere = f"{where} function '{ftitle}'"
        params = [load_parameter(f"{fwhere} parameter #{j}", praw)
                  for j, praw in enumerate(nonempty_list(f"{fwhere} parameters", fraw["parameters"]), 1)]
        op["functions"].append({"title": ftitle, "parameters": params})
    return op


def load_ops(content_dir):
    files = sorted(content_dir.glob("*.yaml"))
    if not files:
        raise ContentError(f"no .yaml files in {content_dir}")
    ops = []
    for n, path in enumerate(files, 1):
        if not re.match(rf"{n:02d}-.+\.yaml$", path.name):
            raise ContentError(f"{path.name}: expected a name starting with {n:02d}- (Ops are numbered by file order, without gaps)")
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as err:
            raise ContentError(f"{path.name}: invalid YAML: {err}") from err
        ops.append(load_op(path, raw))
    return ops


def render_op(n, op):
    lines = []

    def add(depth, s):
        lines.append("    " * depth + s)

    add(0, f'<details class="op" id="op-{n}">')
    add(1, f'<summary class="op-sum"><span class="id">{n}</span>{inline(op["title"])}</summary>')
    add(1, '<div class="acc-content">')
    add(2, f'<p class="op-intro">{inline(op["intro"])}</p>')
    for m, fn in enumerate(op["functions"], 1):
        add(2, f'<details class="function" id="func-{n}-{m}">')
        add(3, f'<summary class="function-sum"><span class="id">{n}.{m}</span>{inline(fn["title"])}</summary>')
        add(3, '<div class="acc-content">')
        for k, param in enumerate(fn["parameters"], 1):
            add(4, '<details class="parameter">')
            add(5, f'<summary class="parameter-sum"><span class="id">{n}.{m}.{k}</span>{inline(param["title"])}</summary>')
            add(5, '<div class="acc-content">')
            for key, label in VENDORS:
                add(6, f'<div class="desc-line {key}"><span class="id">{n}.{m}.{k}.{label}</span>{inline(param["lines"][key])}</div>')
            add(5, '</div>')
            add(4, '</details>')
        add(3, '</div>')
        add(2, '</details>')
    add(1, '</div>')
    add(0, '</details>')
    return lines


def render_toc(ops):
    lines = ['<nav class="toc">', '    <h2>Table of Contents</h2>', '    <ul>']
    for n, op in enumerate(ops, 1):
        lines.append(f'        <li><a href="#op-{n}"><span class="id">{n}</span>{inline(op["title"])}</a>')
        lines.append('            <ul>')
        for m, fn in enumerate(op["functions"], 1):
            lines.append(f'                <li><a href="#func-{n}-{m}"><span class="id">{n}.{m}</span>{inline(fn["title"])}</a></li>')
        lines.append('            </ul>')
        lines.append('        </li>')
    lines += ['    </ul>', '</nav>']
    return lines


def fill(template, ops, version, updated):
    for name in PLACEHOLDERS:
        if "{{%s}}" % name not in template:
            raise ContentError(f"template is missing the {{{{{name}}}}} placeholder")
    titles = ", ".join(op["title"] for op in ops)
    alt = f"eaOps block diagram — {len(ops)} Ops ({titles}) around a central Enterprise Architect"
    values = {
        "VERSION": version,
        "UPDATED": updated,
        "OP_COUNT": str(len(ops)),
        "DIAGRAM_ALT": html.escape(alt, quote=True),
    }
    for name, value in values.items():
        template = template.replace("{{%s}}" % name, value)

    ops_lines = []
    for n, op in enumerate(ops, 1):
        ops_lines += render_op(n, op) + [""]
    blocks = {"TOC": render_toc(ops), "OPS": ops_lines[:-1]}
    for name, block in blocks.items():
        def indent_block(match, block=block):
            pad = match.group(1)
            return "\n".join(pad + line if line else line for line in block)
        template = re.sub(rf"^([ \t]*)\{{\{{{name}\}}\}}[ \t]*$", indent_block, template, flags=re.M)
    if "{{" in template:
        raise ContentError("template still contains an unfilled {{...}} placeholder")
    return template


def today():
    d = datetime.date.today()
    return f"{d.month}/{d.day}/{d.year}"


def read_version():
    path = ROOT / "VERSION"
    if not path.is_file():
        raise ContentError(f"{path} not found (it holds the version, e.g. 26.9.1)")
    version = path.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d{2}\.\d{1,2}\.\d+", version):
        raise ContentError(f"VERSION '{version}' is not like 26.9.1 (YY.M.patch)")
    return version


def built_version(path):
    """Version of an already-built page, read from its <title>, or None."""
    if not path.is_file():
        return None
    match = re.search(r"<title>eaOps (\S+)</title>", path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--updated", default=today(), help="'Last Updated' date shown in the footer, e.g. 9/17/2026 (default: today)")
    parser.add_argument("--content", type=Path, default=ROOT / "content", help="folder of Op YAML files (default: content/)")
    parser.add_argument("--out", type=Path, default=ROOT / "dist" / "eaOps.html", help="output HTML file (default: dist/eaOps.html)")
    parser.add_argument("--template", type=Path, default=ROOT / "tools" / "template.html")
    parser.add_argument("--check", action="store_true", help="validate the content and exit without writing anything")
    parser.add_argument("--force", action="store_true", help="overwrite the output even if it already has this version")
    args = parser.parse_args()

    version = read_version()
    if not args.content.is_dir():
        raise ContentError(f"{args.content} does not exist")

    ops = load_ops(args.content)
    functions = sum(len(op["functions"]) for op in ops)
    parameters = sum(len(fn["parameters"]) for op in ops for fn in op["functions"])
    summary = f"{len(ops)} Ops, {functions} Functions, {parameters} Parameters"

    if args.check:
        print(f"OK: {summary}")
        return

    if not args.template.is_file():
        raise ContentError(f"template not found: {args.template}")
    out = args.out
    if built_version(out) == version and not args.force:
        raise ContentError(f"{out} is already version {version}. Bump VERSION for a new release, or pass --force to overwrite it.")
    page = fill(args.template.read_text(encoding="utf-8"), ops, version, args.updated)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"Built {out} (version {version})\n  {summary}")

    png = out.parent / "eaOps.png"
    if not png.is_file():
        print(f"  warning: {png} not found, so the page's block diagram will be missing")
    print("  Note: the block diagram PNG shows these counts and the version as text, so regenerate it with tools/build_block_diagram.py.")


if __name__ == "__main__":
    try:
        main()
    except ContentError as err:
        sys.exit(f"error: {err}")
