# release_tool

Python helper to create and clean release artifacts for **Manta Airlab**.

Repository: `manta-airfoil-tools`

## Prerequisites

- Python 3.10+
- Internet access for first dependency install

## Build executable + installer (Windows)

From repository root:

```bash
python release_tool/release_tool.py build
```

What it does:
1. Installs build dependencies from `release_tool/requirements-build.txt`
2. Runs PyInstaller with `release_tool/manta-airfoil-tools.spec`
3. Produces executable in `dist/` (`dist/Manta_Airfoil_Tools_portable_<version>.exe`)
4. Runs Inno Setup and produces installer in `dist/` (`dist/Manta_Airfoil_Tools_setup_<version>.exe`)
5. Removes temporary build folders (`build/`, `release_tool/dist/`, `__pycache__/`)

Default installer version is `1.0.0`. You can override it:

```bash
python release_tool/release_tool.py build --app-version 1.2.0
```

## Build only executable

```bash
python release_tool/release_tool.py build-exe
```

With explicit version:

```bash
python release_tool/release_tool.py build-exe --app-version 1.2.0
```

## Build only installer (from existing exe)

```bash
python release_tool/release_tool.py build-installer --app-version 1.2.0
```

If Inno Setup is not in PATH, pass:

```bash
python release_tool/release_tool.py build-installer --iscc-path "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

## Clean artifacts

From repository root:

```bash
python release_tool/release_tool.py clean
```

This removes generated build folders/files such as `build/`, `dist/`, and local `__pycache__` folders.

## Notes

- The spec file includes the entire `images/` directory, required by GUI icon/logo assets.
- Inno Setup 6 is required for installer generation (`ISCC.exe`).
- Installer uses `images/ico.ico` as setup icon.
- Wizard branding uses `images/logo_manta_air_lab.svg` when `cairosvg` is available; otherwise it falls back to bundled raster logo files.
- Installer can download runtime assets with progress (`airfoil.db` and `XFOIL6.99.zip`) when the `runtimeassets` task is selected (default).
- During setup, XFOIL is extracted with elevated rights and normalized to `{app}\\xfoil\\xfoil.exe` (extra extracted files are cleaned).
- Existing installed versions are handled by Inno Setup using the same stable `AppId` (standard upgrade path).
- Benchmark cases and generated benchmark reports are not included in the packaged executable.
- Unsigned Windows executables may show `Unknown publisher` and trigger Microsoft Defender SmartScreen warnings when downloaded from the internet.

