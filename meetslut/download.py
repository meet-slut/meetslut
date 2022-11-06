
import os
import re
import logging
from functools import partial
from multiprocessing.pool import ThreadPool
import requests
from tqdm import tqdm

from meetslut.config import GET_CFG, NUM_THREADS, RETRY

def saveImage(image, folder):
    url, filename = image
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        return filename, 0
    i, r = 0, None
    while r==None and i<RETRY:
        i += 1
        try:
            r = requests.get(url, headers=GET_CFG['headers'], proxies=GET_CFG['proxies'], timeout=10)
        except:
            continue
        if r.headers["Content-Type"].strip().startswith("image/"):
            break
    if i >= RETRY:
        raise Exception("Max Retries!")

    with open(filepath, 'wb') as f:
        f.write(r.content)
    filesize = len(r.content)

    return filename, filesize


def amend_suffix(s):
    return s if s in [".gif", ".jpg", ".jpeg", ".png"] else '.jpg'

def rename(urls, names, indexed):
    res = []
    max_length = len(str(len(urls)))

    for idx, (url, name) in enumerate(zip(urls, names), start=1):
        filename = os.path.basename(url)
        filename, suffix = os.path.splitext(filename)
        suffix = amend_suffix(suffix)
        filename = str(idx).zfill(max_length) if indexed else name
        filename = re.sub(r"[\/\\\:\*\?\"\<\>\|]", " ", filename)

        if f"{filename}{suffix}" in res:
            filename = filename + str(idx)
        res.append(f"{filename}{suffix}")
    return res


def download(images, folder, indexed=True):
    """ multi-threading downloader.
    """
    os.makedirs(folder, exist_ok=True)
    urls = [i['url'] for i in images]
    names = [i['name'] for i in images]
    files = rename(urls, names, indexed)
    save = partial(saveImage, folder=folder)
    results = ThreadPool(NUM_THREADS).imap(save, zip(urls, files))
    logging.info(f"Start download in {folder}...")
    with tqdm(results, total=len(urls), ncols=100, desc=f"Download") as t:
        for filename, filesize in t:
            t.set_postfix({"name": filename, "size": f"{round(filesize/1024)}kb"})