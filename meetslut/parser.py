""" given url, parse the html and return metadata
"""

from typing import Union, Optional, Dict, List
from abc import ABCMeta, abstractmethod
import re
import json
import time
import random
from urllib.parse import urlparse
import requests
from lxml import etree
from bs4.element import Tag
from bs4 import BeautifulSoup
from collections import namedtuple
ImageItem = namedtuple('ImageItem', 'id, name, url, width, height')

from meetslut.config import HEADERS, TIMEOUT

class AbstractParser(metaclass=ABCMeta):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def parse(self):
        raise NotImplementedError

    @staticmethod
    def get(url: str, **kwargs) -> requests.Response:
        getargs = {
            "headers": HEADERS,
            "timeout": TIMEOUT
        }
        getargs.update(kwargs)
        r: requests.Response = requests.get(url, **getargs)
        assert r.status_code == 200, f'Statuc code: {r.status_code} @ url: {url}'
        r.encoding = r.apparent_encoding
        return r

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'


class Caitlin(AbstractParser):
    def __init__(self):
        super().__init__('Caitlin')
        self.indexed = True

    def _fetch(self, comic_id: Union[str, int]) -> Dict:
        """ get the title and image urls according to comic id."""
        params = {
            "route": "comic/readOnline",
            "comic_id": str(comic_id)
        }
        r = self.get("https://caitlin.top/index.php", params=params)
        html = r.text
        title = re.search(r'<span class="d">(.+)<span>', html).group(1)
        title = title.replace(" ", "")
        root_url = re.search(r'HTTP_IMAGE = "(//.+)";', html).group(1)

        images = re.search(r'Image_List = (\[.+\]);', html).group(1)
        images = json.loads(images)
        data = {
            'url': r.url,
            'comic_id': str(comic_id),
            'title': title,
            'images': [
                {'name': str(i), 'url': f"https:{root_url}{image['sort']}.{image['extension']}"}
                for i, image in enumerate(images, start=1)
            ]
        }
        return data

    def parse(self, url: str) -> Dict:
        # get comic id
        if url.startswith('https://caitlin.top/index.php'):
            matched = re.search(r'comic_id=(\d+)', url)
            assert matched is not None, f'No valid comic_id in url: {url}.'
            comic_id = matched.group(1)
        elif url.isdigit():
            comic_id = url
        else:
            raise ValueError(f'Invalid url: {url}. It should be full url or comic id.')

        metadata = self._fetch(comic_id)

        return metadata


class Zipai(AbstractParser):
    def __init__(self):
        super().__init__('Zipai')
        self.indexed = True

    # def worklist(uid):
    #     # url = f"{ROOT}/my/{uid}/"
    #     url = f"https://99zipai.com/e/space/ulist.php?page=0&mid=1&line=80&tempid=10&orderby=&myorder=0&userid={uid}"
    #     r = requests.get(url, headers=HEADERS)
    #     assert r.status_code == 200, r.text
    #     r.encoding = r.apparent_encoding
    #     soup = BeautifulSoup(r.text, "html.parser")
    #     total = soup.find("a", attrs={"class": "sh_1"}).span.text.strip()

    #     user = soup.find(name="h2", attrs={"itemprop": "name"}).text.strip()
    #     # print(total, user)
    #     ul = soup.find(name="ul", attrs={"class": "ul_author_list cl"})
    #     for idx, li in enumerate(ul.findAll("li")):
    #         a = li.a
    #         yield a.text, a.get("href")

    def _fetch(self, url: str) -> dict:
        p = urlparse(url)
        root = f"{p.scheme}//{p.netloc}"
        html = self.get(url)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("div", attrs={"class": "item_title"}).h1.text.strip()
        div = soup.find("div", attrs={"class": "content_left"})
        images = []
        for i, ele in enumerate(div.contents, start=1):
            if isinstance(ele, Tag) and ele.name == "img":
                src = ele.get("src")
                if "d/file/selfies" not in src:
                    continue
                if src.startswith("/"):
                    src = root + src
                images.append({'name': str(i), 'url': src})

        data = {
            'title': title,
            'images': images
        }
        return data

    def parse(self, url: str) -> dict:
        if url.startswith("https://www.99zipai.com/selfies"):
            pass
        else:
            raise ValueError(f'Invalid url: {url}. It should be full url or comic id.')

        data = self._fetch(url)
        data['url'] = url
        return data


