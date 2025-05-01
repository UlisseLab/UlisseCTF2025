#! /bin/env sh 
echo "Make sure to run from the chall root dir!"

cd $1 || exit -1
# Copy
cp -r src/ attachments/
cp checker/pow.py attachments/

# Clean
rm -rf attachments/src/makefile attachments/src/scripts
git clean -Xf attachments/

# Redact
find attachments/ -name '.env' -type f -execdir mv '{}.redacted' '{}' \;

# Compress
tar -czvf attachments/viby-notes.tar.gz attachments/src
rm -rdf attachments/src
