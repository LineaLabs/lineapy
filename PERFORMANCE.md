# Performance Profiling

We have had luck using the [py-spy](https://github.com/benfred/py-spy) tool,
which runs your Python script in a separate process and samples it, to
profile our tests to get a rough sense of how long things take:

```bash
# Run with sudo so it can inspect the subprocess
sudo py-spy record \
    # Save as speedscope so we can load in the browser
    --format speedscope \
    # Group by function name, instead of line number
    --function \
    # Increase the sampling rate from 100 to 200 times per second
    -r 200  -- pytest tests/
```

After creating your trace, you can load it [in
Speedscope](https://www.speedscope.app/).

In this example, we are inspecting calls to `transform`.
We see that it cumulatively takes up 12% of total time and that most of the
time inside of it is spent visiting imports, as well as committing to the DB:

<img width="2560" alt="Screen Shot 2021-10-12 at 2 29 10 PM" src="https://user-images.githubusercontent.com/1186124/137037002-18f29bd8-db02-4924-9855-5f3db9d2d0ee.png">
