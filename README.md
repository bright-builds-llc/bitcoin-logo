# Bitcoin Logos

This repository collects Bitcoin logos that are in the public domain or
available under open licenses.

Some files include small shape corrections to improve their use in physical
fabrication. In particular, sharp edges and other geometry that can cause
problems during 3D printing, extrusion, or similar workflows may be softened
or cleaned up.

Check the licensing information included with each asset before using or
redistributing it.

## Included Logos

![Original circular Bitcoin logo](bitcoin.svg)

- [`bitcoin.svg`](bitcoin.svg) — the circular Bitcoin symbol downloaded from
  [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Bitcoin.svg).
  Wikimedia Commons identifies the image as public domain because it does not
  meet the threshold of originality. The logo may still be protected as a
  trademark in some jurisdictions.

## Before-and-After Geometry

This compares the first commit containing the SVG
([`66bb8b4`](https://github.com/bright-builds-llc/bitcoin-logo/commit/66bb8b4d71e114bacb110b3e5107f3c4d99ff3af))
with the current SVG commit
([`14f25f6`](https://github.com/bright-builds-llc/bitcoin-logo/commit/14f25f654c7284e66c4d414375e90bac44bd0ebd)),
after eight SVG-editing commits.

| Property | Before | After | Change or observation |
| --- | ---: | ---: | --- |
| Total path nodes | 47 | 41 | 6 fewer nodes (-12.8%) |
| Nodes in the white Bitcoin symbol | 42 | 36 | All 6 removed nodes came from the symbol |
| Cubic Bézier segments | 22 | 18 | 4 fewer curved segments |
| Straight-line segments | 21 | 19 | 2 fewer line segments |
| SVG paths / closed subpaths | 2 / 4 | 2 / 4 | The overall shape structure is unchanged |
| Nominal canvas | 64 × 64 | 6400 × 6400 | 100× larger in each dimension for easier editing |
| `viewBox` | Not set | `0 0 64 64` | Preserves the original 64-unit coordinate system |
| Visible colors | `#f7931a`, `#FFF` | `#f7931a`, `#ffffff` | The orange and white colors are visually unchanged |
| Inkscape node classifications | Not recorded | 32 corner, 4 smooth | The symbol now records four explicitly smooth nodes |
| XML elements | 4 | 9 | Inkscape added editor and document metadata |
| File size | 1,498 bytes | 2,631 bytes | 75.6% larger from metadata and formatting despite fewer nodes |

Node counts come from the committed path data: each move point or segment
endpoint counts as one node, while a close-path command does not add a node.
The orange disc's geometry is unchanged; its path was only rewritten from
relative to absolute coordinates.

### Reproducing the measurements

The standard-library-only
[`scripts/analyze_svg.py`](scripts/analyze_svg.py) script reads both SVG
versions directly from Git and prints the measurements used above. It requires
Git and Python 3, but no third-party packages.

Run it from the repository root:

```powershell
python scripts/analyze_svg.py
```

By default, the script finds the first commit containing `bitcoin.svg` and
compares it with `HEAD`. To reproduce the exact comparison above regardless of
the currently checked-out commit, pass both commit IDs:

```powershell
python scripts/analyze_svg.py --before 66bb8b4 --after 14f25f6
```

## Sharp-Edge Demonstration

The
[sharp-edge demonstration video](2026-08-11-bitcoin-logo-sharp-edges.mp4)
shows several pointed areas in the original logo geometry that can cause
problems when the shape is extruded or prepared for 3D printing.