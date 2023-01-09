# Testing a Generated Pipeline

When building a pipeline, LineaPy transforms the user's original code into modularized functions
where extraneous operations are removed. With such changes, the user may want to ensure that the
transformed code is valid and reliable before actually using it. To support this, LineaPy's pipeline
API provides an optional `generate_test` argument (default set to `False`).

## Creating Pipeline Test

To create tests for a pipeline, set `generate_test=True`, like so:

```python hl_lines="7"
lineapy.to_pipeline(
    pipeline_name="iris_pipeline",
    artifacts=["iris_preprocessed", "iris_model"],
    dependencies={"iris_model": {"iris_preprocessed"}},
    output_dir="~/airflow/dags/",
    framework="AIRFLOW",
    generate_test=True,
)
```

Running this will produce, along with usual pipeline files, an additional file
for pipeline testing (`test_<pipeline_name>.py` where `<pipeline_name>` is
`iris_pipeline` in the above example), which may look as follows:

```python title="/Users/username/airflow/dags/test_iris_pipeline.py"
import os
import pickle
import unittest
import warnings
from pathlib import Path
from typing import Callable

from iris_pipeline_module import get_iris_model, get_iris_preprocessed

[...]

class TestIrisPipeline(unittest.TestCase):

    [...]

    def test_get_iris_preprocessed(self) -> None:
        """
        NOTE: The code below is provided as scaffold/template.
        Please adapt it to your specific testing context.
        """
        # Prepare function input (adapt as needed)
        pass

        # Generate function output (adapt as needed)
        sample_output_generated = get_iris_preprocessed()

        # Perform tests (add/adapt as needed)
        sample_output_expected = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "iris_preprocessed.pkl"),
            alt_val_func=lambda: FileNotFoundError,
        )
        try:
            self.assertEqual(sample_output_generated, sample_output_expected)
        except Exception:
            warnings.warn(
                "Test failed, but this may be due to our limited templating. "
                "Please adapt the test as needed."
            )

    def test_get_iris_model(self) -> None:
        """
        NOTE: The code below is provided as scaffold/template.
        Please adapt it to your specific testing context.
        """
        # Prepare function input (adapt as needed)
        df = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "iris_preprocessed.pkl"),
            alt_val_func=lambda: get_iris_preprocessed(),
            save_alt_val=True,
        )

        # Generate function output (adapt as needed)
        sample_output_generated = get_iris_model(df)

        # Perform tests (add/adapt as needed)
        sample_output_expected = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "iris_model.pkl"),
            alt_val_func=lambda: FileNotFoundError,
        )
        try:
            self.assertEqual(sample_output_generated, sample_output_expected)
        except Exception:
            warnings.warn(
                "Test failed, but this may be due to our limited templating. "
                "Please adapt the test as needed."
            )
```

As shown, the file contains test methods (e.g., `TestIrisPipeline.test_get_iris_preprocessed()`) that
each examine validity of the corresponding function in the module file (e.g., `get_iris_preprocessed()`).
Specifically, each test method attempts to check whether running the target function generates the same
output (i.e., artifact value such as pre-processed data) as the original one saved in the artifact store
(which gets copied over to a new local subfolder, e.g., `~/airflow/dags/sample_output/`
in this case, during pipeline generation).

??? question "What does `safe_load_pickle()` do?"

    `safe_load_pickle()` is a helper function (defined in the same testing file) that first tries to
    load the pickle file at `path_to_file` and, if the file does not exist, uses `alt_val_func` to
    re-calculate the value on the fly. If `save_alt_val` is set to `True` (default set to `False`),
    the value produced from `alt_val_func` is saved at `path_to_file` so that it can be used by other
    related test methods without having to re-calculate it again (this "recycling" becomes critical when
    the value involves long computation).

    For `alt_val_func`, the desired execution should be wrapped inside a lambda function to delay actual execution
    until needed (i.e., when `safe_load_pickle()` realizes that the pickle file does not exist and that it needs to
    re-calculate the value).

As indicated by docstrings and comments such as `adapt as needed`, these test methods are provided as
a scaffold/template rather than a final version of pipeline testing. For instance, out of the box, all test methods
rely on `unittest`'s `assertEqual()` to evaluate equality between the generated vs. expected output values
(of the function run), which may not be the right way to perform equality evaluation for certain objects such as
a NumPy array (calling `assertEqual()` on two NumPy arrays would return an array of multiple Boolean values
instead of a single Boolean value). Accordingly, the user is expected to customize the code to suit their own testing
needs/contexts. For example, if the tested function's output is a NumPy array, then the user can replace the templated
`self.assertEqual(sample_output_generated, sample_output_expected)` with the customized `assert all(sample_output_generated == sample_output_expected)`,
which would result in proper equality evaluation.

## Running Pipeline Test

