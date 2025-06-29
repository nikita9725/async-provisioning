import click
from service_a.run import run_service as run_service_a
from service_b.run import run_service as run_service_b
from worker.run import run_service as run_worker
from task_status_refresher.run import run_service as run_task_status_refresher


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


@cli.command()
def task_status_refresher() -> None:
    """Запуск сервиса, который обновляет статусы 'зависших задач'"""
    run_task_status_refresher()


if __name__ == "__main__":
    cli()
