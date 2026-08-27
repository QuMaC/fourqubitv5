from __future__ import annotations

import shutil
from pathlib import Path

ALLOWED_EXTENSIONS = {".json", ".py", ".ipynb"}
SOURCE_DIR = Path(r"D:\QUA\Master_Scripts\fourqubitv5 (Under Construction)")
DESTINATION_DIR = Path(r"D:\QUA\Master_Scripts\fourqubitv5_export")
DRY_RUN = False


def clone_filtered_tree(source_dir: str | Path, destination_dir: str | Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Recreate source_dir tree inside destination_dir while only copying
    files with allowed extensions.

    Returns
    -------
    tuple[int, int]
        (number_of_directories_created, number_of_files_copied)
    """
    source = Path(source_dir).resolve()
    destination = Path(destination_dir).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source folder does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source}")
    if destination == source or destination.is_relative_to(source):
        raise ValueError("Destination folder cannot be the source folder or a subfolder of the source.")

    dirs_created = 0
    files_copied = 0

    for item in source.rglob("*"):
        rel_path = item.relative_to(source)
        target_path = destination / rel_path

        if item.is_dir():
            if not dry_run:
                target_path.mkdir(parents=True, exist_ok=True)
            dirs_created += 1
            continue

        if item.is_file() and item.suffix.lower() in ALLOWED_EXTENSIONS:
            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_path)
            files_copied += 1

    return dirs_created, files_copied


def main() -> None:
    dirs_created, files_copied = clone_filtered_tree(
        SOURCE_DIR,
        DESTINATION_DIR,
        dry_run=DRY_RUN,
    )
    action = "Would create/copy" if DRY_RUN else "Created/copied"
    print(f"{action}: {dirs_created} directories, {files_copied} files.")


if __name__ == "__main__":
    main()
