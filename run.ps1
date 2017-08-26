$curpath=$PWD.Path.Replace('\', '/');
docker run -ti -v ${curpath}:/usr/src/app -p 4000:4000 starefossen/github-pages