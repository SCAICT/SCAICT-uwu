import os
import tempfile
from contextlib import contextmanager


@contextmanager
def safe_open_w(file: str | os.PathLike[str], *, encoding: str | None):
    dirpath, basename = os.path.split(file)

    fd, tmp_path = tempfile.mkstemp(prefix=f"{basename}.tmp_", dir=dirpath)

    try:
        with os.fdopen(fd, "w", encoding=encoding) as tmp_file:
            yield tmp_file

        os.replace(tmp_path, file)

    except Exception:
        os.remove(tmp_path)
        raise


def safe_write(
    file: str | os.PathLike[str],
    data: str,
    encoding: str | None,
):

    with safe_open_w(file, encoding=encoding) as f:
        f.write(data)
