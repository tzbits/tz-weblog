# Copyright 2025 tzbits.com
"""A CLI tool to manage static site content and feeds."""

import pathlib
import string
from typing import Any, Dict, List, Optional, Tuple

import click
import markdown
import yaml


def _read(path: str, default: str = "") -> str:
    return pathlib.Path(path).read_text(encoding="utf-8") if path else default


def _load_md_yaml(filename: str) -> Tuple[str, Dict[str, Any]]:
    """Returns (body, metadata)."""
    content = _read(filename)
    if "---" in content and "..." in content:
        parts = content.split("---", 1)
        meta_block = parts[1].split("...", 1)
        return meta_block[1].strip(), yaml.safe_load(meta_block[0]) or {}
    return content.strip(), {"title": filename}


def _subst(tmpl: str, **ctx) -> str:
    return string.Template(tmpl).safe_substitute(ctx)


@click.group()
def cli():
    """Static site generation subcommands."""
    pass


@cli.command("md2html")
@click.option(
    "--site-yaml",
    type=click.Path(exists=True),
    help="Path to the global site configuration YAML.",
)
@click.option(
    "--page-template",
    type=click.Path(exists=True),
    help="Path to a page template with a ${body} placeholder.",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, writable=True),
    default=".",
    help="Directory where HTML files will be saved.",
)
@click.argument("filenames", nargs=-1, type=click.Path(exists=True))
def md2html(
    filenames: List[str],
    page_template: Optional[str],
    site_yaml: Optional[str],
    output_dir: str,
):
    """Convert markdown files to html files."""
    site_dict = yaml.safe_load(_read(site_yaml)) or {} if site_yaml else {}
    page_template = _read(page_template, default="${body}")

    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for filename in filenames:
        body, metadata = _load_md_yaml(filename)
        markdown_body = _subst(body, **site_dict, **metadata)

        html_body = markdown.markdown(markdown_body)
        final_html = _subst(page_template, **site_dict, body=html_body)

        input_file = pathlib.Path(filename)
        target_file = output_path / input_file.with_suffix(".html").name

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(final_html)


@cli.command("make-feed")
@click.option(
    "--site-yaml",
    type=click.Path(exists=True),
    help="Path to the global site configuration YAML.",
)
@click.option(
    "--page-template",
    type=click.Path(exists=True),
    help="Path to a page template with a ${body} placeholder.",
)
@click.option(
    "--items-template",
    type=click.Path(exists=True),
    help="Path to a feed template with a ${items} placehoder.",
)
@click.option(
    "--item-template",
    type=click.Path(exists=True),
    help="""Path to individual feed item template taking subsitutions
    from an item's YAML, for example, ${title}.""",
)
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    default="-",
    help="Output file path (default: stdout)",
)
@click.argument("filenames", nargs=-1, type=click.Path(exists=True))
def make_feed(filenames, site_yaml, page_template, items_template,
              item_template, output):
    """Generates an index feed from markdown files and PEP 292
    templates."""

    if not filenames:
        return

    site_dict = yaml.safe_load(_read(site_yaml)) or {} if site_yaml else {}

    p_tmpl, is_tmpl, i_tmpl = _read(page_template, "${body}"), _read(
        items_template, "${items}"), _read(item_template)

    items = [
        _subst(i_tmpl, **site_dict,
               **_load_md_yaml(f)[1]) for f in filenames
    ]
    items_wrapped = _subst(is_tmpl, **site_dict, items="".join(items))
    page = _subst(p_tmpl, **site_dict, body=items_wrapped)

    output.write(page)


if __name__ == "__main__":
    cli()
