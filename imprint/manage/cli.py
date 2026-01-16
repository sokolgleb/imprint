import click
import uvloop


@click.group()
def cli() -> None:
    uvloop.install()
