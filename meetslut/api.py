import os
import logging
import functools
from tqdm import tqdm
from multiprocessing.pool import ThreadPool

from meetslut.config import NUM_THREADS

from meetslut.utils import rename, saveImage

def download(urls, filenames, folder, auto_increment=False, num_threads=None):
    """ multi-threading downloader.
    """
    num_threads = num_threads or NUM_THREADS
    os.makedirs(folder, exist_ok=True)
    filenames = rename(urls, filenames, auto_increment)
    save = functools.partial(saveImage, folder=folder, force_download=False)
    logging.info(f"Found {len(urls)} images. Start download in {folder}...")
    if num_threads <= 1:
        with tqdm(zip(urls, filenames), ncols=120, desc=f"Download") as t:
            for url, filename in t:
                filename, filesize = save(url, filename)
                t.set_postfix({"name": filename, "size": f"{round(filesize/1024)} KB"})
    else:
        # pool.imap ppol.starmap
        results = ThreadPool(num_threads).starmap(save, zip(urls, filenames))
        with tqdm(results, total=len(urls), ncols=120, desc=f"Download") as t:
            for filename, filesize in t:
                t.set_postfix({"name": filename, "size": f"{round(filesize/1024)} KB"})