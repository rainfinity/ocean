# -*- coding: utf-8 -*-

import click
from cookiecutter.main import cookiecutter  # type: ignore

from port_ocean.cli.commands.main import cli_start, print_logo, console
from port_ocean.cli.utils import cli_root_path


@cli_start.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "--remove-docker-files",
    "remove_docker_files",
    is_flag=True,
    default=False,
    help="Remove Docker files from the generated project. (Used for contributing to Ocean)",
)
def new(path: str, remove_docker_files: bool) -> None:
    """
    Scaffold a new integration in the given PATH.

    PATH: Path to the integration. If not provided, the current directory will be used.
    """
    print_logo()

    console.print(
        "🚢 Unloading cargo... Setting up your integration at the dock.", style="bold"
    )

    result = cookiecutter(
        f"{cli_root_path}/cookiecutter",
        output_dir=path,
        extra_context={
            "remove_docker_files": remove_docker_files,
        },
    )
    name = result.split("/")[-1]

    console.print(
        "\n🌊 Ahoy, Captain! Your project is ready to set sail into the vast ocean of possibilities!",
        style="bold",
    )
    console.print("Here are your next steps:\n", style="bold")
    console.print(
        "⚓️ Install necessary packages: Run [bold][blue]make install[/blue][/bold] to install all required packages for your project.\n"
        f"▶️ [bold][blue]cd {path}/{name} && make install && . .venv/bin/activate[/blue][/bold]\n"
    )
    console.print(
        "⚓️ Set sail with [blue]Ocean[/blue]: Run [bold][blue]ocean sail[/blue] <path_to_integration>[/bold] to run the project using Ocean.\n"
        f"▶️ [bold][blue]ocean sail {path}/{name}[/blue][/bold] \n"
    )
    console.print(
        "⚓️ Smooth sailing with [blue]Make[/blue]: Alternatively, you can run [bold][blue]make run[/blue][/bold] to launch your project using Make. \n"
        f"▶️ [bold][blue]make run {path}/{name}[/blue][/bold]"
    )
