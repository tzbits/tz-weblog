# tz-weblog

`tz-weblog` is a command-line interface (CLI) utility designed for the management of static site content. It facilitates the transformation of Markdown source files into HTML and the generation of aggregate index feeds. The tool utilizes PEP 292 string templates for variable substitution and extracts metadata from YAML frontmatter.

## Installation

The following dependencies are required:

* `Click` (CLI framework)
* `Markdown` (Markdown-to-HTML conversion)
* `PyYAML` (Metadata parsing)

Install the dependencies via `pip` from the tz-weblog directory:

```bash
pip install .

```

## Templating Model

The tool employs a hierarchical substitution model. Templates use the `${variable}` syntax. Variables are resolved from the following sources in increasing order of precedence:

1. Global Configuration: Key-value pairs provided via the `--site-yaml` option.
2. File Metadata: YAML frontmatter extracted from the Markdown source.
3. Computed Variables: Runtime-specific data such as navigation links.

### Templating Hierarchy for `md2html` command

* Page Template: The global layout. Must contain a `${body}` placeholder.
* Body Template: The article-specific layout. Must contain a `${content}` placeholder.
* Content: The HTML rendered from the Markdown source.

### Templating Hierarchy for `make-feed` command

* Page Template: The global layout. Must contain a `${body}` placeholder.
* Items Template: The container for the feed list. Must contain an `${items}` placeholder.
* Item Template: The layout for individual entries, mapped to the metadata of each source file (title, date, author, etc.).

## Usage

### Converting Markdown to HTML

The `md2html` command processes Markdown files and outputs individual HTML pages.

```bash
weblog md2html [OPTIONS] FILENAMES...

```

Options:

* `--site-yaml`: Path to global configuration variables
* `--page-template`: Path to the outer template around `${body}`
* `--body-template`: Path to the inner `${content}` wrapper
* `-o, --output-dir`: Target directory for generated HTML files

### Generating an Index Feed

Use the `make-feed` command to aggregate metadata from multiple Markdown files into a single index file.

```bash
weblog make-feed [OPTIONS] FILENAMES...

```

Use this command to create a blog homepage or an archive list. It iterates over the provided filenames, extracts their metadata, applies the `item-template`, and joins the results into the `items-template`.

Options:

* `--site-yaml`: Path to global configuration variables
* `--page-template`: Path to the outer template around `${body}` replaced by items
* `--items-template`: Path to the template around `${items}`
* `--item-template`: Path to the templater that uses markdown frontmatter (`${title}`, etc.)
* `-o, --output-dir`: Target directory for generated HTML files

## Automatic Sequential Navigation

The `md2html` command binds sequential navigation variables that can be used in the body template to create "Next" and "Previous" links in a series of posts.

* `${filename}`: The name of the current output file.
* `${next_filename}`: The filename of the next item in the sequence.
* `${previous_filename}`: The filename of the previous item in the sequence.

Note: The navigation logic uses modulo arithmetic, meaning the sequence wraps around (the last item links forward to the first item, and the first item links back to the last).


## Example

### 1. Define Source Content (`post_01.md`)

```yaml
---
title: Introduction to tz-weblog
author: tzbits
date: 2026-01-13
...
# ${title}

Content authored by ${author}.

```

### 2. Run tz-weblog

```bash
# Generate HTML pages
weblog md2html \
    --site-yaml config.yaml \
    --page-template page.in.html \
    --body-template article.in.html \
    --output-dir ./dist \
    content/*.md

# Generate the index feed
weblog make-feed \
    --site-yaml config.yaml \
    --page-template page.in.html \
    --items-template index_wrapper.in.html \
    --item-template index_item.in.html \
    --output ./dist/index.html \
    content/*.md

```
