# NXOpenPythonStub

Cleaned NXOpen Python API stubs for Pylance.

## Contents

- `NXOpen/`
- `NXOpenUI/`
- `scripts/clean_nxopen_stubs.py`
- `NXOpen_stub_cleanup.md`

## Purpose

These stubs are cleaned from generated NXOpen API output so they are easier for Pylance to consume.

The cleanup focuses on:

- invalid identifiers and generated syntax artifacts
- broken annotation forms such as `any` or `Tag[]`
- static method inference for APIs like `Session.GetSession()`
- converting annotated members to property form for more stable chained type inference

## Acknowledgements

Thanks to the original stub provider, [theScriptingEngineer / Frederik Vanhee](https://community.sw.siemens.com/s/profile/0054O00000ANP82QAH), for publishing the original NXOpen Python Intellisense stubs and usage notes in the Siemens Community post:

- [NXOpen intellisense for Python in Visual Studio Code](https://community.sw.siemens.com/s/feed/0D54O00007oICmdSAG)

This repository publishes a cleaned and Pylance-friendly derivative of that stub set.

## Pylance

Point `python.analysis.stubPath` to the directory that contains `NXOpen/` and `NXOpenUI/`.

## Examples

- `examples/traverse_all_components.py`: recursively traverses all assembly components from the work part root component and writes the result to the NX Listing Window.
- `examples/component_body_spatial_matrix.py`: collects per-body area, mass, centroid, bounding-box data for each component and builds a tuple-indexed 3D spatial matrix such as `matrix[0, 1, 1]`.

## Regeneration

If you regenerate the raw NXOpen files, rerun:

```powershell
python scripts/clean_nxopen_stubs.py <raw_stub_root> <clean_output_root>
```

More detail is in [NXOpen_stub_cleanup.md](NXOpen_stub_cleanup.md).
