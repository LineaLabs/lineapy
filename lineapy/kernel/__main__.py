import sys

if sys.path[0] == "":
    del sys.path[0]

from ipykernel import kernelapp as app
from lineapy.kernel import LineaKernel

app.launch_new_instance(kernel_class=LineaKernel)
