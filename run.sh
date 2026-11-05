#!/bin/bash
# jekyll/jekyll:pages ships the github-pages gem preinstalled and is multi-arch (amd64 + arm64).
docker run --rm -it \
    -v "$(pwd)":/srv/jekyll \
    -p 4000:4000 \
    jekyll/jekyll:pages \
    jekyll serve --host 0.0.0.0 --watch --force_polling
