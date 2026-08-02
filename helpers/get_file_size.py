from pathlib import Path


def get_file_size(file_path: Path):
    if file_path.exists():
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        return file_size_mb
    else:
        return 0
