"""
Module flagging pages whose composition deviates unusually from their
structural category, as a ranking/triage heuristic for human review.
"""

from typing import Dict, List, Tuple

import numpy as np

from xrf.config import Xrf_Comparison_Config
from xrf.comparison.category_signatures import Category_Signature_Aggregator


class Rarity_Scorer:
    """Flags pages whose composition deviates unusually from their category.

    This is a ranking/triage heuristic, not a statistical test — small-N
    category groups don't support real significance claims. Docstrings on
    the public methods repeat this caveat explicitly so it isn't lost
    downstream.
    """

    @staticmethod
    def Compute_Robust_Deviation(
        Page_Signature: np.ndarray,
        Category_Median: np.ndarray,
        Category_Mad: np.ndarray,
    ) -> np.ndarray:
        """Compute the per-class robust z-score of a page against its category.

        Formula: 0.6745 * (x - median) / MAD. This is a triage heuristic
        for human review, not a hypothesis test.

        Args:
            Page_Signature: Leaf signature (abundance vector) of the page
                being scored.
            Category_Median: Per-class median abundance vector for the
                page's structural category.
            Category_Mad: Per-class MAD vector for the page's structural
                category.

        Returns:
            np.ndarray: Per-class robust z-score vector.

        Raises:
            RuntimeError: If any Category_Mad entry is exactly 0 (which
                happens when every page in a tiny category has an identical
                value for that class) — guarded explicitly rather than
                silently producing inf/nan, matching this project's
                existing guard-clause error-handling style.
        """
        if np.any(Category_Mad == 0):
            raise RuntimeError(
                "Category_Mad contains a zero entry; robust z-score is "
                "undefined (would produce inf/nan). This happens when "
                "every page in a tiny category shares an identical value "
                "for that class."
            )

        return 0.6745 * (Page_Signature - Category_Median) / Category_Mad

    @staticmethod
    def Rank_Pages_By_Rarity(
        Page_Signatures: Dict[str, np.ndarray],
        Page_Categories: Dict[str, str],
        Config: Xrf_Comparison_Config,
    ) -> List[Tuple[str, float, bool]]:
        """Rank pages by their maximum absolute deviation from their category.

        This is a ranking/triage heuristic, not a hypothesis test — see the
        class docstring.

        Args:
            Page_Signatures: Mapping of page id to its leaf signature
                (abundance vector).
            Page_Categories: Mapping of page id to its structural category
                tag.
            Config: Comparison configuration holding Rarity_Mad_Threshold.

        Returns:
            List[Tuple[str, float, bool]]: [(page_id, max_abs_deviation,
            is_flagged), ...] sorted descending by deviation. is_flagged is
            True when the deviation exceeds Config.Rarity_Mad_Threshold.

        Raises:
            ValueError: If a page in Page_Categories has no matching entry
                in Page_Signatures.
            RuntimeError: If a category's MAD vector has a zero entry for
                any class present in a page's signature — see
                Compute_Robust_Deviation.
        """
        Category_Medians = Rarity_Scorer._Compute_Category_Medians(
            Page_Signatures, Page_Categories
        )
        Category_Mads = Category_Signature_Aggregator.Compute_Category_Spread(
            Page_Signatures, Page_Categories
        )

        Rankings: List[Tuple[str, float, bool]] = []
        for Page_Id, Category in Page_Categories.items():
            if Page_Id not in Page_Signatures:
                raise ValueError(
                    f"Page '{Page_Id}' listed in Page_Categories has no "
                    "matching entry in Page_Signatures."
                )

            Deviation = Rarity_Scorer.Compute_Robust_Deviation(
                Page_Signatures[Page_Id],
                Category_Medians[Category],
                Category_Mads[Category],
            )
            Max_Abs_Deviation = float(np.max(np.abs(Deviation)))
            Is_Flagged = Max_Abs_Deviation > Config.Rarity_Mad_Threshold
            Rankings.append((Page_Id, Max_Abs_Deviation, Is_Flagged))

        Rankings.sort(key=lambda Entry: Entry[1], reverse=True)
        return Rankings

    @staticmethod
    def _Compute_Category_Medians(
        Page_Signatures: Dict[str, np.ndarray],
        Page_Categories: Dict[str, str],
    ) -> Dict[str, np.ndarray]:
        """Compute the per-class median abundance vector for each category.

        Args:
            Page_Signatures: Mapping of page id to its leaf signature.
            Page_Categories: Mapping of page id to its structural category
                tag.

        Returns:
            Dict[str, np.ndarray]: {category: per_class_median_vector}.

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

        return {
            Category: np.median(np.stack(Signatures, axis=0), axis=0)
            for Category, Signatures in Grouped.items()
        }