class Motherless(AbstractParser):
    def __init__(self):
        super().__init__('Motherless')
        self.indexed = False

    def _fetch(self, gid: str, sleep: Optional[Union[int, float]] = None) -> dict:
        url = f"https://motherless.com/{gid}"
        page = 1
        codes = []
        def get(p):
            params = {'page': p} if p>1 else {}
            html = self.get(url, params=params)
            html = etree.HTML(html)
            return html
        html = get(page)
        title = html.xpath("//h2[@id='view-upload-title']/text()")[0].strip()
        amount = int(re.search(r"Images \(([0-9]*)\)", html.xpath("//span[@class='active']/text()")[0]).group(1))
        srcs = html.xpath("//img[@class='static']/@data-strip-src")
        names = html.xpath("//img[@class='static']/@alt")
        codes.extend([{'name': name, 'url': src.replace("thumbs", "images")} for src, name in zip(srcs, names)])
        # print(f"Parse gallery({gid}) {title}: ")
        # print(f"{len(codes)}/{amount} @ page {page}")
        while len(srcs) > 0 and len(codes) <= amount:
            if sleep: time.sleep(sleep if isinstance(sleep, (int, float)) else random.random())
            page += 1
            html = get(page)
            srcs = html.xpath("//img[@class='static']/@data-strip-src")
            names = html.xpath("//img[@class='static']/@alt")
            codes.extend([{'name': name, 'url': src.replace("thumbs", "images")} for src, name in zip(srcs, names)])
            # print(f"{len(codes)}/{amount} @ page {page}")

        data = {
            'title': title,
            'images': codes
        }
        return data

    def parse(self, url: str) -> dict:
        if url.startswith("https://motherless.com"):
            p = urlparse(url)
            gid = p.path.split("/")[-1]
        else:
            raise ValueError(f'Invalid url: {url}. It should be full url or comic id.')
        data = self._fetch(gid)
        data['url'] = url
        return data


