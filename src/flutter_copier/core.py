import zipfile

from rich import print as rprint
from rich.prompt import Prompt
from pathlib import Path

VARIATIONS_MAP = {
    "@2x": "2.0x",
    "@3x": "3.0x",
}


def copy_assets_from_path(
    zip_file: Path, *, name: str | None = None, delete_src: bool = True
):
    main_dir = zip_file.parent
    unzip_folder = main_dir / zip_file.stem

    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(unzip_folder)

        files = list(unzip_folder.glob("*"))
        default_size = min(files, key=lambda x: len(x.name))
        extension = default_size.suffix

        # Check if all files are the default or variations, check the suffix is valid and defined in VARIANTIONS_MAP
        for file in files:
            if file == default_size:
                continue

            if file.suffix != extension:
                raise ValueError(f"File {file.name} has an invalid extension")

            if (
                file.name[len(default_size.stem) : -len(file.suffix)]
                not in VARIATIONS_MAP
            ):
                raise ValueError(f"File {file.name} has an invalid variation")

        # Move each file to the assets folder, if the asset folder does not exist, create it

        copy_name: str

        if name is None:
            copy_name = Prompt.ask(
                f"Detected [yellow]{default_size.stem}[/yellow] as the default, please enter the asset name: ",
                default=default_size.stem,
            )
        else:
            copy_name = name

        for file in files:
            asset_path: Path

            if file == default_size:
                asset_path = main_dir
            else:
                asset_path = (
                    main_dir
                    / VARIATIONS_MAP[
                        file.name[len(default_size.stem) : -len(file.suffix)]
                    ]
                )

            rprint(
                f"Copying [yellow]{file.name}[/yellow] to [cyan]{asset_path / copy_name}{extension}[/cyan]"
            )
            
            if not asset_path.exists():
                asset_path.mkdir()
            
            file.rename(asset_path / f"{copy_name}{extension}")

    except zipfile.BadZipFile:
        raise ValueError("Invalid zip file")
    except Exception as e:
        raise e
    finally:
        # Delete unzip folder and its content
        for file in unzip_folder.iterdir():
            file.unlink()
        unzip_folder.rmdir()
        
        if delete_src:
            zip_file.unlink()
