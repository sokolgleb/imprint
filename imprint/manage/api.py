import click
import uvicorn

from .cli import cli


@cli.command(help="run API")
@click.option("-h", "--host", default="0.0.0.0", help="Host")
@click.option("-p", "--port", default=8000, help="Port")
def run_api(host: str, port: int) -> None:
    from ..api.app import create_app

    uvicorn.run(create_app(), host=host, port=port, log_config=None)
