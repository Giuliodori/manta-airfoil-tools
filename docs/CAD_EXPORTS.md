# CAD and Export Guide

One of the main workflow advantages of Manta Airlab is export-first usability.
You can define chord and span in the app, inspect geometry in `2D` or `3D`, and export output already close to downstream form.

## Supported export formats

- `.pts`
- `.dxf`
- `.stl`
- `.csv`

## CAD and 3D tools commonly used with DXF

- AutoCAD
- CREO Parametric
- Fusion 360
- Inventor
- SolidWorks
- FreeCAD
- Rhino
- BricsCAD
- DraftSight
- QCAD
- LibreCAD
- Onshape (DXF workflow)

## Point cloud and `.pts` (XYZ) workflows

- CloudCompare
- MeshLab
- MATLAB
- GNU Octave
- Python (NumPy / Pandas)
- CATIA (point import)
- Siemens NX (point import)
- Autodesk Alias (point set)

## CSV points

CSV export writes `x,y,z` with `z=0` and no header by default.
In advanced options you can switch to `x,y` for tools that prefer 2D points.
DXF export defaults to spline, with a polyline option.

Commonly usable with:

- Rhino (CSV/XYZ/PTS points import)
- Fusion 360 (via point/curve import scripts)
- general point cloud or scripting workflows

## Why this workflow is different

Many airfoil tools are strong in lookup, comparison, or deeper solver work.
Manta Airlab is strongest when you need a short path from selection/tuning to usable geometry and quick aerodynamic feedback.

Practical differences:

- direct GUI editing with immediate geometry feedback
- quick aerodynamic response while changing the section
- geometry already scaled by chord and span for downstream use
- optional `2D` and `3D` confirmation before export
- local export to CAD/prototype-friendly formats without browser dependency

This scope is intentional: fast first-pass design work with practical geometry/export flow.

