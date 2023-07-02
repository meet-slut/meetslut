import sys
sys.path.append("/workspaces/meetslut")

import pytest
from meetslut.parser import Caitlin, ImageFap

@pytest.mark.skip(reason="skip")
def test_Caitlin():
    app = Caitlin()
    print(app)
    # metadata = app.parse("https://caitlin.top/index.php?route=comic/article&comic_id=663706")
    metadata = app.parse("663706")
    print(metadata)


def test_ImageFap():
    app = ImageFap()
    # metadata = app.parse("https://caitlin.top/index.php?route=comic/article&comic_id=663706")
    metadata = app.parse("11026085")
    print(metadata)