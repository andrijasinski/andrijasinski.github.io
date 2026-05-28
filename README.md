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

`python3 generate.py <photos_path> <folder-name> <title> <date> <tags...>`

- `title`: pass `notitle` to hide the title
- `date`: pass `today` to use the current date, otherwise `YYYY-MM-DD`

Example: `python3 generate.py assets/images/2026/May/tartu-titans-vs-riga-bears tartu-titans-vs-riga-bears "Tartu Titans vs Riga Bears" 2026-05-23 archive digital sports`

## Tag photos as black-and-white or color

Scans the image referenced by each md file in a portfolio folder and appends a `black-and-white` or `color` tag to its frontmatter. Idempotent — re-running won't duplicate tags.

`python3 tag_bw_color.py content/portfolio/<folder-name>/`

## Resize

`function resize() {for f in *.jpg; do sips -Z "$1" "$f"; mv "$f" "${f/.png/_$1x.png}"; done } && resize 5000`
