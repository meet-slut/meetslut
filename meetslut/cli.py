"""
The Command Line Interface (CLI) for the downloader
"""
import os, argparse, logging, json


from meetslut.webparser import ParserFactory
from meetslut.download import download

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)-5s] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG)

    logger.addHandler(console)

def main():
    parser = argparse.ArgumentParser(description="A fancy downloader for slut.")
    subparsers = parser.add_subparsers(help='sub-command help')
    image_parser = subparsers.add_parser('image', help='image tool')
    image_parser.add_argument("url", type=str, help="The URL of the resource to be downloaded.")
    image_parser.add_argument(
        "--output", "-o", default=os.getcwd(),
        help=("Destination local file path. If not set, the resource "
                "will be downloaded to the current working directory, with filename "
                "same as the basename of the URL")
    )
    image_parser.set_defaults(func=process_image)


    args = parser.parse_args()

    args.func(args)


def process_image(args):
    url = args.url
    output = args.output
    app = ParserFactory.create(url)
    data = app.parse(url)
    folder = os.path.join(output, data['title'])
    metafile = os.path.join(folder, 'metadata.json')
    # if os.path.exists(metafile):
    #     # save metadata
    #     with open(metafile, 'r', encoding='utf8') as f:
    #         data = json.load(f)
    # else:
    #     # save metadata
    #     with open(metafile, 'w', encoding='utf8') as f:
    #         json.dump(data, f, ensure_ascii=False)
    # save metadata

    download(data['images'], folder, indexed=app.indexed)
    with open(metafile, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)



if __name__ == "__main__":
    setup_logger()
    logging.info("🚀 Start...")
    main()