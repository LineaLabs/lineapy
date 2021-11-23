import os

from lineapy.config import linea_folder


def test_linea_folder_creation():
    # i wonder if this breaks other tests... meh
    os.chdir("/tmp")
    # everything in /tmp should be ephemeral. so clearing this out should be A-ok.
    recreate = False
    if os.path.exists("./.linea"):
        os.rmdir("./.linea")
        recreate = True

    assert os.path.exists("./.linea") is False
    # ba dam boom... this should create our little folder
    linea_folder()
    # does not raise exception yaay
    assert os.path.exists("./.linea") is True
    # clean up - if .linea folder existed in /tmp, keep this new, clean one otherwise remove our test folder
    if not recreate:
        os.rmdir("./.linea")
