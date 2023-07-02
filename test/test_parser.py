import sys
sys.path.append("/workspaces/meetslut")

from meetslut.parser import Caitlin

def test_Caitlin():
    app = Caitlin()
    print(app)
    # metadata = app.parse("https://caitlin.top/index.php?route=comic/article&comic_id=663706")
    metadata = app.parse("663706")
    print(metadata)