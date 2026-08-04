"""
Módulo para la reconstrucción topológica y extracción de métricas espaciales (CCA).
"""

import numpy as np
from scipy import ndimage
from typing import Dict, Any


class Spatial_Analyzer:
    """Clase para mapear etiquetas a 2D y analizar su morfología."""

    @staticmethod
    def Reconstruct_Class_Map(
        Labels: np.ndarray, Mask: np.ndarray, Fill_Value: int = -1
    ) -> np.ndarray:
        """
        Asigna el vector aplanado de etiquetas de vuelta a la grilla 2D.

        Args:
            Labels (np.ndarray): Etiquetas 1D (N_validos,).
            Mask (np.ndarray): Máscara binaria 2D (M, N).
            Fill_Value (int, optional): Valor para fondo (ruido). Por defecto -1.

        Returns:
            np.ndarray: Mapa de clases 2D de tamaño (M, N).
        """
        Class_Map = np.full(Mask.shape, Fill_Value, dtype=np.int32)
        Class_Map[Mask] = Labels
        return Class_Map

    @staticmethod
    def Extract_Spatial_Descriptors(
        Class_Map: np.ndarray, Target_Class: int, Min_Size: int = 10
    ) -> Dict[str, float]:
        """
        Calcula descriptores de componentes conectadas para una clase.

        Args:
            Class_Map (np.ndarray): Mapa de clases 2D.
            Target_Class (int): Identificador de la clase a analizar.
            Min_Size (int): Tamaño mínimo para considerar una región.

        Returns:
            Dict[str, float]: Diccionario con Num_Regiones y Tamaño_Promedio.
        """
        Binary_Mask = (Class_Map == Target_Class).astype(np.uint8)

        # Conectividad de 8 (matriz 3x3 de unos)
        Structure = np.ones((3, 3), dtype=np.uint8)
        Labeled_Array, Num_Features = ndimage.label(Binary_Mask, structure=Structure)

        Valid_Regions = 0
        Total_Area = 0

        # Filtrar regiones pequeñas
        for Region_Id in range(1, Num_Features + 1):
            Area = np.sum(Labeled_Array == Region_Id)
            if Area >= Min_Size:
                Valid_Regions += 1
                Total_Area += Area

        Avg_Size = Total_Area / Valid_Regions if Valid_Regions > 0 else 0.0

        return {"Num_Regiones": float(Valid_Regions), "Tamano_Promedio": float(Avg_Size)}
