# Copyright 2025 tzbits.com
"""A CLI tool to manage static site content and feeds.

This module provides commands to convert Markdown files into HTML and generate
index feeds (like RSS or navigation lists) using PEP 292 string templates.
"""

import pathlib
import string
from typing import Any, Dict, List, Optional, Tuple

import click
import markdown
import yaml

# Internal defaults for template substitution to prevent key errors.
_DEFAULTS = {
    "sitetitle": "",
    "title": "",
    "filename": "",
    "next_filename": "",
    "prev_filename": "",
    "author": "",
    "date": "",
}


def read_text(path: Optional[str], default: str = "") -> str:
    """Reads content from a file path.

    Args:
        path: String path to the file.
        default: Fallback string if the path is None or empty.

    Returns:
        The file contents as a string.
    """
    if not path:
        return default
    return pathlib.Path(path).read_text(encoding="utf-8")


def load_md_yaml(filename: str) -> Tuple[Dict[str, Any], str]:
    """Extracts YAML metadata and Markdown body from a file.

    Args:
        filename: Path to the markdown file.

    Returns:
        A tuple containing a dictionary of metadata and the raw markdown text.
    """
    content = read_text(filename)
    if "---" in content and "..." in content:
        # YAML frontmatter uses --- to start and ... to end.
        parts = content.split("---", 1)
        meta_block = parts[1].split("...", 1)
        metadata = yaml.safe_load(meta_block[0]) or {}
        return metadata, meta_block[1].strip()

    return {"title": filename}, content.strip()


def safe_substitute(tmpl: str, **ctx: Any) -> str:
    """Substitutes variables into a PEP 292 template.

    Args:
        tmpl: The template string.
        **ctx: Key-value pairs for substitution.

    Returns:
        The processed string.
    """
    return string.Template(tmpl).safe_substitute(ctx)


def prev_elt(i: int, items: List[Any]) -> Any:
    """Returns the previous item in a list with wrapping.

    Args:
        i: Current index.
        items: The list to navigate.

    Returns:
        The item at the previous index.
    """
    # Using modulo allows the navigation to wrap back to the end of the list
    # when the user is on the first page.
    return items[(i - 1) % len(items)]


def next_elt(i: int, items: List[Any]) -> Any:
    """Returns the next item in a list with wrapping.

    Args:
        i: Current index.
        items: The list to navigate.

    Returns:
        The item at the next index.
    """
    # Using modulo creates a continuous loop, ensuring "Next" links always
    # lead to valid content.
    return items[(i + 1) % len(items)]


def make_files_dict(
    target_file: pathlib.Path, index: int, filenames: List[str]
) -> Dict[str, str]:
    """Generates a dictionary of related filenames for navigation.

    Args:
        target_file: The Path object of the current output file.
        index: The index of the current file in the source list.
        filenames: The list of all source filenames.

    Returns:
        A dictionary containing current, next, and previous HTML filenames.
    """
    prev_file = pathlib.Path(prev_elt(index, filenames)).with_suffix(".html")
    next_file = pathlib.Path(next_elt(index, filenames)).with_suffix(".html")
    return {
        "filename": target_file.name,
        "next_filename": next_file.name,
        "previous_filename": prev_file.name,
    }


@click.group()
def cli():
    """Static site generation subcommands."""


@cli.command("md2html")
@click.option(
    "--site-yaml",
    type=click.Path(exists=True),
    help="Path to the global site configuration YAML.",
)
@click.option(
    "--page-template",
    type=click.Path(exists=True),
    help=(
        "Path to a page template with a ${body} placeholder to be substituted "
        "with the output of --body-template."
    ),
)
@click.option(
    "--body-template",
    type=click.Path(exists=True),
    help=(
        "Path to a body template with a ${content} placeholder to be "
        "substituted with the html generated from the Markdown file."
    ),
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, writable=True),
    default=".",
    help="Directory where HTML files will be saved.",
)
@click.argument("filenames", nargs=-1, type=click.Path(exists=True), required=True)
def md2html(
    filenames: List[str],
    page_template: Optional[str],
    body_template: Optional[str],
    site_yaml: Optional[str],
    output_dir: str,
):
    """Convert Markdown files to HTML files."""
    site_dict = yaml.safe_load(read_text(site_yaml)) or {} if site_yaml else {}
    page_template_text = read_text(page_template, default="${body}")
    body_template_text = read_text(body_template, default="${content}")

    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for index, filename in enumerate(filenames):
        input_file = pathlib.Path(filename)
        target_file = output_path / input_file.with_suffix(".html").name

        metadata, markdown_raw = load_md_yaml(filename)

        # Substitution happens before Markdown conversion to allow template
        # variables to be used within the Markdown source itself.
        markdown_substituted = safe_substitute(markdown_raw, **site_dict, **metadata)
        content_html = markdown.markdown(markdown_substituted)

        # Merge dictionaries in order of increasing specificity.
        context = (
            _DEFAULTS
            | site_dict
            | metadata
            | make_files_dict(target_file, index, list(filenames))
        )

        body_html = safe_substitute(body_template_text, **context, content=content_html)
        page_html = safe_substitute(page_template_text, **context, body=body_html)

        target_file.write_text(page_html, encoding="utf-8")


@cli.command("make-feed")
@click.option(
    "--site-yaml",
    type=click.Path(exists=True),
    help="Path to the global site configuration YAML.",
)
@click.option(
    "--page-template",
    type=click.Path(exists=True),
    help=(
        "Path to a page template with a ${body} placeholder to be substituted "
        "by the output of --items-template."
    ),
)
@click.option(
    "--items-template",
    type=click.Path(exists=True),
    help=(
        "Path to a feed template with a ${items} placeholder to be "
        "substituted with the accumulated results of --item-template."
    ),
)
@click.option(
    "--item-template",
    type=click.Path(exists=True),
    help=(
        "Path to individual feed item template taking substitutions "
        "from an item's YAML, for example, ${title}."
    ),
)
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    default="-",
    help="Output file path (default: stdout)",
)
@click.argument("filenames", nargs=-1, type=click.Path(exists=True), required=True)
def make_feed(
    filenames: List[str],
    site_yaml: Optional[str],
    page_template: Optional[str],
    items_template: Optional[str],
    item_template: Optional[str],
    output,
):
    """Generates an index feed from Markdown files and PEP 292 templates."""

    site_dict = yaml.safe_load(read_text(site_yaml)) or {} if site_yaml else {}

    page_template_text = read_text(page_template, "${body}")
    items_template_text = read_text(items_template, "${items}")
    item_template_text = read_text(item_template, "${item}")

    item_text = []
    for index, filename in enumerate(filenames):
        metadata, _ = load_md_yaml(filename)
        target_file = pathlib.Path(filename)
        context = (
            _DEFAULTS
            | site_dict
            | metadata
            | make_files_dict(target_file, index, list(filenames))
        )
        item_text.append(safe_substitute(item_template_text, **context))

    items_text = safe_substitute(
        items_template_text, **site_dict, items="".join(item_text)
    )
    page_text = safe_substitute(page_template_text, **site_dict, body=items_text)

    output.write(page_text)


if __name__ == "__main__":
    cli()
