# Quick Start

## CT Pipeline (research_ct)

```python
from research_ct.io.volume_loader import Load_Slice_Stack
from research_ct.preprocessing.pipeline_revised import Preprocess_For_Gmm_Revised
from research_ct.segmentation.gmm_fitter import Gmm_Fitter

Volume = Load_Slice_Stack("data/raw/")
Preprocessed, Diagnostics = Preprocess_For_Gmm_Revised(Volume)
Gmm = Gmm_Fitter(Min_Components=2, Max_Components=8)
Gmm.Fit(Preprocessed.reshape(-1, 1))
Labels = Gmm.Predict_Labels(Preprocessed.reshape(-1, 1)).reshape(Volume.shape)
Probabilities = Gmm.Predict_Probabilities(Preprocessed.reshape(-1, 1))
```

## XRF Pipeline (xrf)

```python
from xrf.io.xrf_loader import Xrf_Loader
from xrf.transforms.coda import Clr_Transformer
from xrf.segmentation.xrf_gmm import Xrf_Gmm_Segmenter

Stack = Xrf_Loader.Load_Element_Stack([
    "data/xrf/raw/Letter_1_Pb_La.tiff",
    "data/xrf/raw/Letter_1_Fe_Ka.tiff",
])
Mask = Xrf_Loader.Compute_Intensity_Mask(Stack, Tau_Noise=5.0)
Valid_Pixels = Stack[Mask]
Clr_Data = Clr_Transformer.Apply_Clr_Transform(Valid_Pixels)
Labels, Probs, Pca, Gmm = Xrf_Gmm_Segmenter.Fit_Predict(
    Clr_Data, Num_Components=7, Variance_Ratio=0.95
)
```
