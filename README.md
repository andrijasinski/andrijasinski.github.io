# Scripts

## Pre commit hook

Path `.git/hooks/pre-commit`

```bash
#!/bin/sh

HUGO_ENVIRONMENT="production"
HUGO_ENV="production"
hugo --gc --minify --baseURL "https://andrijasinski.eu"

git add public

exit 0
```

## Generate md files

`python3 generate.py assets/images/path/to/images folder-name archive digital other tags`

## Resize

`function resize() {for f in *.jpg; do sips -Z "$1" "$f"; mv "$f" "${f/.png/_$1x.png}"; done } && resize 5000`
