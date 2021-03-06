# Integration tests

This folder contains a number of "integration" tests, meaning tests of running 
files from third party sources unchanged, as a way to check Lineapy's validity 
against real world use cases.

## What the tests do

All of the tests so far of the same form, so they are all parameters of the 
same test function `test_slice.py::test_slice`.

In each the test:

1. Creates a conda environment for the project we are testing against in `envs/<virtualenv name>`, 
if that directory does not exist. Inside this environment, we install a 
development build of lineapy as well as any requirements needed to run the tests.
2. Load the hand written ground truth slice of the file from the `slices/<test id>.py` 
directory. If one does not exist, it will create one from the source file. Also 
prettify the file and save it back, to remove comments unnecessary spaces.
3. Run the ground truth slice, to make sure that it is accurate.
4. Run the lineapy CLI on the source file (in `sources/`) to create a slice of it.
5. Verifies that that slice is equal to the snapshot (we make a snapshot of the 
slice, even if its "wrong", so that we can see in the the repo what the current 
slice is, and we can see how it changes over time, even if it is never fully "correct"). 
Note that a copy of the entire file will be created when it's run the first time,
and you can manually correct the slices, which will _not_ be overwritten in 
future runs.
6. Assert that the created slice is equal to the ground truth slice, after prettifying each.

## Running tests

The tests have the `integration` mark so that they are not run by default. So 
to run them use `-m integration`.

Note that when you run the tests for the first time in your environment, it might
take a long time (e.g., > 5 min), but future runs will be faster.

Also, all the tests which have failing slices, are currently marked as xfailed, 
so will not raise errors by default. If you do want to see the errors, you can 
use `--runxfail` and use `-vv` to print out the full diff.

Most tests do succeed in producing a slice, but the slice just happens to be 
wrong, so they are marked with `raises=AssertionError`. This is so that pytest 
knows they should only fail there, not at an earlier step. However,
some tests don't succeed in even producing a slice, and those are just marked 
`xfail` without a reason.

So if you wanted to say run the `numpy-mnist` test to see how the written slice
differs from the generated slice, you could do:

```bash
$ pytest 'tests/integration/test_slice.py::test_slice[numpy_mnist]' --runxfail -vv -m 'integration'
================================================================================== test session starts ===================================================================================
platform darwin -- Python 3.9.7, pytest-6.2.5, py-1.11.0, pluggy-1.0.0 -- /opt/homebrew/Caskroom/miniconda/base/envs/lineapy/bin/python
cachedir: .pytest_cache
rootdir: /Users/saul/p/lineapy, configfile: pytest.ini
plugins: xdist-2.5.0, forked-1.4.0, shutil-1.7.0, nbval-0.9.6, anyio-3.4.0, syrupy-1.4.5, virtualenv-1.7.0, cov-3.0.0
collected 1 item

tests/integration/test_slice.py::test_slice[numpy-mnist] FAILED                                                                                                                    [100%]

======================================================================================== FAILURES ========================================================================================
________________________________________________________________________________ test_slice[numpy-mnist] _________________________________________________________________________________

venv = 'numpy-tutorials', source_file = 'numpy-tutorials/content/tutorial-deep-learning-on-mnist.md', slice_value = '(weights_1, weights_2)', sliced_file = 'numpy_mnist_weights.py'
request = <FixtureRequest for <Function test_slice[numpy-mnist]>>

    @mark.integration
    @mark.parametrize("venv,source_file,slice_value,sliced_file", PARAMS)
    def test_slice(
        venv: str, source_file: str, slice_value: str, sliced_file: str, request
    ) -> None:
        with use_virtualenv(venv):
            sliced_code = slice_file(
                source_file, slice_value, request.config.getoption("--visualize")
            )

            # Verify running manually sliced version works
            sliced_path = INTEGRATION_DIR / "slices" / sliced_file
            subprocess.run(["python", sliced_path], check=True)
            desired_slice = sliced_path.read_text()

            # Compare normalized sliced
>           assert normalize_source(sliced_code) == normalize_source(desired_slice)
E           assert ([...]) == ([...])
E               data_sources = {'training_images': 'train-images-idx3-ubyte.gz',
E                   'test_images': 't10k-images-idx3-ubyte.gz', 'training_labels':
E                   'train-labels-idx1-ubyte.gz', 'test_labels': 't10k-labels-idx1-ubyte.gz'}
E             - headers = {'User-Agent':
E             -     'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}
E             - request_opts = {'headers': headers, 'params': {'raw': 'true'}}
E               import os
E             - import requests
E               data_dir = '../_data'
E             - os.makedirs(data_dir, exist_ok=True)
E             - base_url = 'https://github.com/rossbar/numpy-tutorial-data-mirror/blob/main/'
E               for fname in data_sources.values():
E                   fpath = os.path.join(data_dir, fname)
E                   if not os.path.exists(fpath):
E             +         print('Downloading file: ' + fname)
E                       resp = requests.get(base_url + fname, stream=True, **request_opts)
E                       resp.raise_for_status()
E                       with open(fpath, 'wb') as fh:
E                           for chunk in resp.iter_content(chunk_size=128):
E                               fh.write(chunk)
[...]

/Users/saul/p/lineapy/tests/integration/test_slice.py:119: AssertionError
-------------------------------------------------------------------------------- snapshot report summary ---------------------------------------------------------------------------------

================================================================================ short test summary info =================================================================================
FAILED tests/integration/test_slice.py::test_slice[numpy-mnist] - assert ("data_sources = {'training_images': 'train-images-idx3-ubyte.gz',\n"\n "    'test_images': 't10k-images-idx3-...
=================================================================================== 1 failed in 22.12s ===================================================================================
```

## Adding new tests

So to add a new test, you have to:

1. Add the sources to the `sources` subfolder. Often, this can be done [using `git submodule add <git url> sources/<desired name>`](https://git-scm.com/book/en/v2/Git-Tools-Submodules#_starting_submodules).
2. Specify the virtualenv requirements to run the tests in the `VIRTUAL_ENVS` dictionary in `test_slice.py`.
3. Add a param for this test in `PARAMS` list in `test_slice.py`.
4. Run the test with `pytest 'tests/integration/test_slice.py::test_slice[<id>]' -m 'integration'` to create a slice file for it
5. Manually edit the slice file to make it accurate.
6. Re-run the test. If it passes, that's great! If not, add an `xfail` with a `reason=` to describe why. If it only failed on comparing
   the slices, add a `raises=AssertionError` to document that the test passed up until the assert.
