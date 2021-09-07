from lineapy.utils import CaseNotHandledError
from typing import Any
import sys

from lineapy.data.types import DataAssetType


def get_data_asset_type(val: Any) -> DataAssetType:
    """
    A little hacky. Trying to avoid building an dependency on the external libraries.
    Just going to cehck if they are already imported, if they are, then we can reference them. Though it might get really weird with our execution scoping.
    TODO
    - We need to more gracefully handle cases that we do not recognize
    """
    if isinstance(val, int) or isinstance(val, float):
        return DataAssetType.Number
    if isinstance(val, str):
        return DataAssetType.Str
    if isinstance(val, list):
        return DataAssetType.List
    if "matplotlib" in sys.modules:
        from matplotlib.figure import Figure

        if isinstance(val, Figure):
            return DataAssetType.MatplotlibFig
    if "numpy" in sys.modules:
        import numpy

        if isinstance(val, numpy.ndarray):
            return DataAssetType.NumpyArray
    if "pandas" in sys.modules:
        import pandas  # this import should be a no-op

        if isinstance(val, pandas.DataFrame):
            return DataAssetType.PandasDataFrame
        if isinstance(val, pandas.Series):
            return DataAssetType.PandasSeries

    raise CaseNotHandledError(f"Do not know the type of {val}, type {type(val)}")
