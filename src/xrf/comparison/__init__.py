"""
Comparison module for grouping and analyzing XRF pages by structural category.
"""

from .category_registry import Category_Registry
from .category_signatures import Category_Signature_Aggregator
from .spatial_comparison import Category_Spatial_Comparator
from .rarity_scoring import Rarity_Scorer

__all__ = [
    "Category_Registry",
    "Category_Signature_Aggregator",
    "Category_Spatial_Comparator",
    "Rarity_Scorer",
]
