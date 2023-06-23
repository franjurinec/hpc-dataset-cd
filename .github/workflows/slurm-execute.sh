#!/bin/bash
TAG_SLUG=$(echo $TAG | iconv -t ascii//TRANSLIT | sed -E -e 's/[^[:alnum:]]+/-/g' -e 's/^-+|-+$//g' | tr '[:upper:]' '[:lower:]')
git clone --depth 1 --branch $TAG https://github.com/$REPO.git $TARGET_TMP_DIR/$TAG_SLUG
cd $TARGET_TMP_DIR/$TAG_SLUG

# EXECUTE WORKFLOW
sbatch --wait slurm.sh

cat *.out

rm -rf $TARGET_TMP_DIR/$TAG_SLUG
