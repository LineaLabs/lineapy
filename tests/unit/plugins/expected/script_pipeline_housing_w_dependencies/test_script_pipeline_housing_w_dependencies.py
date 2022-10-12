import os
import pickle
import unittest
import warnings
from pathlib import Path
from typing import Callable

from script_pipeline_housing_w_dependencies_module import (
    get_assets_for_artifact_y_and_downstream,
    get_p_value,
    get_y,
)


def safe_load_pickle(
    path_to_file: Path,
    alt_val_func: Callable = lambda: FileNotFoundError,
    save_alt_val: bool = False,
):
    """
    Load the specified pickle file if it exists.
    If not, use the provided function to generate and return
    an alternative value (the desired execution should be wrapped
    inside a lambda function to delay actual execution until needed).
    """
    if os.path.exists(path_to_file):
        with open(path_to_file, "rb") as fp:
            file_value = pickle.load(fp)
        return file_value
    else:
        alt_value = alt_val_func()
        if save_alt_val is True:
            # Store value to avoid recompute across test cases
            with open(path_to_file, "wb") as fp:
                pickle.dump(alt_value, fp)
        return alt_value


class TestScriptPipelineHousingWDependencies(unittest.TestCase):
    art_pkl_dir: Path

    def setUp(self) -> None:
        # Add any processes to execute before each test in this class
        pass

    def tearDown(self) -> None:
        # Add any processes to execute after each test in this class
        pass

    @classmethod
    def setUpClass(cls) -> None:
        # Specify location where sample output files are stored for comparison
        cls.art_pkl_dir = Path(__file__).parent / "sample_output"

        # Add any processes to execute once before all tests in this class run
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        # Delete pickle files for intermediate (non-artifact) values
        for intermediate_output_name in [
            "assets_for_artifact_y_and_downstream"
        ]:
            path_to_file = cls.art_pkl_dir / f"{intermediate_output_name}.pkl"
            if os.path.exists(path_to_file):
                os.remove(path_to_file)

        # Add any processes to execute once after all tests in this class run
        pass

    def test_get_assets_for_artifact_y_and_downstream(self) -> None:
        """
        NOTE: The code below is provided as scaffolding/template.
        Please adapt it to your specific testing context.
        [TODO: ADD LINK TO WEB DOCUMENTATION].
        """
        # Prepare function input (adapt as needed)
        pass

        # Generate function output (adapt as needed)
        sample_output_generated = get_assets_for_artifact_y_and_downstream()

        # Perform tests (add/adapt as needed)
        sample_output_expected = safe_load_pickle(
            path_to_file=(
                self.art_pkl_dir / "assets_for_artifact_y_and_downstream.pkl"
            ),
            alt_val_func=lambda: FileNotFoundError,
        )
        try:
            self.assertEqual(sample_output_generated, sample_output_expected)
        except Exception:
            warnings.warn(
                "Test failed, but this may be due to our limited templating. "
                "Please adapt the test as needed."
            )

    def test_get_y(self) -> None:
        """
        NOTE: The code below is provided as scaffolding/template.
        Please adapt it to your specific testing context.
        [TODO: ADD LINK TO WEB DOCUMENTATION].
        """
        # Prepare function input (adapt as needed)
        assets = safe_load_pickle(
            path_to_file=(
                self.art_pkl_dir / "assets_for_artifact_y_and_downstream.pkl"
            ),
            alt_val_func=lambda: get_assets_for_artifact_y_and_downstream(),
            save_alt_val=True,
        )

        # Generate function output (adapt as needed)
        sample_output_generated = get_y(assets)

        # Perform tests (add/adapt as needed)
        sample_output_expected = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "y.pkl"),
            alt_val_func=lambda: FileNotFoundError,
        )
        try:
            self.assertEqual(sample_output_generated, sample_output_expected)
        except Exception:
            warnings.warn(
                "Test failed, but this may be due to our limited templating. "
                "Please adapt the test as needed."
            )

    def test_get_p_value(self) -> None:
        """
        NOTE: The code below is provided as scaffolding/template.
        Please adapt it to your specific testing context.
        [TODO: ADD LINK TO WEB DOCUMENTATION].
        """
        # Prepare function input (adapt as needed)
        assets = safe_load_pickle(
            path_to_file=(
                self.art_pkl_dir / "assets_for_artifact_y_and_downstream.pkl"
            ),
            alt_val_func=lambda: get_assets_for_artifact_y_and_downstream(),
            save_alt_val=True,
        )
        y = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "y.pkl"),
            alt_val_func=lambda: get_y(assets),
            save_alt_val=True,
        )

        # Generate function output (adapt as needed)
        sample_output_generated = get_p_value(assets, y)

        # Perform tests (add/adapt as needed)
        sample_output_expected = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "p_value.pkl"),
            alt_val_func=lambda: FileNotFoundError,
        )
        try:
            self.assertEqual(sample_output_generated, sample_output_expected)
        except Exception:
            warnings.warn(
                "Test failed, but this may be due to our limited templating. "
                "Please adapt the test as needed."
            )
