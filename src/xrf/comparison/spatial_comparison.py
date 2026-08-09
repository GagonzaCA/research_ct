"""
Module aggregating Spatial_Analyzer region descriptors by structural
category.
"""

from typing import Dict

import numpy as np


class Category_Spatial_Comparator:
    """Aggregates Spatial_Analyzer region descriptors by category."""

    @staticmethod
    def Aggregate_Region_Stats(
        Page_Spatial_Descriptors: Dict[str, dict],
        Page_Categories: Dict[str, str],
    ) -> Dict[str, dict]:
        """Aggregate per-page spatial descriptors into per-category stats.

        Groups each page's Spatial_Analyzer.Extract_Spatial_Descriptors()
        output (keyed by compositional class id, with the Spanish keys
        "Num_Regiones" and "Tamano_Promedio") by its structural category,
        and averages them per class.

        Args:
            Page_Spatial_Descriptors: Mapping of page id to a dict of
                {class_k: {"Num_Regiones": float, "Tamano_Promedio": float}},
                matching Spatial_Analyzer.Extract_Spatial_Descriptors's
                return schema.
            Page_Categories: Mapping of page id to its structural category
                tag.

        Returns:
            Dict[str, dict]: {category: {class_k: {mean_region_count,
            mean_region_size}}}.

        Raises:
            ValueError: If a page in Page_Categories has no matching entry
                in Page_Spatial_Descriptors.
        """
        Grouped: Dict[str, list] = {}
        for Page_Id, Category in Page_Categories.items():
            if Page_Id not in Page_Spatial_Descriptors:
                raise ValueError(
                    f"Page '{Page_Id}' listed in Page_Categories has no "
                    "matching entry in Page_Spatial_Descriptors."
                )
            Grouped.setdefault(Category, []).append(
                Page_Spatial_Descriptors[Page_Id]
            )

        Category_Stats: Dict[str, dict] = {}
        for Category, Descriptor_List in Grouped.items():
            Class_Ids = sorted(
                {Class_Id for Descriptors in Descriptor_List for Class_Id in Descriptors}
            )

            Class_Stats = {}
            for Class_Id in Class_Ids:
                Region_Counts = [
                    Descriptors[Class_Id]["Num_Regiones"]
                    for Descriptors in Descriptor_List
                    if Class_Id in Descriptors
                ]
                Region_Sizes = [
                    Descriptors[Class_Id]["Tamano_Promedio"]
                    for Descriptors in Descriptor_List
                    if Class_Id in Descriptors
                ]
                Class_Stats[Class_Id] = {
                    "mean_region_count": float(np.mean(Region_Counts)),
                    "mean_region_size": float(np.mean(Region_Sizes)),
                }

            Category_Stats[Category] = Class_Stats

        return Category_Stats
