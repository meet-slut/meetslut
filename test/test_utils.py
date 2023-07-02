import sys
sys.path.append("/workspaces/meetslut")
import pytest

from meetslut.utils import retry, amend_suffix, rename

@pytest.mark.skip(reason="skip")
def test_retry():
    import random
    @retry(max_retries=3, interval=0.1, ignore=True)
    def func(x):
        if random.random() < x:
            raise ValueError
        return True
    ret = func(1)
    assert ret is None
    ret = func(0.0)
    assert ret is True

@pytest.mark.skip(reason="skip")
def test_amend_suffix():
    assert amend_suffix('.gif') == '.gif'
    assert amend_suffix('.jiff') == '.jpg'
    assert amend_suffix('.jpeg') == '.jpeg'

# @pytest.mark.skip(reason="skip")
def test_rename():
    assert rename(["s/4567.jpg", "image/sample.jpg", "image/sample.jpg", "x/avc.png"]) == ['4567.jpg', 'sample.jpg', 'sample3.jpg', 'avc.png']
    assert rename(["s/4567.jpg", "image/sample.jpg", "image/sample.jpg", "x/avc.png"], auto_increment=True) == ['1.jpg', '2.jpg', '3.jpg', '4.png']
    assert rename(["s/4567.jpg", "image/sample.jpg"], ['a', 'b']) == ['a.jpg', 'b.jpg']