import os
import json
import sys
from ipykernel.kernelbase import Kernel
from lineapy.transformer.transformer import Transformer


def get_kernel_json():
    """Get the kernel json for the kernel."""
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "kernel.json")) as fid:
        data = json.load(fid)
    data["argv"][0] = sys.executable
    return data


class LineaKernel(Kernel):
    app_name = "linea_kernel"
    implementation = "Linea"
    """
    TODO:
    - [] the installation is still not working properly 
    - [] we might need to support async as well.
    """

    kernel_json = get_kernel_json()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # the same class need to persist through multiple execution sessions
        # TODO this assumes that each notebook would have a single kernel; need to verify
        self.transformer = Transformer()

    def do_execute(
        self,
        code,
        silent,
        store_history=False,
        user_expressions=None,
        allow_stdin=False,
    ):
        linea_transformed_code = self.transformer.transform(code)
        super().do_execute(
            linea_transformed_code, silent, store_history, user_expressions, allow_stdin
        )


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=LineaKernel)
