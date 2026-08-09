"""
Module aggregating per-page leaf signatures into per-category signatures.
"""

from typing import Dict

import numpy as np

from xrf.signatures.leaf_signature import Leaf_Signature_Extractor


class Category_Signature_Aggregator:
    """Aggregates per-page leaf signatures into per-category signatures.

    Reuses the same weighted-average logic as
    Leaf_Signature_Extractor.Compute_Weighted_Book_Signature, applied per
    category group instead of over the whole book.
    """

    @staticmethod
    def Aggregate_By_Category(
        Page_Signatures: Dict[str, np.ndarray],
        Page_Categories: Dict[str, str],
    ) -> Dict[str, np.ndarray]:
        """Compute the mean abundance vector for each structural category.

        Args:
            Page_Signatures: Mapping of page id to its leaf signature
                (abundance vector) as produced by
                Leaf_Signature_Extractor.Compute_Abundances.
            Page_Categories: Mapping of page id to its structural category
                tag.

        Returns:
            Dict[str, np.ndarray]: {category: mean_abundance_vector}.

        Raises:
            ValueError: If a page in Page_Categories has no matching entry
                in Page_Signatures.
        """
        Grouped = Category_Signature_Aggregator._Group_Signatures_By_Category(
            Page_Signatures, Page_Categories
        )

        Category_Means: Dict[str, np.ndarray] = {}
        for Category, Signatures in Grouped.items():
            Signature_Matrix = np.stack(Signatures, axis=0)
            Uniform_Weights = np.ones(Signature_Matrix.shape[0])
            Category_Means[Category] = Leaf_Signature_Extractor.Compute_Weighted_Book_Signature(
                Signature_Matrix, Uniform_Weights
            )

        return Category_Means

    @staticmethod
    def Compute_Category_Spread(
        Page_Signatures: Dict[str, np.ndarray],
        Page_Categories: Dict[str, str],
    ) -> Dict[str, np.ndarray]:
        """Compute the per-class MAD vector for each structural category.

        The robust spread measure used both for plot error bars and for
        Rarity_Scorer.

        Args:
            Page_Signatures: Mapping of page id to its leaf signature
                (abundance vector).
            Page_Categories: Mapping of page id to its structural category
                tag.

        Returns:
            Dict[str, np.ndarray]: {category: per_class_mad_vector}.

        Raises:
            ValueError: If a page in Page_Categories has no matching entry
                in Page_Signatures.
        """
        Grouped = Category_Signature_Aggregator._Group_Signatures_By_Category(
            Page_Signatures, Page_Categories
        )

        Category_Spread: Dict[str, np.ndarray] = {}
        for Category, Signatures in Grouped.items():
            Signature_Matrix = np.stack(Signatures, axis=0)
            Median = np.median(Signature_Matrix, axis=0)
            Category_Spread[Category] = np.median(
                np.abs(Signature_Matrix - Median), axis=0
            )

        return Category_Spread

    @staticmethod
    def _Group_Signatures_By_Category(
        Page_Signatures: Dict[str, np.ndarray],
        Page_Categories: Dict[str, str],
    ) -> Dict[str, list]:
        """Group page signatures by their structural category tag.

        Args:
            Page_Signatures: Mapping of page id to its leaf signature.
            Page_Categories: Mapping of page id to its structural category
                tag.

        Returns:
            Dict[str, list]: {category: [signature, ...]}.

        Raises:
            ValueError: If a page in Page_Categories has no matching entry
                in Page_Signatures.
        """
        Grouped: Dict[str, list] = {}
        for Page_Id, Category in Page_Categories.items():
            if Page_Id not in Page_Signatures:
                raise ValueError(
                    f"Page '{Page_Id}' listed in Page_Categories has no "
                    "matching entry in Page_Signatures."
                )
            Grouped.setdefault(Category, []).append(Page_Signatures[Page_Id])

        return Grouped
