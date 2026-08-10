"""
Bruker BCF hypercube → elemental TIFF extraction.

Loads a .bcf spectrum image, dynamically resolves the correct emission
line for each requested element, applies dual-window Bremsstrahlung
subtraction, and writes one 32-bit float ``_raw.tiff`` per element.
"""

from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
import tifffile

Path_Like = Union[str, Path]

# ── atomic-number lookup independent of library metadata ────────────────────
_ATOMIC_NUMBERS: dict = {
    "H": 1,
    "He": 2,
    "Li": 3,
    "Be": 4,
    "B": 5,
    "C": 6,
    "N": 7,
    "O": 8,
    "F": 9,
    "Ne": 10,
    "Na": 11,
    "Mg": 12,
    "Al": 13,
    "Si": 14,
    "P": 15,
    "S": 16,
    "Cl": 17,
    "Ar": 18,
    "K": 19,
    "Ca": 20,
    "Sc": 21,
    "Ti": 22,
    "V": 23,
    "Cr": 24,
    "Mn": 25,
    "Fe": 26,
    "Co": 27,
    "Ni": 28,
    "Cu": 29,
    "Zn": 30,
    "Ga": 31,
    "Ge": 32,
    "As": 33,
    "Se": 34,
    "Br": 35,
    "Kr": 36,
    "Rb": 37,
    "Sr": 38,
    "Y": 39,
    "Zr": 40,
    "Nb": 41,
    "Mo": 42,
    "Tc": 43,
    "Ru": 44,
    "Rh": 45,
    "Pd": 46,
    "Ag": 47,
    "Cd": 48,
    "In": 49,
    "Sn": 50,
    "Sb": 51,
    "Te": 52,
    "I": 53,
    "Xe": 54,
    "Cs": 55,
    "Ba": 56,
    "La": 57,
    "Ce": 58,
    "Pr": 59,
    "Nd": 60,
    "Pm": 61,
    "Sm": 62,
    "Eu": 63,
    "Gd": 64,
    "Tb": 65,
    "Dy": 66,
    "Ho": 67,
    "Er": 68,
    "Tm": 69,
    "Yb": 70,
    "Lu": 71,
    "Hf": 72,
    "Ta": 73,
    "W": 74,
    "Re": 75,
    "Os": 76,
    "Ir": 77,
    "Pt": 78,
    "Au": 79,
    "Hg": 80,
    "Tl": 81,
    "Pb": 82,
    "Bi": 83,
    "Po": 84,
    "At": 85,
    "Rn": 86,
    "Fr": 87,
    "Ra": 88,
    "Ac": 89,
    "Th": 90,
    "Pa": 91,
    "U": 92,
}


