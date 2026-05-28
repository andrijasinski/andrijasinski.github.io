"""
Tag portfolio md files with `black-and-white` or `color` based on their image.
Usage: python tag_bw_color.py <portfolio_dir>
"""
import re
import sys
from pathlib import Path

from image_utils import is_black_and_white

REPO_ROOT = Path(__file__).resolve().parent


def resolve_image(md_image_path: str) -> Path:
    # md frontmatter uses /images/... which lives on disk under assets/images/...
    rel = md_image_path.lstrip('/')
    if rel.startswith('images/'):
        rel = 'assets/' + rel
    return REPO_ROOT / rel


def process_md(md_path: Path) -> tuple[str, bool]:
    """Returns (label, changed)."""
    text = md_path.read_text()
    fm_match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not fm_match:
        raise ValueError(f"No frontmatter in {md_path}")
    fm = fm_match.group(1)
    fm_end = fm_match.end()

    img_match = re.search(r'^images:\n((?:- .+\n?)+)', fm, re.MULTILINE)
    if not img_match:
        raise ValueError(f"No images in {md_path}")
    first_image = img_match.group(1).splitlines()[0].lstrip('- ').strip()

    image_file = resolve_image(first_image)
    if not image_file.exists():
        raise FileNotFoundError(image_file)

    label = 'black-and-white' if is_black_and_white(image_file) else 'color'

    tags_match = re.search(r'^tags:\n((?:- .+\n?)+)', fm, re.MULTILINE)
    if not tags_match:
        raise ValueError(f"No tags in {md_path}")
    tags_block = tags_match.group(1)
    existing = [line.lstrip('- ').strip() for line in tags_block.splitlines()]

    # Remove any prior bw/color tag, then add the current one
    filtered = [t for t in existing if t not in ('black-and-white', 'color')]
    if label in filtered:
        new_tags = filtered
    else:
        new_tags = filtered + [label]

    new_tags_block = '\n'.join(f'- {t}' for t in new_tags)
    new_fm = fm[:tags_match.start(1)] + new_tags_block + fm[tags_match.end(1):]
    new_text = '---\n' + new_fm + '\n---\n' + text[fm_end:]
    if new_text == text:
        return label, False
    md_path.write_text(new_text)
    return label, True


def main():
    if len(sys.argv) < 2:
        print("Usage: python tag_bw_color.py <portfolio_dir>")
        sys.exit(1)

    portfolio_dir = Path(sys.argv[1])
    md_files = sorted(portfolio_dir.glob('*.md'))

    bw, color, changed = 0, 0, 0
    for md in md_files:
        label, did_change = process_md(md)
        if label == 'black-and-white':
            bw += 1
        else:
            color += 1
        if did_change:
            changed += 1
        print(f"{md.name}: {label}{' (updated)' if did_change else ''}")

    print(f"\nTotal: {len(md_files)} files | B&W: {bw} | Color: {color} | Updated: {changed}")


if __name__ == '__main__':
    main()
