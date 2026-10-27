# Manta Airlab Nuitka release tooling

Primary release command from the repository root:

```powershell
python .\Action\release_manta_airlab.py
```

The launcher builds with Nuitka, creates the Inno Setup installer, signs release artifacts, mirrors the installer into the local `DUILIO.CC` site repo, writes `manifest.json`, and uploads installer + manifest through WinSCP.

Useful direct commands:

```powershell
.\release_tooling_nuitka\scripts\build_exe_manta_airlab_nuitka.ps1 -PythonExe python -AppVersion 0.1.5
.\release_tooling_nuitka\scripts\sign_manta_release.ps1 -WhatIf
.\release_tooling_nuitka\scripts\publish_installer_to_duilio_cc.ps1 -SiteRepoRoot C:\Users\fabio\OneDrive\DUILIO.CC -RemoteSubdir manta-airfoil-tools/downloads -RemoteBaseUrl https://duilio.cc/manta-airfoil-tools/downloads -SkipUpload
```
