# XRF Pipeline Guide

End-to-end walkthrough of the X-Ray Fluorescence elemental analysis pipeline.

## Overview

1. **Element loading** — Per-element TIFFs to (M, N, n_elements) cube
2. **Masking** — Threshold on total intensity to discard background/noise pixels
3. **CLR transform** — Zero-replace, normalize, Centered Log-Ratio projection
4. **PCA reduction** — Retain 95% cumulative variance
5. **GMM clustering** — Discover compositional classes K in latent space
6. **Spatial analysis** — Connected-component descriptors per class
7. **Signatures** — Build per-page leaf signature F_h and book-level weighted average
8. **Comparison** — Category norms + rarity scoring against structural categories
