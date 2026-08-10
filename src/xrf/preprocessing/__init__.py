"""
Preprocessing pipeline for raw XRF instrument data.
Converts proprietary Bruker .bcf hypercubes into standardized elemental TIFFs.
"""

from .bcf_extractor import Bcf_Element_Extractor

__all__ = ["Bcf_Element_Extractor"]