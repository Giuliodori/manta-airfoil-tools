# Third-Party Notices

This repository references external software, datasets, and source websites used for validation, benchmarking, or technical context.

The goal of this file is to keep third-party notices explicit and separate from the main project license.

Manta AirLab itself is licensed under `GPL-3.0-only`. Third-party materials keep their own authorship, copyright, and license terms.

Project credit:

- Manta AirLab — Airfoil Tools by Fabio Giuliodori
- Project home and sponsorship: https://duilio.cc

## XFOIL

XFOIL is an airfoil analysis and design program by Mark Drela and Harold Youngren.

- Upstream site: https://web.mit.edu/drela/Public/web/xfoil/
- Upstream notice: the XFOIL site states that XFOIL is released under the GNU General Public License.

Current status in this repository:

- XFOIL is referenced in documentation as an established external tool and comparison point.
- No upstream XFOIL source or binary distribution is currently bundled in this repository.

If a future version of this repository redistributes XFOIL source code, binaries, or modified copies, the corresponding upstream GPL notice, copyright notice, and source-distribution obligations must be included with that distribution.

## UIUC Low-Speed Airfoil Tests and UIUC Airfoil Data Site

This repository uses and cites material from the UIUC Applied Aerodynamics Group, especially the UIUC Low-Speed Airfoil Tests (`UIUC LSAT`) reference data used by the benchmark suite.

Primary sources:

- UIUC wind-tunnel data page: https://m-selig.ae.illinois.edu/pd.html
- UIUC Airfoil Data Site: https://m-selig.ae.illinois.edu/ads.html
- UIUC LSAT Manifesto: https://m-selig.ae.illinois.edu/pd/manifest.html
- Example volume cited by this repository: https://m-selig.ae.illinois.edu/pubs/Low-Speed-Airfoil-Data-V2.pdf

Current status in this repository:

- Benchmark cases such as `naca2414`, `naca2415`, and `clarky` cite UIUC LSAT sources.
- The CSV files in `benchmarks/data/` include reference values derived from UIUC LSAT source tables.

Notice for UIUC-derived benchmark data distributed with this repository:

- This product includes data produced under the UIUC Low-Speed Airfoil Tests program.
- Source references are preserved in `benchmarks/cases/*.json`.
- The UIUC data page requires products using this data to conspicuously state that it was produced under the UIUC Low-Speed Airfoil Tests program.
- The same UIUC notice also requires including the applicable license, copyright notice, and the UIUC Low-Speed Airfoil Tests Manifesto when distributing the data.

Repository handling note:

- When distributing UIUC LSAT-derived data files from this repository, also include the relevant UIUC copyright/license notice and the UIUC Low-Speed Airfoil Tests Manifesto referenced by the UIUC data page.

## Other research references

The benchmark suite also cites NASA and NLR/OSU reference material. Those citations are tracked in the corresponding case files under `benchmarks/cases/`.

## Maintainer note

This file is intended to keep attribution and redistribution notices visible. It does not replace upstream license texts where upstream redistribution terms require them to be included verbatim.
