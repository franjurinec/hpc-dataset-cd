#!/bin/bash
# Donwload correct code version to cluster TMP/scratch disk
TAG_SLUG=$(echo $TAG | iconv -t ascii//TRANSLIT | sed -E -e 's/[^[:alnum:]]+/-/g' -e 's/^-+|-+$//g' | tr '[:upper:]' '[:lower:]')

cd $TARGET_DIR/$TAG_SLUG
