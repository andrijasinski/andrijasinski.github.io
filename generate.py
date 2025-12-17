import sys
from pathlib import Path
from datetime import datetime


CONTENT_PATH = "content/portfolio"

def main():
    print('argument list', sys.argv)
    current_path = Path.cwd()

    photos_path = sys.argv[1]
    content_folder_name = sys.argv[2]
    title = sys.argv[3]
    date = sys.argv[4]
    tags = sys.argv[5:]
    prepped_tags = "\n".join(list(map(lambda x: f'- {x}', tags)))
    output_date = date if date != "today" else datetime.now().strftime("%Y-%m-%d")
    output_title = f"title: {title}\n" if title != "notitle" else "hideTitle: true\n"

    photos = sorted((current_path / photos_path).rglob('*.jpg'))
    i = 1001
    for photo in photos:
        photo_path = str(photo.relative_to(current_path)).strip("assets")
        print(photo_path)

        photo_content_path = (current_path / CONTENT_PATH / content_folder_name)
        photo_content_path.mkdir(parents=True, exist_ok=True)
        with (photo_content_path  / f"{content_folder_name}-{i}.md").open('w') as f:
            f.write(f"---\n")
            f.write(f"weight: 1\n")
            f.write(f"images:\n- {photo_path}\n")
            f.write(output_title)
            f.write(f"date: {output_date}\n")
            f.write(f"tags:\n{prepped_tags}\n")
            f.write(f"---\n\n")
            # f.write("Camera: Canon EOS 500N\n\n")
            # f.write("Film: Cinestill 800T (pushed 2 stop to 3200 ISO)")
        i += 1


if __name__ == '__main__':
    main()