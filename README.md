# meetslut
> A fancy command line tool to download slut👠 pictures from internt.

<!-- ![010116-220-C](https://upload-images.jianshu.io/upload_images/13843118-f46b965a1c878a67.png) -->

## 🚀 Support website
> 📢 Checked on 2022.11.05

|Website|Status|Desc|
|---|---|---|
| [Caitlin](https://caitlin.top/)|✔️|comics|
| [zipai](https://99zipai.com/)|✔️|china amateur photos|
| [motherless]()  |✔️|photo|
| [Imagefap]()|❌|photo|
| [pictoa](https://www.pictoa.com/)|⭕️|photo|

✔️ success ❌ failed ⭕️ developing 

❗️ proxy needed for mainland user

## 🔨 Installation
```
python -m venv meetslut
source /ide/meetslut/bin/activate
git clone https://gitee.com/crj1998/meetslut.git
cd meetslut
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
pip install -e .
cd test
python -m unittest test_demo.py
cd ..
chmod +x examples.sh
./examples.sh
```

## 💡 Usage
```bash
meetslut image https://www.99zipai.com/selfies/202010/110590.html -o ./saved
```


## 📑 License

## 👋 Acknowledgement
- https://jinglong233.gitee.io/markdownIcon/
- Tutorial from 📦  [Converting Python Script Into a Command-line Tool](https://betterprogramming.pub/build-your-python-script-into-a-command-line-tool-f0817e7cebda)


## For Developers
parser: input a url, output a dict {"url": ..., "name": ...}

### Test
```
python meetslut/cli.py zipai https://www.99zipai.com/selfies/202010/110590.html -o ~/work/saved
python meetslut/cli.py caitlin 'https://caitlin.top/index.php?route=comic/readOnline&comic_id=697352&host_id=0&page=3&gallery_brightness=100&gallery_contrast=100' -o ~/work/saved

python meetslut/cli.py motherless https://motherless.com/GICB9A5D8?page=2 -o ~/work/saved
```