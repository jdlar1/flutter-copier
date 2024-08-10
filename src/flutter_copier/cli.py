from pathlib import Path
from importlib.metadata import version

import typer
from watchfiles import watch, Change

from flutter_copier.core import copy_assets_from_path

app = typer.Typer(
    name="Flutter Copier",
    help="Copy assets from a Figma downloaded folder to a Flutter project",
    no_args_is_help=True,
)


@app.command()
def run(
    file: Path = typer.Argument(exists=True, file_okay=True),
):
    if file.suffix != ".zip":
        raise typer.BadParameter("File must be a zip file")

    copy_assets_from_path(file, delete_src=True)


@app.command(name="watch")
def watch_command(
    file: Path = typer.Argument(exists=True, file_okay=False),
):
    for changes in watch(file):
        for change in changes:
            if change[0] is not Change.added:
                continue

            path = Path(change[1])

            if path.suffix != ".zip":
                continue

            copy_assets_from_path(path, delete_src=True)


def version_callback(value: bool):
    if value:
        print(f"Manage FastAPI version: {version('flutter_copier')}")
        raise


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit",
    ),
): ...


if __name__ == "__main__":
    app()
