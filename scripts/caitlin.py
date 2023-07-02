      
import os
import re
import time
import json
import random
import zipfile
from tqdm import tqdm

from io import BytesIO
from PIL import Image

from functools import partial
import functools

import requests
import argparse


from multiprocessing.pool import ThreadPool



NUM_THREADS = 2
RETRY = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
}

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
                    if not ignore and retries == 0: raise e
                    if retries > 0 and interval: time.sleep(interval)
            return ret
        return wrapper
    return decorator



def fetch(comic_id):
    params = {
        "route": "comic/readOnline",
        "comic_id": comic_id
    }
    r = requests.get(f"https://caitlin.top/index.php", params=params, headers=HEADERS)
    html = r.text

    title = re.search(r'<span class="d">(.+)<span>', html).group(1)
    title = title.replace(" ", "")

    root_url = re.search(r'HTTP_IMAGE = "(//.+)";', html).group(1)

    images = re.search(r'Image_List = (\[.+\]);', html).group(1)
    images = json.loads(images)
    images = [f"https:{root_url}{image['sort']}.{image['extension'] if image['extension'] in ['webp', 'jpg'] else 'jpg'}" for image in images]
    # images = [f"https:{root_url}{image['sort']}.jpg" for image in images]
    return title, images

@retry(max_retries=3, interval=4, ignore=True)
def saveImage(url, folder, extension):
    
    filename = os.path.basename(url)
    filename, suffix = os.path.splitext(filename)
    # filename = (4-len(filename))*"0" + filename + extension or ".jpg"
    filename = f"{(4-len(filename))*'0'}{filename}.{extension or 'jpg'}"

    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        return filename, 0

    r = requests.get(url, headers=HEADERS, timeout=15)

    # if not os.path.exists(filepath):
    filesize = len(r.content)
    with open(filepath, 'wb') as f:
        f.write(r.content)

    return filename, filesize

def zip_dir(folder, zipname):
    with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_STORED) as f:
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                f.write(os.path.join(dirpath, filename), filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hentai Image Crawler!')
    parser.add_argument('-c', "--comic_id", nargs='+', type=list, required=True)
    parser.add_argument('-f', '--folder', default="./", type=str)
    parser.add_argument('-e', '--extension', default=None, type=str)
    parser.add_argument('-z', '--zip', action="store_true")
    parser.add_argument('-y', '--yes', action="store_true")
    args = parser.parse_args()

    for comic_id in args.comic_id:
        comic_id = "".join(comic_id)
        title, images = fetch(comic_id)
        folder = os.path.join(args.folder, title)
        if os.path.exists(folder) and (not args.yes and input("Folder exists. continue?[y/n] ")[0]=="n"):
            exit()

        os.makedirs(folder, exist_ok=True)

        # save = lambda x: saveImage(x, folder, extension)
        save = partial(saveImage, folder=folder, extension=args.extension) 

        # print(f"{title}[{len(images)}P]")
        results = ThreadPool(NUM_THREADS).imap(save, images)
        with tqdm(results, total=len(images), desc=f"{title}", ncols=120) as t:
            for filename, filesize in t:
                t.set_postfix({"name": filename, "size": f"{round(filesize/1024)}kb"})

        if args.zip:
            zip_dir(folder, f"{title}.zip")


