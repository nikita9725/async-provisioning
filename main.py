import click
from service_a.run import run_service as run_service_a


@click.group()
def cli():
    """CLI-хаб проекта."""


@cli.command()
@click.option("--port", default=8000, type=int, help="HTTP-порт сервиса")
def service_a(port: int) -> None:
    """Запуск Service A."""
    run_service_a(port)


if __name__ == "__main__":
    cli()
