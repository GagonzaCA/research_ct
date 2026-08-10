"""
Module for loading multiespectral X-Ray Fluorescence (XRF) data.
Manages TIFF file reading and total intensity mask T(p) computation.
"""

import json
import numpy as np
import imageio.v3 as iio
from typing import Union, List, Tuple
from pathlib import Path

Path_Like = Union[str, Path]


class Xrf_Loader:
    """
    Utility class to load and preprocess the elemental XRF data cube.
    """

    @staticmethod
    def Load_Element_Stack(File_Paths: List[Path_Like], Dtype: str = "float64") -> np.ndarray:
        """
        Loads a list of TIFF files corresponding to each chemical channel and stacks them.

        Args:
            File_Paths (List[Path_Like]): List of paths to elemental TIFF files.
            Dtype (str, optional): Precision of the resulting array. Defaults to "float64".

        Returns:
            np.ndarray: 3D data cube of shape (M, N, n) where n is the
                number of chemical elements.

        Raises:
            ValueError: If the path list is empty or the images have different dimensions.
        """
        if not File_Paths:
            raise ValueError("The File_Paths list cannot be empty.")

        Layers = []
        for Path_Str in File_Paths:
            Image = iio.imread(Path_Str)
            Layers.append(Image.astype(Dtype, copy=False))

        # Stack along the last axis (M, N, n)
        Stack = np.stack(Layers, axis=-1)
        return Stack

    @staticmethod
    def Compute_Intensity_Mask(
        Stack: np.ndarray, Tau_Noise: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes the accumulated total intensity T(p) and extracts valid pixels.

        Args:
            Stack (np.ndarray): Multichannel cube (M, N, n).
            Tau_Noise (float): Minimum intensity threshold tau_noise.

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                - Mask (np.ndarray): 2D boolean array (M, N) with valid pixels.
                - Valid_Pixels (np.ndarray): Flattened 2D array of shape (N_valid, n).
        """
        # Total intensity T(p) by summing all channels
        Total_Intensity = np.sum(Stack, axis=-1)

        # Binary mask
        Mask = Total_Intensity >= Tau_Noise

        # Index to extract only valid vectors (flattening)
        Valid_Pixels = Stack[Mask]

        return Mask, Valid_Pixels


def Update_Page_Metadata(Meta_Path: Path_Like, **Fields) -> None:
    """Merge new fields into an existing page_NNN_meta.json file.

    Args:
        Meta_Path: Path to the page's meta.json file.
        **Fields: Key/value pairs to merge into the existing JSON object.
            Existing keys are overwritten; all other keys are preserved.

    Raises:
        FileNotFoundError: If Meta_Path does not exist — this function
            updates existing metadata, it does not create a page record
            from scratch.
    """
    Meta_Path = Path(Meta_Path)
    if not Meta_Path.exists():
        raise FileNotFoundError(
            f"Meta_Path {Meta_Path} does not exist. Update_Page_Metadata only "
            "updates existing page metadata records."
        )

    with open(Meta_Path, "r", encoding="utf-8") as Meta_File:
        Metadata = json.load(Meta_File)

    Metadata.update(Fields)

    with open(Meta_Path, "w", encoding="utf-8") as Meta_File:
        json.dump(Metadata, Meta_File, indent=2)

    print(f"[Xrf_Loader] updated metadata fields {list(Fields.keys())} in {Meta_Path}")
