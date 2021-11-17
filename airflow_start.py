#!/usr/bin/env python
"""
Starts the airflow process in parallel.

Similar to `airflow standalone` except it doesn't set the port of the
web server explicitly, so it can be overridden by the environment variable,
and also doesn't try to create the DB.

Start this from `make airflow_start` so that env variables are properly set
and the airflow home is built beforehand
"""

import asyncio
import atexit
from distutils.log import debug

# Start all tasks
# If any die, exit
# On exit, kill all subprocesses


async def start_task(*args: str) -> None:
    command = " ".join(args)
    print(f"Starting {command}")
    sub = await asyncio.create_subprocess_exec(*args)
    # Kill subprocesses when done
    atexit.register(sub.kill)
    # If it exits, exit our program with an error
    await sub.wait()
    print(f"{args} stopped, exiting")
    exit(1)


async def main():
    tasks = [
        # Run these commands in parallel
        # Similar to https://github.com/apache/airflow/blob/7cda7d4b5e413925bf639976e77ebf2442b4bff9/airflow/cli/commands/standalone_command.py#L66-L83
        start_task("airflow", cmd)
        for cmd in ("webserver", "triggerer", "scheduler")
    ]
    await asyncio.gather(*tasks)


asyncio.run(main(), debug=True)
