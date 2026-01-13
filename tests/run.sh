#!/bin/bash

function basic_index {
	local out=output/basic_index
    rm -Rf $out
    mkdir -p $out
    ls basic-index/*.md | sort -r \
    | xargs weblog make-feed \
           --site-yaml basic-index/site.yaml \
           --page-template basic-index/index.in.html \
           --items-template basic-index/items.in.html \
           --item-template basic-index/item.in.html \
           -o $out/index.html
    weblog md2html \
           --site-yaml basic-index/site.yaml \
           --page-template basic-index/index.in.html \
           --body-template basic-index/body.in.html \
           -o $out/ \
           basic-index/page1.md basic-index/page2.md basic-index/page3.md
    diff -r -u goldens/basic-index $out/
}

function no_yaml {
	local out=output/no_yaml
    rm -Rf $out
    mkdir -p $out
    ls no-yaml/*.md | sort -r \
    | xargs weblog make-feed \
           --page-template no-yaml/index.in.html \
           --items-template no-yaml/items.in.html \
           --item-template no-yaml/item.in.html \
           -o $out/index.html
    weblog md2html \
           --page-template basic-index/index.in.html \
           --body-template basic-index/body.in.html \
           -o $out/ \
           no-yaml/page1.md no-yaml/page2.md no-yaml/page3.md
    diff -r -u goldens/no-yaml $out/
}


basic_index
no_yaml

echo "Testing finished."