class ImageFap(AbstractParser):
    def __init__(self):
        super().__init__('ImageFap')
        self.indexed = False

    def _fetch(self, gid: str) -> Dict:
        # view=2 means all images in one page
        url = f"https://www.imagefap.com/pictures/{gid}?gid={gid}&view=2"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        assert r.ok, f"URL: {url} Status code: {r.status_code}"
        print(r.text)
        gallery_title = re.search('<title>(.*?)</title>', r.text).group(1).strip()
        images_id = re.findall('<td id="([0-9]+)" align="center"  ?valign="top">', r.text)
        gallery_title = re.sub(r'[-\s]+', "_", gallery_title)

        def prepare_images_url(image_id: str) -> ImageItem:
            url = f"https://www.imagefap.com/photo/{image_id}"
            r =  requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            try:
                name = re.findall(r'<title>([a-zA-Z0-9_-]+)[.jpg|.JPG|.jpeg|.GIF|.gif|.PNG|.png]+ Porn Pic', r.text)[0]
            except:
                name = ""
            matched = re.search(r'<script type="application/ld\+json">(.*?)</script>', r.text, flags=re.S)
            info = json.loads(matched.group(1).strip())
            image = ImageItem(image_id, name, info["contentUrl"], int(info["width"]), int(info["height"]))
            return image

        images = []
        for image_id in images_id:
            im = prepare_images_url(image_id)
            images.append(im)
            print(im)
            time.sleep(1.1)
        return gallery_title, images_id
        # url = parse.urljoin(ROOT, os.path.join("pictures", f"{str(gid)}/"))
        # params = {"view": "2"}
        # r = requests.get(url, params=params, headers=HEADERS, timeout=3)
        # assert r.status_code == 200, f"Status code {r.status_code} error"
        # html = etree.HTML(r.text)
        # title = html.xpath("//*[@id='menubar']/table/tr[1]/td[2]/table/tr/td[1]/b[1]/font/text()")[0]
        # table = html.xpath("//div[@class='expp-container']/form/table")[0]
        # pid = table.xpath("tr/td/table/tr[1]/td/a/@name")
        # name = table.xpath("tr/td/table/tr[2]/td/font[2]/i/text()")

        # assert len(pid) == len(name)
        # total = len(pid)
        # current = 0
        # src = []

        # while current<total:
        #     url = parse.urljoin(ROOT, os.path.join("photo", f"{str(pid[current])}/"))
        #     params = {
        #         "gid": str(gid),
        #         "idx": str(current),
        #         "partial": "true"
        #     }
        #     r = requests.get(url, headers=HEADERS, timeout=3)
        #     html = etree.HTML(r.text)
        #     href = html.xpath("//div[@id='navigation']/ul/li/a/@href")
        #     current += len(href)
        #     src.extend(href)
        #     print(f"Images url fetching [{current}/{total}]...")
        # assert len(src) == total

        # return list(zip(pid, src, name))

    def parse(self, url: str) -> Dict:
        if url.startswith("https://imagefap.com"):
            p = urlparse(url)
            gid = p.path.split("/")[-1]
        elif url.isdigit():
            gid = url
        else:
            raise ValueError(f'Invalid url: {url}. It should be full url or comic id.')
        metadata = self._fetch(gid)
        # data['url'] = url
        return metadata


class Pictoa(AbstractParser):
    def __init__(self):
        super().__init__('Pictoa')
        self.indexed = False

    def _fetch(self, gid: str) -> dict:
        return
        # r = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=5)
        # assert r.status_code == 200
        # r.encoding = r.apparent_encoding
        # soup = BeautifulSoup(r.text, "html.parser")
        # album = soup.find("div", attrs={"id": "album"})
        # title = album.div.h1.text.strip()
        # wrapper = album.findAll("a", attrs={"class": "gallery-link"})
        # res = {
        #     "title": title,
        #     "data": [{'name': a.img.attrs['alt'], 'url': a.img.attrs['data-lazy-src']} for a in wrapper]
        # }
        # return res

    def parse(self, url: str) -> dict:
        return
        # if url.startswith("https://imagefap.com"):
        #     p = urlparse(url)
        #     gid = p.path.split("/")[-1]
        # else:
        #     raise ValueError(f'Invalid url: {url}. It should be full url or comic id.')
        # data = self._fetch(gid)
        # data['url'] = url
        # return data


class ParserFactory:
    @staticmethod
    def create(website):
        p = urlparse(website)
        domain = p.netloc
        domain = domain.strip().replace(' ', '').lower()
        if "caitlin" in domain:
            p = Caitlin()
        elif "zipai" in domain:
            p = Zipai()
        elif "motherless" in domain:
            p = Motherless()
        elif "imagefap" in domain:
            p = ImageFap()
        else:
            raise ValueError(f'Unknown website {website}')
        return p

if __name__ == '__main__':
    # app = Caitlin()
    # app.parse('aaaa')
    # app.parse('https://caitlin.top/index.php')
    # data = app.parse('https://caitlin.top/index.php?route=comic/readOnline&comic_id=697352')
    # print(data)

    # app = Zipai()
    # data = app.parse('https://www.99zipai.com/selfies/202010/110590.html')
    # print(data)

    # app = Motherless()
    # data = app.parse('https://motherless.com/GI6E08B47')
    # print(data)

    pass
