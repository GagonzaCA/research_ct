"""
Módulo para la carga de datos multiespectrales de Fluorescencia de Rayos X (XRF).
Gestiona la lectura de archivos TIFF y el cálculo de la máscara de intensidad total T(p).
"""

import numpy as np
import imageio.v3 as iio
from typing import Union, List, Tuple
from pathlib import Path

Path_Like = Union[str, Path]


class Xrf_Loader:
    """
    Clase utilitaria para cargar y preprocesar el cubo de datos elementales XRF.
    """

    @staticmethod
    def Load_Element_Stack(File_Paths: List[Path_Like], Dtype: str = "float64") -> np.ndarray:
        """
        Carga una lista de archivos TIFF correspondientes a cada canal químico y los apila.

        Args:
            File_Paths (List[Path_Like]): Lista de rutas a los archivos TIFF elementales.
            Dtype (str, optional): Precisión del array resultante. Por defecto "float64".

        Returns:
            np.ndarray: Cubo de datos 3D de dimensiones (M, N, n) donde n es el
                número de elementos químicos.

        Raises:
            ValueError: Si la lista de rutas está vacía o las imágenes tienen distintas dimensiones.
        """
        if not File_Paths:
            raise ValueError("La lista de archivos File_Paths no puede estar vacía.")

        Layers = []
        for Path_Str in File_Paths:
            Image = iio.imread(Path_Str)
            Layers.append(Image.astype(Dtype, copy=False))

        # Apilar a lo largo del último eje (M, N, n)
        Stack = np.stack(Layers, axis=-1)
        return Stack

    @staticmethod
    def Compute_Intensity_Mask(
        Stack: np.ndarray, Tau_Noise: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula la intensidad total acumulada T(p) y extrae los píxeles válidos.

        Args:
            Stack (np.ndarray): Cubo multicanal (M, N, n).
            Tau_Noise (float): Umbral mínimo de intensidad tau_ruido.

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                - Mask (np.ndarray): Matriz booleana 2D (M, N) con los píxeles válidos.
                - Valid_Pixels (np.ndarray): Matriz 2D aplanada de dimensiones (N_validos, n).
        """
        # Intensidad total T(p) sumando todos los canales
        Total_Intensity = np.sum(Stack, axis=-1)

        # Máscara binaria
        Mask = Total_Intensity >= Tau_Noise

        # Indexación para extraer solo vectores válidos (aplanamiento)
        Valid_Pixels = Stack[Mask]

        return Mask, Valid_Pixels
