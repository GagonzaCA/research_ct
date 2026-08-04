"""
Módulo de transformaciones para el Análisis de Datos Composicionales (CoDa).
Implementa la transformación Centered Log-Ratio (CLR) para superar el efecto de cierre.
"""

import numpy as np


class Clr_Transformer:
    """
    Clase para aplicar transformaciones proporcionales y CLR a datos XRF.
    """

    @staticmethod
    def Apply_Clr_Transform(Valid_Pixels: np.ndarray, Delta: float = 1e-4) -> np.ndarray:
        """
        Convierte intensidades brutas en proporciones, aplica reemplazo de ceros
        y proyecta al espacio euclidiano mediante la transformación CLR.

        Args:
            Valid_Pixels (np.ndarray): Matriz (N_validos, n) con intensidades brutas >= 0.
            Delta (float, optional): Constante pequeña para el reemplazo de ceros.
                Por defecto 1e-4.

        Returns:
            np.ndarray: Matriz (N_validos, n) transformada en el espacio real (R^n).
        """
        # 1. Normalización (cierre) a proporciones (sum = 1)
        Row_Sums = np.sum(Valid_Pixels, axis=1, keepdims=True)
        Proportions = Valid_Pixels / Row_Sums

        # 2. Reemplazo multiplicativo de ceros simple
        Proportions[Proportions == 0.0] = Delta

        # Renormalización tras imputar ceros
        Proportions = Proportions / np.sum(Proportions, axis=1, keepdims=True)

        # 3. Transformación Centered Log-Ratio (CLR)
        # log( x_i / geometric_mean(x) )
        Log_Proportions = np.log(Proportions)
        Geometric_Mean = np.mean(Log_Proportions, axis=1, keepdims=True)
        Clr_Data = Log_Proportions - Geometric_Mean

        return Clr_Data