With such limitations in templating, most test methods out of the box are bound to fail. However, to avoid any potential interference
with the user's system, test failures are wrapped inside the `try`-`except` block, which makes all test methods run successfully
without erroring out. Instead, the user is informed of failed test methods via warning messages that ask the user to check the code
and adapt it if needed.

Hence, for the `iris_pipeline` example discussed here, running

```bash
cd ~/airflow/dags/
python -m unittest test_iris_pipeline.TestIrisPipeline
```

would result in

```
/Users/username/airflow/dags/test_iris_pipeline.py:108: UserWarning: Test failed, but this may be due to our limited templating. Please adapt the test as needed.
warnings.warn(
./Users/username/airflow/dags/test_iris_pipeline.py:79: UserWarning: Test failed, but this may be due to our limited templating. Please adapt the test as needed.
warnings.warn(
.
----------------------------------------------------------------------
Ran 2 tests in 0.262s

OK
```

!!! warning

    Tests may involve long compute and/or large storage, so please take care in running them.

## Adapting Pipeline Test

As shown, both test methods "failed" (i.e., warning messages raised) for `iris_pipeline`. This is not surprising because,
again, the scaffold is relying on a naive mode of equality evaluation via `unittest`'s `assertEqual()`, which does not
work for more sophisticated object types such as `pandas.DataFrame` and `sklearn.linear_model.LinearRegression`.
For more proper equality evaluation, we may replace existing `try`-`except` blocks with new `assert` statements,
like so (updates highlighted in yellow):

```python hl_lines="32 54 55" title="/Users/username/airflow/dags/test_iris_pipeline.py"
import os
import pickle
import unittest
import warnings
from pathlib import Path
from typing import Callable

from iris_pipeline_module import get_iris_model, get_iris_preprocessed

[...]

class TestIrisPipeline(unittest.TestCase):

    [...]

    def test_get_iris_preprocessed(self) -> None:
        """
        NOTE: The code below is provided as scaffold/template.
        Please adapt it to your specific testing context.
        """
        # Prepare function input (adapt as needed)
        pass

        # Generate function output (adapt as needed)
        sample_output_generated = get_iris_preprocessed()

        # Perform tests (add/adapt as needed)
        sample_output_expected = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "iris_preprocessed.pkl"),
            alt_val_func=lambda: FileNotFoundError,
        )
        assert sample_output_generated.equals(sample_output_expected)

    def test_get_iris_model(self) -> None:
        """
        NOTE: The code below is provided as scaffold/template.
        Please adapt it to your specific testing context.
        """
        # Prepare function input (adapt as needed)
        df = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "iris_preprocessed.pkl"),
            alt_val_func=lambda: get_iris_preprocessed(),
            save_alt_val=True,
        )

        # Generate function output (adapt as needed)
        sample_output_generated = get_iris_model(df)

        # Perform tests (add/adapt as needed)
        sample_output_expected = safe_load_pickle(
            path_to_file=(self.art_pkl_dir / "iris_model.pkl"),
            alt_val_func=lambda: FileNotFoundError,
        )
        assert sample_output_generated.intercept_ == sample_output_expected.intercept_
        assert all(sample_output_generated.coef_ == sample_output_expected.coef_)
```

With these changes, running the test would result in success without any warning messages raised:

```
..
----------------------------------------------------------------------
Ran 2 tests in 0.103s

OK
```

Note that the user is free to use their own input and (expected) output values to suit their testing needs.
For instance, with the example above, say the user happens to have new pre-processed data stored as a CSV file,
along with the corresponding model's parameter estimates recorded. Then, the user may further customize testing of
`get_iris_model()` as the following (newer updates highlighted in yellow):

```python hl_lines="8 9 25 31 32" title="/Users/username/airflow/dags/test_iris_pipeline.py"
import os
import pickle
import unittest
import warnings
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from iris_pipeline_module import get_iris_model, get_iris_preprocessed

[...]

class TestIrisPipeline(unittest.TestCase):

    [...]

    def test_get_iris_model(self) -> None:
        """
        NOTE: The code below is provided as scaffold/template.
        Please adapt it to your specific testing context.
        """
        # Prepare function input (adapt as needed)
        df = pd.read_csv("some_path_or_url/new_iris_preprocessed.csv")

        # Generate function output (adapt as needed)
        sample_output_generated = get_iris_model(df)

        # Perform tests (add/adapt as needed)
        assert round(sample_output_generated.intercept_, 2) == 3.24
        assert all(np.round(sample_output_generated.coef_, 2) == [0.78, -1.5, -1.84])
```

!!! tip

    In adapting the testing scaffold/template, we can go beyond equality evaluation. For instance, if the tested function outputs
    a model, we can check whether the model behaves "reasonably" by feeding it with particular input values and observing whether
    it returns output values within a certain range. This type of testing is especially valuable for models involving inherent stochasticity,
    where the same procedure does not necessarily guarantee exactly identical results.
