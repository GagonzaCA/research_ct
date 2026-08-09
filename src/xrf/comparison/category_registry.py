"""
Module owning the structural page-category vocabulary and the read/write
access to the ``structural_*`` fields on page metadata.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from xrf.config import Xrf_Comparison_Config
from xrf.io.xrf_loader import Path_Like, Update_Page_Metadata

_Logger = logging.getLogger(__name__)


class Category_Registry:
    """Static-method utility for structural page-category tags.

    Mirrors the interface style of other XRF classes (Xrf_Loader,
    Clr_Transformer): stateless, static methods, no persisted instance.
    """

    @staticmethod
    def Validate_Category_Tag(Tag: str, Config: Xrf_Comparison_Config) -> None:
        """Validate a category tag against the allowed vocabulary.

        Args:
            Tag: Category label to validate.
            Config: Comparison configuration holding the allowed vocabulary.

        Raises:
            ValueError: If Tag is not in Config.Allowed_Categories.
        """
        if Tag not in Config.Allowed_Categories:
            raise ValueError(
                f"Category tag '{Tag}' is not in the allowed vocabulary "
                f"{Config.Allowed_Categories}."
            )

    @staticmethod
    def Write_Page_Category(
        Meta_Path: Path_Like,
        Category: str,
        Config: Xrf_Comparison_Config,
        Tag_Source: str = "manual",
        Secondary_Categories: Optional[List[str]] = None,
        Notes: Optional[str] = None,
    ) -> None:
        """Validate Category, then persist it into the page metadata.

        Args:
            Meta_Path: Path to the page's meta.json file.
            Category: Primary structural category tag.
            Config: Comparison configuration holding the allowed vocabulary.
            Tag_Source: Either "manual" or "heuristic". Defaults to "manual".
            Secondary_Categories: Optional list of additional category tags
                for pages that do not fit one bucket cleanly.
            Notes: Optional free-text note, read by humans only.

        Raises:
            ValueError: If Category is not in Config.Allowed_Categories.
            FileNotFoundError: If Meta_Path does not exist.
        """
        Category_Registry.Validate_Category_Tag(Category, Config)

        Fields = {
            "structural_category": Category,
            "structural_category_source": Tag_Source,
            "structural_category_secondary": Secondary_Categories or [],
            "structural_category_notes": Notes or "",
        }
        Update_Page_Metadata(Meta_Path, **Fields)

        Page_Id = Path(Meta_Path).stem.replace("_meta", "")
        print(f"[Category_Registry] tagged {Page_Id} as {Category} ({Tag_Source})")

    @staticmethod
    def Load_Page_Category(Meta_Path: Path_Like) -> Optional[str]:
        """Return the structural_category field, or None if not yet tagged.

        Args:
            Meta_Path: Path to the page's meta.json file.

        Returns:
            The primary structural category tag, or None if the page has
            not been tagged yet.

        Raises:
            FileNotFoundError: If Meta_Path does not exist.
        """
        Meta_Path = Path(Meta_Path)
        if not Meta_Path.exists():
            raise FileNotFoundError(f"Meta_Path {Meta_Path} does not exist.")

        with open(Meta_Path, "r", encoding="utf-8") as Meta_File:
            Metadata = json.load(Meta_File)

        return Metadata.get("structural_category")

    @staticmethod
    def List_Tagged_Pages(
        Output_Dir: Path_Like, Config: Optional[Xrf_Comparison_Config] = None
    ) -> Dict[str, List[str]]:
        """Scan page_*_meta.json files and group page ids by category.

        Args:
            Output_Dir: Directory containing page_NNN_meta.json files
                (typically data/xrf/output/processed/).
            Config: Comparison configuration holding the allowed
                vocabulary, used only to flag unexpected tags with a
                warning. Defaults to Xrf_Comparison_Config() if omitted.

        Returns:
            Dict[str, List[str]]: {category: [page_id, ...]}. Pages without
            a structural_category are grouped under "untagged".
        """
        if Config is None:
            Config = Xrf_Comparison_Config()

        Output_Dir = Path(Output_Dir)
        Grouped: Dict[str, List[str]] = {}

        for Meta_Path in sorted(Output_Dir.glob("page_*_meta.json")):
            Page_Id = Meta_Path.stem.replace("_meta", "")
            Category = Category_Registry.Load_Page_Category(Meta_Path)

            if Category is None:
                Category = "untagged"
            elif Category not in Config.Allowed_Categories:
                _Logger.warning(
                    "[Category_Registry] page %s has unexpected category "
                    "'%s' not in Allowed_Categories %s",
                    Page_Id,
                    Category,
                    Config.Allowed_Categories,
                )

            Grouped.setdefault(Category, []).append(Page_Id)

        return Grouped