class Bcf_Element_Extractor:
    """Ingests a .bcf hypercube and exports background-subtracted elemental maps.

    For each requested element the extractor:
        1. Resolves the dominant emission line (Kα for Z ≤ 40, Lα otherwise).
        2. Integrates a peak window ± *Peak_Width_Kev*/2 around the line.
        3. Estimates the continuum from two sideband windows offset by
           ± *Bg_Offset_Kev* from the line, each of width *Bg_Width_Kev*.
        4. Subtracts the scaled average sideband from the peak integral
           and clips negative residuals to zero.
        5. Writes the result as a 32-bit TIFF tagged with element
           symbol and line energy.

    Args:
        Cutoff_At_Kv: Detector energy ceiling (keV).
        Peak_Width_Kev: Full width of the integration window (keV).
        Bg_Width_Kev: Full width of each background sideband (keV).
        Bg_Offset_Kev: Distance from line center to sideband center (keV).
    """

    def __init__(
        self,
        Cutoff_At_Kv: float = 40.0,
        Peak_Width_Kev: float = 0.20,
        Bg_Width_Kev: float = 0.10,
        Bg_Offset_Kev: float = 0.25,
    ) -> None:
        self.cutoff_at_kv = Cutoff_At_Kv
        self.peak_width_kev = Peak_Width_Kev
        self.bg_width_kev = Bg_Width_Kev
        self.bg_offset_kev = Bg_Offset_Kev

    # ── public API ──────────────────────────────────────────────────────────

    def Resolve_Emission_Line(self, Element_Input: str) -> Tuple[float, str]:
        """Look up the dominant emission line and its energy for an element.

        Accepts either ``"Fe"`` (auto-selects the principal line) or
        ``"Fe_Ka"`` (forces a specific line).  Elements with Z ≤ 40
        default to Kα; heavier elements default to Lα.

        Args:
            Element_Input: Element symbol optionally extended with an
                underscore-separated line label (e.g. ``"Au_La"``).

        Returns:
            A tuple ``(Energy_Kev, Resolved_Tag)`` where *Resolved_Tag*
            has the form ``"Fe_Ka"``.

        Raises:
            ValueError: If the element symbol is not recognised by the
                ``exspy`` materials database or the requested emission
                line is missing.
        """
        # lazy import — hyperspy/exspy are heavy and slow to load
        import exspy

        if "_" in Element_Input:
            elem_symbol, line_symbol = Element_Input.split("_", 1)
        else:
            elem_symbol = Element_Input
            line_symbol = None

        try:
            elem_obj = getattr(exspy.material.elements, elem_symbol)
        except AttributeError:
            raise ValueError(
                f"Element '{elem_symbol}' not found in the periodic table database."
            )

        if not line_symbol:
            z = _ATOMIC_NUMBERS.get(elem_symbol, 20)
            line_symbol = "Ka" if z <= 40 else "La"

        resolved_tag = f"{elem_symbol}_{line_symbol}"

        xray_lines = None
        if hasattr(elem_obj, "Xray_lines"):
            xray_lines = elem_obj.Xray_lines
        elif hasattr(elem_obj, "Atomic_properties") and hasattr(
            elem_obj.Atomic_properties, "Xray_lines"
        ):
            xray_lines = elem_obj.Atomic_properties.Xray_lines

        if xray_lines is None or line_symbol not in xray_lines:
            raise ValueError(
                f"Emission line '{line_symbol}' not found for element {elem_symbol}."
            )

        line_data = xray_lines[line_symbol]
        try:
            energy_kev = float(line_data["energy (keV)"])
        except Exception:
            try:
                energy_kev = float(line_data.energy)
            except Exception:
                energy_kev = float(line_data)

        return energy_kev, resolved_tag

    def Extract_And_Save(
        self,
        Bcf_File_Path: Path_Like,
        Target_Elements: List[str],
        Output_Dir: Path_Like = Path("data", "xrf", "raw"),
    ) -> None:
        """Run the full BCF → element TIFF extraction pipeline.

        Args:
            Bcf_File_Path: Path to a ``.bcf`` Bruker hypercube file.
            Target_Elements: List of element symbols (e.g. ``["Fe", "Cu", "Pb"]``)
                or symbol-plus-line strings (e.g. ``["Au_La"]``).
            Output_Dir: Directory where element TIFFs will be written.
                Defaults to ``data/xrf/raw/`` relative to the current
                working directory.

        Raises:
            FileNotFoundError: If *Bcf_File_Path* does not exist.
        """
        # lazy import — hyperspy is heavy
        import hyperspy.api as hs

        bcf_path = Path(Bcf_File_Path)
        output_dir = Path(Output_Dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        sample_name = bcf_path.stem

        print(f"\n[Bcf_Extractor] Loading hypercube: {bcf_path.name}")
        signal = hs.load(
            str(bcf_path),
            cutoff_at_kV=self.cutoff_at_kv,
            select_type="spectrum_image",
        )

        num_elements = len(Target_Elements)
        print(f"[Bcf_Extractor] Output directory: {output_dir.resolve()}")

        for idx, element_input in enumerate(Target_Elements):
            try:
                center_energy, resolved_tag = self.Resolve_Emission_Line(element_input)
            except Exception as exc:
                print(f"[Bcf_Extractor] [{idx+1}/{num_elements}] SKIPPING '{element_input}': {exc}")
                continue

            print(
                f"[Bcf_Extractor] [{idx+1}/{num_elements}] Extracting {resolved_tag} "
                f"(line at {center_energy:.3f} keV) …"
            )

            p_min = center_energy - (self.peak_width_kev / 2.0)
            p_max = center_energy + (self.peak_width_kev / 2.0)
            bg1_min = (center_energy - self.bg_offset_kev) - (self.bg_width_kev / 2.0)
            bg1_max = (center_energy - self.bg_offset_kev) + (self.bg_width_kev / 2.0)
            bg2_min = (center_energy + self.bg_offset_kev) - (self.bg_width_kev / 2.0)
            bg2_max = (center_energy + self.bg_offset_kev) + (self.bg_width_kev / 2.0)

            try:
                gross_map = signal.isig[p_min:p_max].sum(axis=-1).data.astype(np.float64)
                bg1_map = signal.isig[bg1_min:bg1_max].sum(axis=-1).data.astype(np.float64)
                bg2_map = signal.isig[bg2_min:bg2_max].sum(axis=-1).data.astype(np.float64)
            except (IndexError, ValueError):
                print(
                    f"[Bcf_Extractor]   └─ SKIPPING: line at {center_energy:.2f} keV "
                    f"is outside detector range (max {self.cutoff_at_kv} kV)."
                )
                continue

            width_ratio = self.peak_width_kev / self.bg_width_kev
            estimated_bg = ((bg1_map + bg2_map) / 2.0) * width_ratio

            net_map = gross_map - estimated_bg
            np.clip(net_map, 0.0, None, out=net_map)

            final_map = net_map.astype(np.float32)

            output_file = output_dir / f"{sample_name}_{resolved_tag}_raw.tiff"
            tifffile.imwrite(
                str(output_file),
                final_map,
                metadata={"element": resolved_tag, "energy_kev": center_energy},
            )
            print(f"[Bcf_Extractor]   └─ Saved: {output_file.name}")

        print("[Bcf_Extractor] Pipeline complete.\n")