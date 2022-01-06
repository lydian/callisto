#!/usr/bin/env python
import sys

import click
from more_click import host_option
from more_click import port_option
from more_click import debug_option
from more_click import with_gunicorn_option
from more_click import workers_option
from more_click import run_app


@click.group()
def cli():
    pass


@cli.command("start")
@click.option(
    "--config",
    envvar="CALLISTO_CONFIG",
    type=click.Path(exists=True),
    help="config file",
)
@host_option
@port_option
@with_gunicorn_option
@workers_option
@debug_option
def start(
    config: str, host: str, port: str, with_gunicorn: bool, workers: int, debug: bool
) -> None:

    from callisto.app import configure_app

    run_app(
        app=configure_app(config),
        with_gunicorn=with_gunicorn,
        host=host,
        port=port,
        workers=workers,
        debug=debug,
    )


@cli.command("start-dev")
@click.option(
    "--config",
    envvar="CALLISTO_CONFIG",
    type=click.Path(exists=True),
    help="config file",
)
@host_option
@port_option
def start_dev(config, host, port):
    import subprocess
    from functools import partial

    run = partial(subprocess.Popen, stdout=sys.stdout, stderr=sys.stderr)
    p0 = run(["npm", "run", "watch"], cwd="front")
    p1 = run(["venv/bin/moto_server", "-p3000"])
    p2 = run(
        [
            "venv/bin/python",
            "-c",
            "from tests.utils.create_s3 import create_files; create_files()",
        ]
    )

    args = ["--config", config or "tests/fixtures/config.py", "--debug"]
    if host:
        args.extend(["--host", host])
    if port:
        args.extend(["--port", str(port)])

    p3 = run(
        ["venv/bin/python", __file__, "start"] + args, env={"FLASK_ENV": "development"}
    )
    ps = [p0, p1, p3]
    try:
        while True:
            if any(p.poll() is not None for p in ps):
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        for p in ps + [p2]:
            click.echo(f"stop {p}")
            p.terminate()
        while True:
            if all(p.poll() is not None for p in ps):
                break


if __name__ == "__main__":
    cli()
