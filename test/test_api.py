import sys
sys.path.append("/workspaces/meetslut")
from meetslut.api import download

def test_download():
    import csv
    urls = []
    names = []
    with open("/workspaces/meetslut/test/images.csv", 'r', newline='') as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)    # skip header
        for row in reader:
            url, name = row
            urls.append(url)
            names.append(name)
    download(urls, names, folder="./ssd", auto_increment=True, num_threads=1)

if __name__ == "__main__":
    test_download()