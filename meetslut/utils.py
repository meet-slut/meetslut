from typing import List, Union, Tuple, Optional

import os
import re
import time
import zipfile
import requests
import functools


from meetslut.config import HEADERS, MAX_RETRY

def retry(max_retries=3, interval=None, ignore=False):
    """ function retry

    Args:
        max_retries (int, optional): retry. Defaults to 3.
        interval (_type_, optional): retry interval. Defaults to None.
        ignore (bool, optional): ignore error when max retry reach. Defaults to False.

    Raises:
        e: execute error

    """
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


def amend_suffix(s: str) -> str:
    """ amend image extension, except all '.jpg'

    Args:
        s (str): file extension

    Returns:
        str: file extension
    """
    return s if s in [".gif", ".jpg", ".jpeg", ".png"] else '.jpg'


def rename(paths: List[str], names: Optional[List[str]] = None, auto_increment: bool = False) -> List[str]:
    """ Batch renaming files

    Args:
        urls (List[str]): file urls
        names (List[str], optional): file names. Defaults to False.
        auto_increment (bool, optional): use auto-increasing index as filename. Defaults to False.

    Returns:
        List[str]: _description_
    """
    res = []
    max_length = len(str(len(paths)))
    if names is None:
        names = [None] * len(paths)
    for idx, (path, name) in enumerate(zip(paths, names), start=1):
        filename = name or os.path.basename(path)
        filename, suffix = os.path.splitext(filename)
        suffix = amend_suffix(suffix)
        filename = str(idx).zfill(max_length) if auto_increment else filename
        filename = re.sub(r"[\/\\\:\*\?\"\<\>\|]", " ", filename)
        if not auto_increment and f"{filename}{suffix}" in res:
            filename = filename + str(idx)
        res.append(f"{filename}{suffix}")
    return res


def zip_dir(folder: str, zipname: str) -> bool:
    with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_STORED) as f:
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                f.write(os.path.join(dirpath, filename), filename)
    return True

# @retry(max_retries=MAX_RETRY, interval=3, ignore=True)
def saveImage(url: str, filepath: str, folder: Optional[str] = None, force_download: bool = False) -> Tuple[str, int]:
    filename = os.path.basename(filepath)
    if folder is not None:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

    if not force_download and os.path.exists(filepath):
        return filename, os.path.getsize(filepath)

    r = requests.get(url, headers=HEADERS, timeout=15)

    filesize = len(r.content)
    with open(filepath, 'wb') as f:
        f.write(r.content)

    return filename, filesize

