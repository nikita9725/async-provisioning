import click
from service_a.run import run_service as run_service_a
from service_b.run import run_service as run_service_b


@click.group()
def cli():
    """CLI-хаб проекта."""


@cli.command()
@click.option("--port", default=8000, type=int, help="HTTP-порт сервиса")
def service_a(port: int) -> None:
    """Запуск Service A."""
    run_service_a(port)


@cli.command()
@click.option("--port", default=8001, type=int, help="HTTP-порт сервиса")
def service_b(port: int) -> None:
    """Запуск Service B."""
    run_service_b(port)


@cli.command()
def worker() -> None:
    """Запуск consumer worker."""
    run_worker()


if __name__ == "__main__":
    cli()
