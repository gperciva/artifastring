#!/bin/sh
rm -rf build/
mkdir build/
cd build/
../configure
VERSION=`ls artifastring-*.tar.gz | sed 's/artifastring-//' | sed 's/.tar.gz//'`

### tarball
make distcheck
FILENAME=`ls artifastring-*.tar.gz`
echo "Uploading $FILENAME..."
rsync $FILENAME \
  gperciva@percival-music.ca:percival-music.ca/artifastring/
ssh gperciva@percival-music.ca \
  "cd percival-music.ca/artifastring/ && \
     rm -f artifastring-latest.tar.gz && \
     ln -s $FILENAME artifastring-latest.tar.gz"
echo "Done"

### docs
make docs
rsync doc/html/* \
  gperciva@percival-music.ca:percival-music.ca/artifastring/

### tag
git tag release-$VERSION
echo
echo "Update version number:"
echo "  vi configure.ac"

