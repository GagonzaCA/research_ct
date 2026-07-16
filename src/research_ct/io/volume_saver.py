"""Memory-efficient volume I/O with lazy loading and chunked streaming.

All load functions default to memmap (lazy) -- no data enters RAM until
explicitly materialized via ``np.array(...)``, slicing, or iteration.
This prevents 24 GB probability arrays and 5 GB processed volumes from
exhausting 32 GB RAM on Windows, where ``del`` alone is insufficient.
"""

import os
import gc
import weakref
import numpy as np
from pathlib import Path
from typing import Union, Optional, Tuple, Iterator, Generator

Path_Like = Union[str, Path]

# ---------------------------------------------------------------------------
# Internal registry: keeps .npz archives alive while lazy memmap views exist
# ---------------------------------------------------------------------------
# numpy.ndarray has no __dict__, so we cannot attach arbitrary attributes.
# Instead we use a module-level dict keyed by array id.  Finalizers registered
# via weakref ensure cleanup when the array is garbage collected.
_npz_registry: "dict[int, object]" = {}


def _register_npz(array: np.ndarray, archive: object) -> None:
    """Bind an .npz archive to an array so it stays open while the array lives."""
    _npz_registry[id(array)] = archive
    # When the array is collected, close the archive automatically.
    weakref.finalize(array, _close_npz_by_id, id(array))


def _close_npz_by_id(array_id: int) -> None:
    """Close and remove the archive for *array_id*."""
    archive = _npz_registry.pop(array_id, None)
    if archive is not None:
        archive.close()


def _close_npz(array: np.ndarray) -> None:
    """Explicitly close the .npz archive backing *array*."""
    _close_npz_by_id(id(array))


def Save_As_Numpy(
    Volume: np.ndarray,
    File_Path: Path_Like,
) -> Path:
    """Save volume as compressed .npz file.

    Args:
        Volume: 3D array.
        File_Path: Output path with .npz extension.
    """
    File_Path = Path(File_Path)
    File_Path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(File_Path, volume=Volume)
    print(f"[Save_As_Numpy] Saved -> {File_Path}")
    return File_Path


# ---------------------------------------------------------------------------
# Core loader -- lazy by default, dual .npy / .npz
# ---------------------------------------------------------------------------

def Load_From_Numpy(
    File_Path: Path_Like,
    *,
    lazy: bool = True,
    key: str = "volume",
    z_slice: Optional[Union[slice, Tuple[int, Optional[int]]]] = None,
) -> np.ndarray:
    """Load a volume from .npz or .npy with memory-mapped (lazy) access.

    By default the returned array is a **memmap** -- no data is read from
    disk until you index into it.  Use ``lazy=False`` or ``z_slice`` to
    materialize a concrete array in RAM.

    Args:
        File_Path: Path to ``.npz`` or ``.npy`` file.
        lazy: If True (default), return a memmap / lazy view.  If False,
            materialize the full array into RAM immediately.
        key: Array key inside the ``.npz`` archive (ignored for ``.npy``).
            Defaults to ``"volume"``.
        z_slice: Optional Z-axis range to load as a **concrete** array.
            Accepts ``slice(start, stop)`` or ``(start, stop)``.
            When provided, the result is always materialized regardless
            of ``lazy``.

    Returns:
        - With ``lazy=True`` and no ``z_slice``: a memmap-backed array
          (``.npy``) or memmap view into the ``.npz`` archive.  Shape
          is read from the header without touching pixel data.
        - With ``lazy=False``: full concrete ``np.ndarray``.
        - With ``z_slice``: concrete slice ``(Nz, H, W, ...)``.
    """
    File_Path = Path(File_Path)
    ext = File_Path.suffix.lower()

    if ext == ".npz":
        # np.load with mmap_mode='r' on .npz opens an NpzFile whose
        # internal arrays are backed by the mmap -- no data read yet.
        archive = np.load(File_Path, mmap_mode="r")
        try:
            array = archive[key]
        except KeyError:
            available = list(archive.keys())
            raise KeyError(
                f"Key {key!r} not found in {File_Path.name}. "
                f"Available keys: {available}"
            )
        # Register the archive so it stays alive as long as the array does.
        _register_npz(array, archive)

    elif ext == ".npy":
        # np.load on .npy with mmap_mode returns a memmap directly.
        array = np.load(File_Path, mmap_mode="r" if lazy else None)

    else:
        raise ValueError(
            f"Unsupported extension {ext!r}. Expected .npz or .npy."
        )

    # ---- Z-slice materialization ------------------------------------------
    if z_slice is not None:
        if isinstance(z_slice, tuple):
            z_slice = slice(*z_slice)
        # copy=True: array[z_slice] may be a memmap view into the .npz;
        # we must detach before closing the archive below.
        result = np.array(array[z_slice], dtype=array.dtype, copy=True)
        _close_npz(array)
        print(
            f"[Load_From_Numpy] Loaded z-slice {z_slice} -> "
            f"{result.shape}  ({result.nbytes / 1e9:.2f} GB)"
        )
        return result

    # ---- Full materialization ---------------------------------------------
    if not lazy:
        result = np.array(array, copy=True)
        _close_npz(array)
        print(
            f"[Load_From_Numpy] Loaded (materialized): {result.shape}  "
            f"({result.nbytes / 1e9:.2f} GB)"
        )
        return result

    # ---- Lazy (memmap) ----------------------------------------------------
    print(
        f"[Load_From_Numpy] Loaded (lazy): {array.shape}  "
        f"({array.nbytes / 1e9:.2f} GB on disk)"
    )
    return array


