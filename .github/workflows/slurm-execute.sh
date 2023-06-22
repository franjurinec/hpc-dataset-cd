#!/bin/bash
TAG_SLUG= echo $TAG | iconv -t ascii//TRANSLIT | sed -E -e 's/[^[:alnum:]]+/-/g' -e 's/^-+|-+$//g' | tr '[:upper:]' '[:lower:]'
# git clone --depth 1 --branch $TAG $REPO_URL $TARGET_TMP_DIR/$TAG_SLUG
# cd $TARGET_TMP_DIR/$TAG_SLUG

# rm -r $TARGET_TMP_DIR/$TAG_SLUG

echo $TARGET_TMP_DIR/$TAG_SLUG
echo $TAG
echo $REPO_URL