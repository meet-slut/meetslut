import sys
sys.path.append("/workspaces/meetslut")
# import pytest
from datetime import datetime
from meetslut.config import GET_CFG
from meetslut.download import amend_suffix
from meetslut.webparser import ParserFactory
from meetslut.download import download

def test_amend_suffix():
    assert amend_suffix('.gif') == '.gif'
    assert amend_suffix('.jiff') == '.jpg'

def test_factory():
    for url in [
        'https://caitlin.top/home',
        'https://www.99zipai.com/selfies',
        'https://motherless.com/'
    ]:
        p = ParserFactory.create(url)
        assert p