# ---------------------------------------------------------------------------
# Chunked / streaming helpers
# ---------------------------------------------------------------------------

def Load_From_Numpy_Chunked(
    File_Path: Path_Like,
    chunk_size: int,
    *,
    axis: int = 0,
    key: str = "volume",
    dtype: Optional[np.dtype] = None,
    gc_every: int = 10,
) -> Generator[np.ndarray, None, None]:
    """Yield concrete, contiguous chunks along *axis* without loading the
    full volume into RAM.

    Each chunk is a writable ``np.ndarray`` in C order.  The underlying
    memmap is discarded after each yield so Windows releases the mapping.

    Args:
        File_Path: ``.npz`` or ``.npy`` path.
        chunk_size: Number of slices (or elements) per chunk along *axis*.
        axis: Axis to chunk along (0 = Z for 3D volumes).
        key: Array key inside ``.npz`` (ignored for ``.npy``).
        dtype: Optional cast dtype (e.g. ``np.float32``).  If None, the
            on-disk dtype is preserved.
        gc_every: Call ``gc.collect()`` every N chunks to keep Windows
            resident-set size under control.

    Yields:
        ``np.ndarray`` of shape ``(chunk_size, ...)`` (last chunk may be
        smaller).
    """
    data = Load_From_Numpy(File_Path, lazy=True, key=key)
    total = data.shape[axis]

    for start in range(0, total, chunk_size):
        end = min(start + chunk_size, total)
        idx = tuple(
            slice(start, end) if i == axis else slice(None)
            for i in range(data.ndim)
        )
        chunk = np.array(data[idx], dtype=dtype or data.dtype, copy=True,
                         order="C")

        yield chunk

        del chunk
        if ((start // chunk_size) + 1) % gc_every == 0:
            gc.collect()

    _close_npz(data)
    del data
    gc.collect()


def Load_From_Numpy_Slab(
    File_Path: Path_Like,
    z_start: int,
    z_stop: int,
    *,
    key: str = "volume",
    dtype: Optional[np.dtype] = None,
) -> np.ndarray:
    """Convenience wrapper: load a concrete Z-slab ``[z_start, z_stop)``.

    Equivalent to ``Load_From_Numpy(..., z_slice=(z_start, z_stop))``
    with an optional dtype override.
    """
    slab = Load_From_Numpy(File_Path, z_slice=slice(z_start, z_stop), key=key)
    if dtype is not None and slab.dtype != dtype:
        slab = slab.astype(dtype, copy=False)
    return slab