import pathlib
import json
import shutil

static_photos_folder_path = pathlib.Path('static/photos')
gallery_photos_folder_path = pathlib.Path('content/photos')
index_file_name = 'index.md'

meta_files = static_photos_folder_path.glob('**/meta.json')

for meta_file in meta_files:
    with open(meta_file, 'r') as f:
        meta = json.load(f)
        photos = meta_file.parent.glob('**/*.[jJ][pP][gG]')

        for photo in photos:
            if photo.name == 'meta.json' or not meta['title']:
                continue
            gallery_photo_path = gallery_photos_folder_path / f"{meta['title'].replace(' ', '-').lower()}-{photo.name}"
            gallery_photo_path.mkdir(parents=True, exist_ok=True)
            shutil.copy(photo, gallery_photo_path / photo.name)
            with (gallery_photo_path / index_file_name).open("w") as f:
                f.write(f'+++\nimage = "{photo.name}"\ndate = "{meta["date"]}"\ntitle = "{meta["title"]}"\ntype = "gallery"\n+++\n')
                f.write(f'```\nCamera: {meta["camera"]}\nLens: {meta["lens"]}\n')
                if (meta['film']):
                    f.write(f'Film: {meta["film"]}\n')
                f.write('```\n')
