import sys
from pathlib import Path
from datetime import datetime


CONTENT_PATH = "content/portfolio"

def main():
    print('argument list', sys.argv)
    current_path = Path.cwd()

    photos_path = sys.argv[1]
    content_folder_name = sys.argv[2]
    tags = sys.argv[3:]
    prepped_tags = "\n".join(list(map(lambda x: f'- {x}', tags)))
    current_date = datetime.now().strftime("%Y-%m-%d")

    photos = (current_path / photos_path).rglob('*.jpg')
    i = 1
    for photo in photos:
        photo_path = str(photo.relative_to(current_path)).strip("assets")
        print(photo_path)

        photo_content_path = (current_path / CONTENT_PATH / content_folder_name)
        photo_content_path.mkdir(parents=True, exist_ok=True)
        with (photo_content_path  / f"{content_folder_name}-1000{i}.md").open('w') as f:
            f.write(f"---\n")
            f.write(f"weight: 1\n")
            f.write(f"images:\n- {photo_path}\n")
            f.write(f"hideTitle: true\n")
            f.write(f"date: {current_date}\n")
            f.write(f"tags:\n{prepped_tags}\n")
            f.write(f"---\n")
        i += 1


if __name__ == '__main__':
    main()