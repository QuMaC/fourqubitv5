# Contact academia.harimohan@gmail.com for any questions/bugs/suggestions
from pathlib import Path
from datetime import datetime
from termcolor import cprint

def get_save_dir(root_folder: str | Path) -> Path:
    """
    Return the date-based directory for today: root_folder / yy / mm / dd.
    Creates the directory if it does not exist.

    Parameters
    ----------
    root_folder : str or Path
        Root folder for all experiment saves.

    Returns
    -------
    Path
        Path to the directory for today's saves.
    """
    root = Path(root_folder)
    now = datetime.now()
    save_dir = root / now.strftime("%y") / now.strftime("%m") / now.strftime("%d")
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


def get_timestamp_24h() -> str:
    """Return current time as HH_MM_SS (24h, to the second)."""
    return datetime.now().strftime("%H_%M_%S")


def get_save_path(
    root_folder: str | Path = None,
    suffix: str = "Untitled_experiment",
    extension: str = "",
    *,
    timestamp: str | None = None,
) -> Path:
    """
    Return a full save path: root_folder / yy / mm / dd / (suffix)_HH_MM_SS[.extension].
    Creates the date directory if it does not exist.

    Parameters
    ----------
    root_folder : str or Path
        Root folder for experiment saves.
    suffix : str, optional
        Experiment or file name (e.g. "resonator_spec", "Ramsey_q1").
        If empty, the filename is just the timestamp.
    extension : str, optional
        File extension without the dot (e.g. "csv", "npz"). Omit for no extension.
    timestamp : str, optional
        Override time part (e.g. "14_30_00"). If None, uses current time.

    Returns
    -------
    Path
        Full path suitable for saving a file. Parent directory is created.

    Examples
    --------
    >>> p = get_save_path("/data", suffix="res_spec", extension="csv")
    >>> # e.g. /data/25/02/13/res_spec_14_30_22.csv
    >>> p = get_save_path("/data", suffix="Rabi_q1")
    >>> # e.g. /data/25/02/13/Rabi_q1_14_30_22
    """
    #warn if root_folder is not provided
    if root_folder is None:
        cprint("Warning: Root folder not provided. Using default folder", "yellow")
        root_folder = r"D:\QUA\Master_Scripts\fourqubitv5_Hari\HM\data_misc"
    root = Path(root_folder)
    now = datetime.now()
    save_dir = root / now.strftime("%y") / now.strftime("%m") / now.strftime("%d")
    save_dir.mkdir(parents=True, exist_ok=True)

    time_str = timestamp if timestamp is not None else get_timestamp_24h()
    if suffix:
        base_name = f"{suffix}_{time_str}"
    else:
        base_name = time_str

    if extension:
        base_name = f"{base_name}.{extension.lstrip('.')}"

    return save_dir / base_name


def get_save_paths_for_run(
    root_folder: str | Path,
    suffix: str = "",
    extension: str = "",
) -> tuple[Path, Path, str]:
    """
    Return directory, full path, and a single timestamp for a run.
    Use this when saving multiple files in the same run so they share the same
    HH_MM_SS and directory.

    Parameters
    ----------
    root_folder : str or Path
        Root folder for experiment saves.
    suffix : str, optional
        Base name for the file (e.g. experiment name).
    extension : str, optional
        File extension without the dot.

    Returns
    -------
    tuple[Path, Path, str]
        (save_dir, full_save_path, timestamp_str)
        You can build more paths as: save_dir / f"{other_suffix}_{timestamp_str}.csv"
    """
    ts = get_timestamp_24h()
    save_dir = get_save_dir(root_folder)
    full_path = get_save_path(root_folder, suffix=suffix, extension=extension, timestamp=ts)
    return save_dir, full_path, ts


def timestamp_to_datetime(timestamp: str) -> datetime:
    return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")




def save_json(data, file_path):
    """Checks if the object contains any numpy arrays and converts them to lists before saving as JSON."""
    import json
    import numpy as np

    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.generic,)):
            return obj.item()
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [convert(v) for v in obj]
        return obj

    data_converted = convert(data)
    with open(file_path, 'w') as f:
        json.dump(data_converted, f, indent=4)