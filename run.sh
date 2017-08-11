#!/bin/bash
docker run -it -v $(pwd):/usr/src/app -p 4000:4000 starefossen/github-pages
