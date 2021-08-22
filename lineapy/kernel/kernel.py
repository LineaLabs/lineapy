from lineapy.transformer.transformer import Transformer
from ipykernel.kernelbase import Kernel


class LineaKernel(Kernel):
    implementation = "Linea"
    """
    TODO: it looks like we might need to support async as well.
    """

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
