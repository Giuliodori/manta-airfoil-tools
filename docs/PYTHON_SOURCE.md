# Python Source Guide (Optional)

Repository: `manta-airfoil-tools`
Brand: `Manta Airlab`

Use this guide if you want to run Manta Airlab from Python source instead of the Windows executable.

## Requirements

- Python `3.10+`
- `pip`
- Windows PowerShell or terminal shell

Runtime dependencies:

- `numpy`
- `matplotlib`
- `ezdxf` (required for `.dxf` export)

## 1. Create and activate a virtual environment (recommended)

From repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If script execution is blocked in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Install Python dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Bootstrap runtime assets

This step prepares local runtime assets such as `database/airfoil.db` and `xfoil/xfoil.exe`.

```bash
python manta_airfoil_tools.py setup --yes
```

Useful setup options:

- `--skip-python` skip Python package checks
- `--skip-airfoil-db` skip download/update of `database/airfoil.db`
- `--skip-xfoil` skip download/update of `xfoil/xfoil.exe`

## 4. Run the application

GUI:

```bash
python manta_airfoil_tools.py
```

Alternative on Windows:

- run `manta_airfoil_tools.bat`

## 5. Verify installation quickly

```bash
python manta_airfoil_tools.py --help
python manta_airfoil_tools.py export --help
python manta_airfoil_tools.py analyze --help
```

## Common issues

- Missing `ezdxf`: DXF export will fail until `ezdxf` is installed.
- Missing runtime assets: run `python manta_airfoil_tools.py setup --yes` again.
- First-time downloads blocked by network/proxy: pre-provision required files (`database/airfoil.db`, `xfoil/xfoil.exe`) in expected paths.

## Related docs

- CLI details: [`CLI.md`](CLI.md)
- Contributing and local checks: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Release packaging: [`../release_tool/README.md`](../release_tool/README.md)
