#! /bin/bash
git push --delete origin v1.0.1
git tag v1.0.1
git add . && git commit -m "-" && git push
git push --tag