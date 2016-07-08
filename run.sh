#!/bin/bash
docker run -it -v $(pwd):/app -p 4000:4000 morendil/github-pages
