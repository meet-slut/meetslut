# num of threads for downloading resources
NUM_THREADS = 4
# requests max retry
RETRY = 3
MAX_RETRY = 3
# requests config
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
}
TIMEOUT = 7
GET_CFG = {
    'headers': {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    },
    'proxies': None,
    # 'proxies': {
    #     'http': 'socks5h://127.0.0.1:2801',
    #     'https': 'socks5h://127.0.0.1:2801'
    # },
    'timeout': 5
}
"""
{
    'http': 'socks5h://127.0.0.1:2801',
    'https': 'socks5h://127.0.0.1:2801'
}
"""

ROOT_ZIPAI = "https://99zipai.com"