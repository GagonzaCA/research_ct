# Research CT

Unsupervised material segmentation for micro-CT and XRF of sealed historical books.

## What this project does

This repository implements a dual-modal pipeline for analyzing historical books without destruction:

- **CT Pipeline (research_ct)**: Segments micro-CT volumes into material classes (air, paper, ink, cover, adhesive) using hierarchical GMM + HMRF spatial regularization. No labelled training data required.
- **XRF Pipeline (xrf)**: Extracts elemental composition from X-Ray Fluorescence data, clusters pages by chemical makeup, and builds per-page leaf signatures for material comparison.

## Where to start

- New users -> [Installation](guides/installation.md) then [Quick Start](guides/quickstart.md)
- Running CT analysis -> [CT Pipeline guide](guides/ct_pipeline.md)
- Running XRF analysis -> [XRF Pipeline guide](guides/xrf_pipeline.md)
- API details -> [research_ct API](api/research_ct.md) / [xrf API](api/xrf.md)

## Status (2026-08-09)

Both pipelines are independently operational on real data (Brevar Capucin CT, Letter_1 XRF). The CT-XRF fusion module (ct_xrf_fusion.py) is planned but not yet implemented.
