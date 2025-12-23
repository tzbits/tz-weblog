# tz-weblog

A lightweight Python CLI tool for managing static site content and feeds. It transforms Markdown files into HTML and generates aggregate index pages using PEP 292 string templates and YAML metadata.

## Overview

`tz-weblog` provides two primary commands to build a static website:

- md2html: Converts individual Markdown files into HTML pages
- make-feed: Aggregates multiple Markdown files into a single index or feed page (like a blog home page).

## Usage

### 1. Convert Markdown to HTML

```
Usage: weblog md2html [OPTIONS] [FILENAMES]...

  Convert markdown files to html files.

Options:
  --site-yaml PATH            Path to the global site configuration YAML.
  --page-template PATH        Path to a page template with a ${body}
                              placeholder.
  -o, --output-dir DIRECTORY  Directory where HTML files will be saved.
  --help                      Show this message and exit.

```

`--site-yaml` contains global variables (e.g., sitetitle).

`--page-template` is a PEP 292 template, e.g, an HTML or RSS file containing a `${body}` placeholder.

The markdown files given by FILENAMES may have YAML frontmatter (delimited by `---` and `...`). The YAML keys may appear as placeholders in the markdown body.

### 2. Generate an Index Feed

```
$ weblog make-feed --help
Usage: weblog make-feed [OPTIONS] [FILENAMES]...

  Generates an index feed from markdown files and PEP 292 templates.

Options:
  --site-yaml PATH       Path to the global site configuration YAML.
  --page-template PATH   Path to a page template with a ${body} placeholder.
  --items-template PATH  Path to a feed template with a ${items} placehoder.
  --item-template PATH   Path to individual feed item template taking
                         subsitutions from an item's YAML, for example,
                         ${title}.
  -o, --output FILENAME  Output file path (default: stdout)
  --help                 Show this message and exit.
```

## Example

Generate a simple blog index and its corresponding pages.

Create a Metadata-rich Markdown files (e.g. `page1.md`, `page2.md`, etc.):

```
---
title: Page One
author: tzbits
date: 2025-12-19
...
# ${title}

This is page one.
```

Build the Site:

```
# Generate individual HTML pages
weblog md2html \
    --site-yaml site.yaml \
    --page-template index.in.html \
    -o output/ \
    *.md

# Generate the index feed
ls *.md | sort -r | xargs weblog make-feed \
    --site-yaml site.yaml \
    --page-template index.in.html \
    --items-template items.in.html \
    --item-template item.in.html \
    -o output/index.html
```
