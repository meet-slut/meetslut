from typing import List, Any

import os
import re
import time
import json
import argparse
import requests
import functools
from urllib.parse import urlparse
from collections import namedtuple

MB = 1<<20

EXTENSION = 'jpg'

PROGRESS_BAR = ["\\", "|", "/", "—"]

TIMEOUT = 7
IMAGE_TIMEOUT = 15
HEADERS={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"}

# PROXIES={
#     'http': 'socks5://127.0.0.1:1080',
#     'https': 'socks5://127.0.0.1:1080'
# }
PROXIES=None


ImageItem = namedtuple('ImageItem', 'id, name, url, width, height')

def colorstr(*inputs):
    # Colors a string https://en.wikipedia.org/wiki/ANSI_escape_code, i.e.  colorstr('blue', 'hello world')
    *args, string = inputs if len(inputs) > 1 else ('blue', 'bold', inputs[0])  # color arguments, string
    string = str(string)
    colors = {
        'black': '\033[30m',  # basic colors
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',  # bright colors
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'end': '\033[0m',  # misc
        'bold': '\033[1m',
        'underline': '\033[4m'}
    return ''.join(colors[x] for x in args) + f'{string}' + colors['end']


def retry(max_retries=3, interval=None, ignore=False):
    assert isinstance(max_retries, int) and max_retries > 0, f"max_retries {max_retries} should be int and greater than 0."
    assert interval is None or isinstance(interval, (float, int)), f"interval {interval} should be number."
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = max_retries
            ret = None
            while retries > 0:
                try:
                    ret = func(*args, **kwargs)
                    break
                except Exception as e:
                    retries -= 1
                    print(f'func {func.__name__} error: {colorstr("red", str(e))}. {retries} retry left.')
                    if not ignore and retries == 0: raise e
                    if retries > 0 and interval: time.sleep(interval)
            return ret
        return wrapper
    return decorator


def prepare_images_id(gallery_id: str) -> List[str]:
    # view=2 means all images in one page
    url = f"https://www.imagefap.com/pictures/{gallery_id}?gid={gallery_id}&view=2"
    r = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT)
    assert r.ok, f"URL: {url} Status code: {r.status_code}"
    gallery_title = re.search('<title>(.*?)</title>', r.text).group(1).strip()
    images_id = re.findall('<td id="([0-9]+)" align="center"  ?valign="top">', r.text)
    return gallery_title, images_id

def filter_images_id(images_id: List[str], folder: str) -> List[str]:
    for filename in os.listdir(folder):
        filename, suffix = os.path.splitext(filename)
        name, image_id = filename.split("_")
        if image_id in images_id:
            images_id.remove(image_id)

    return images_id

def prepare_images_url(image_id: List[str]) -> ImageItem:
    url = f"https://www.imagefap.com/photo/{image_id}"
    r =  requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT)
    name = re.findall('<title>([a-zA-Z0-9_-]+)[.jpg|.JPG|.jpeg|.GIF|.gif|.PNG|.png]+ Porn Pic', r.text)[0]
    matched = re.search('<script type="application/ld\+json">(.*?)</script>', r.text, flags=re.S)
    info = json.loads(matched.group(1).strip())
    image = ImageItem(image_id, name, info["contentUrl"], int(info["width"]), int(info["height"]))
    return image

@retry(max_retries=3, interval=3, ignore=True)
def save_image(url, filepath):
    r = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=IMAGE_TIMEOUT)

    filesize = len(r.content)
    with open(filepath, 'wb') as f:
        f.write(r.content)

    return filesize

def download(images_id: List[str], folder=None, auto_increment=False, interval=3) -> None:
    assert folder is not None
    bar = PROGRESS_BAR
    ext = EXTENSION
    storage = 0
    failures = []
    for idx, image_id in enumerate(images_id):
        im = prepare_images_url(image_id)
        filename = os.path.basename(urlparse(im.url).path)
        filename, suffix = os.path.splitext(filename)
        filename = f"{str(idx+1):04s}" if auto_increment else im.name
        filepath = os.path.join(folder, f"{filename}_{im.id}.{ext or suffix}")
        assert not os.path.exists(filepath), f"File {filepath} exist."

        file_size = save_image(im.url, filepath)
        if isinstance(file_size, int):
            storage += file_size
        else:
            failures.append(image_id)

        print(f"\r{bar[idx%len(bar)]}[{idx+1}/{len(images_id)}] Downloading {filename}[{'🟢' if file_size else '🔴'}], Storage: {storage/MB:.1f} MB", end="\n" if idx == len(images_id)-1 else "", flush=True)

        time.sleep(interval)
    
    
    return failures



def main(args: argparse.ArgumentParser):
    gid = args.gid
    folder = args.folder
    
    gallery_title, images_id = prepare_images_id(gid)
    total_images = len(images_id)
    gallery_title = re.sub(r'[-\s]+', "_", gallery_title)
    folder = folder or gallery_title
    os.makedirs(folder, exist_ok=True)
    
    images_id = filter_images_id(images_id, folder)
    print(f"🚀 Gallery({gid}): [{colorstr('green', str(total_images)+'P')}] {colorstr('green', gallery_title)}. {colorstr('blue', str(len(images_id)))} images to be downloaded!")
    failures = download(images_id, folder, interval=args.interval)
    print(f"⚠️  Following images download failed: {failures}")


if __name__ == '__main__':
    print(" ___                      __             ___                  _              _         ")
    print("|_ _|_ __  __ _ __ _ ___ / _|__ _ _ __  |   \ _____ __ ___ _ | |___  __ _ __| |___ _ _ ")
    print(" | || '  \/ _` / _` / -_)  _/ _` | '_ \ | |) / _ \ V  V / ' \| / _ \/ _` / _` / -_) '_|")
    print(" |__|_|_|_\__,_\__, \___|_| \__,_| .__/ |___/\___/\_/\_/|_||_|_\___/\__,_\__,_\___|_|  ")
    print("               |___/             |_|                                                   ")
    print("")
    
    parser = argparse.ArgumentParser(description='ImageFap Downloader')
    parser.add_argument('--gid', type=str, required=True)
    parser.add_argument('--folder', type=str, default=None)
    parser.add_argument('--interval', type=int, default=7)
    args = parser.parse_args()

    main(args)


"""
python imagefap.py --gid 11026085
python imagefap.py --gid 11100999
"""