#!/bin/bash

function basic_index {
    rm -Rf output
    mkdir -p output
    ls basic-index/*.md | sort -r \
    | xargs weblog make-feed \
           --site-yaml basic-index/site.yaml \
           --page-template basic-index/index.in.html \
           --items-template basic-index/items.in.html \
           --item-template basic-index/item.in.html \
           -o output/index.html
    weblog md2html \
           --site-yaml basic-index/site.yaml \
           --page-template basic-index/index.in.html \
           -o output/ \
           basic-index/*.md
    diff -r -u goldens/basic-index output/
}

basic_index

echo "Testing finished."
