$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Missing virtualenv Python at $python"
}

$iconSource = Join-Path $PSScriptRoot "images\mlem.png"
$iconOutput = Join-Path $PSScriptRoot "images\mlem.ico"

if (-not (Test-Path $iconSource)) {
    throw "Missing icon source at $iconSource"
}

& $python -m pip install pyinstaller pillow
& $python tools\make_icon.py $iconSource $iconOutput
& $python -m PyInstaller --noconfirm --clean --onefile --name autofish --icon $iconOutput nte_auto_fishing.py
