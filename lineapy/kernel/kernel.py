# import asyncio
import os
import json
import sys
import inspect
from ipykernel.ipkernel import IPythonKernel
from lineapy.transformer.transformer import Transformer


def get_kernel_json():
    """Get the kernel json for the kernel."""
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "kernel.json")) as fid:
        data = json.load(fid)
    data["argv"][0] = sys.executable
    return data


from lineapy import __version__


class LineaKernel(IPythonKernel):
    app_name = "linea_kernel"
    implementation = "kernel"
    implementation_version = __version__
    language = "python"
    banner = "Linea kernel - super charging data science"

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
        print("running kernel main")  # FIXME delete
        self.transformer = Transformer()

    def init_metadata(self, parent):
        """
        Don't actually change the metadata; we just want to get the cell id
        out of the execution request.
        """
        cell_id = parent.get("metadata", {}).get("cellId", None)
        if cell_id is not None:
            self.transformer.set_active_cell(cell_id)
        return super().init_metadata(parent)

    # copying from nbsafety
    if inspect.iscoroutinefunction(IPythonKernel.do_execute):
        raise NotImplementedError
        # async def do_execute(
        #     self,
        #     code,
        #     silent,
        #     store_history=False,
        #     user_expressions=None,
        #     allow_stdin=False,
        # ):
        #     super_ = super()

        #     async def _run_cell_func(cell):
        #         return await super_.do_execute(
        #             cell, silent, store_history, user_expressions, allow_stdin
        #         )

        #     if silent:
        #         # then it's probably a control message; don't run through nbsafety
        #         return await _run_cell_func(code)
        #     else:
        #         return await _run_cell_func(code)  # FIXME
        #         # bs().safe_execute(code, True, _run_cell_func)

    else:
        print("We are in synchronous!")

        def do_execute(
            self,
            code,
            silent,
            store_history=False,
            user_expressions=None,
            allow_stdin=False,
        ):
            super_ = super()

            def _run_cell_func(cell):
                return super_.do_execute(
                    cell, silent, store_history, user_expressions, allow_stdin
                )

            linea_transformed_code = self.transformer.transform(code)
            linea_transformed_code
            return _run_cell_func(linea_transformed_code)

            # below are some reference code if we ever want to support async.
            # return next(
            #     iter(
            #         asyncio.get_event_loop().run_until_complete(
            #             asyncio.wait([_run_cell_func(code)])
            #         )[0]
            #     )
            # ).result()


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    print("Launching Linea Kernel")  # FIXME delete
    IPKernelApp.launch_instance(kernel_class=LineaKernel)
