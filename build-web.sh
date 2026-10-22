#!/bin/sh
# Assembles the public website for Cloudflare Pages (build command: sh build-web.sh, output directory: public):
# the temple tour (3d/, which the posters' QR codes open: /3d/ and /3d/n), its test link (3d-pilot/), and the front door.
# The rest of this repository (print, brand, models' sources) is not published.
set -e
rm -rf public && mkdir -p public
cp -R 3d 3d-pilot public/
cp web-root/_redirects public/
echo "website assembled: $(find public -type f | wc -l) files"
