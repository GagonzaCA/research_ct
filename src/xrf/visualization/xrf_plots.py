"""
Visualization utilities for category-level XRF page comparison.

All plotting/image-layout functions import matplotlib lazily inside their
bodies, matching this project's convention for optional/heavy visualization
libraries.
"""

from typing import Dict, List

import numpy as np

from xrf.io.xrf_loader import Path_Like


def Plot_Category_Signature_Bars(
    Category_Signatures: Dict[str, np.ndarray],
    Category_Spread: Dict[str, np.ndarray],
    Output_Path: Path_Like,
) -> None:
    """Draw a grouped bar chart of per-class abundance by category.

    One group of bars per category, with MAD-derived error bars.

    Args:
        Category_Signatures: Mapping of category to its mean abundance
            vector, as produced by
            Category_Signature_Aggregator.Aggregate_By_Category.
        Category_Spread: Mapping of category to its per-class MAD vector,
            as produced by
            Category_Signature_Aggregator.Compute_Category_Spread.
        Output_Path: Destination path for the saved figure.

    Raises:
        ValueError: If Category_Signatures is empty, or if a category in
            Category_Signatures has no matching entry in Category_Spread.
    """
    if not Category_Signatures:
        raise ValueError("Category_Signatures cannot be empty.")

    for Category in Category_Signatures:
        if Category not in Category_Spread:
            raise ValueError(
                f"Category '{Category}' has no matching entry in Category_Spread."
            )

    import matplotlib.pyplot as plt

    Categories = list(Category_Signatures.keys())
    Num_Classes = len(next(iter(Category_Signatures.values())))
    Class_Positions = np.arange(Num_Classes)
    Bar_Width = 0.8 / len(Categories)

    Figure, Axis = plt.subplots(figsize=(max(6, Num_Classes * 1.2), 5))

    for Index, Category in enumerate(Categories):
        Offset = (Index - (len(Categories) - 1) / 2) * Bar_Width
        Axis.bar(
            Class_Positions + Offset,
            Category_Signatures[Category],
            width=Bar_Width,
            yerr=Category_Spread[Category],
            capsize=3,
            label=Category,
        )

    Axis.set_xticks(Class_Positions)
    Axis.set_xticklabels([f"class_{K}" for K in range(Num_Classes)])
    Axis.set_ylabel("Mean abundance")
    Axis.set_title("Category signature comparison")
    Axis.legend()

    Figure.tight_layout()
    Figure.savefig(Output_Path)
    plt.close(Figure)
    print(f"[Xrf_Plots] saved category signature bar chart to {Output_Path}")


def Plot_Category_Signature_Radar(
    Category_Signatures: Dict[str, np.ndarray],
    Output_Path: Path_Like,
) -> None:
    """Draw a radar/spider overlay with one line per category.

    Args:
        Category_Signatures: Mapping of category to its mean abundance
            vector, as produced by
            Category_Signature_Aggregator.Aggregate_By_Category.
        Output_Path: Destination path for the saved figure.

    Raises:
        ValueError: If Category_Signatures is empty.
    """
    if not Category_Signatures:
        raise ValueError("Category_Signatures cannot be empty.")

    import matplotlib.pyplot as plt

    Num_Classes = len(next(iter(Category_Signatures.values())))
    Angles = np.linspace(0, 2 * np.pi, Num_Classes, endpoint=False).tolist()
    Angles.append(Angles[0])

    Figure, Axis = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})

    for Category, Signature in Category_Signatures.items():
        Values = list(Signature) + [Signature[0]]
        Axis.plot(Angles, Values, label=Category)
        Axis.fill(Angles, Values, alpha=0.1)

    Axis.set_xticks(Angles[:-1])
    Axis.set_xticklabels([f"class_{K}" for K in range(Num_Classes)])
    Axis.set_title("Category signature radar overlay")
    Axis.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    Figure.tight_layout()
    Figure.savefig(Output_Path)
    plt.close(Figure)
    print(f"[Xrf_Plots] saved category signature radar overlay to {Output_Path}")


def Build_Category_Montage(
    Cluster_Visual_Paths: List[Path_Like],
    Output_Path: Path_Like,
    Grid_Cols: int = 4,
) -> None:
    """Assemble existing cluster visualization PNGs into one grid image.

    Pure layout for visual review — no new computation is performed on the
    underlying images.

    Args:
        Cluster_Visual_Paths: Paths to existing Cluster_k_Visual.png files
            to lay out together.
        Output_Path: Destination path for the saved montage image.
        Grid_Cols: Number of columns in the montage grid. Defaults to 4.

    Raises:
        ValueError: If Cluster_Visual_Paths is empty or Grid_Cols is not
            positive.
    """
    if not Cluster_Visual_Paths:
        raise ValueError("Cluster_Visual_Paths cannot be empty.")
    if Grid_Cols <= 0:
        raise ValueError("Grid_Cols must be a positive integer.")

    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    Num_Images = len(Cluster_Visual_Paths)
    Num_Rows = int(np.ceil(Num_Images / Grid_Cols))

    Figure, Axes = plt.subplots(
        Num_Rows, Grid_Cols, figsize=(Grid_Cols * 3, Num_Rows * 3)
    )
    Axes = np.atleast_1d(Axes).flatten()

    for Axis, Visual_Path in zip(Axes, Cluster_Visual_Paths):
        Image = mpimg.imread(Visual_Path)
        Axis.imshow(Image)
        Axis.axis("off")

    for Axis in Axes[Num_Images:]:
        Axis.axis("off")

    Figure.tight_layout()
    Figure.savefig(Output_Path)
    plt.close(Figure)
    print(f"[Xrf_Plots] saved category montage ({Num_Images} images) to {Output_Path}")
