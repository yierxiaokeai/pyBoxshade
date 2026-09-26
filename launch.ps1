$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Run python -m venv .venv and install this project first. See INSTALL.txt.'
}
Start-Process -FilePath $pythonPath -ArgumentList @('-m', 'pyboxshade') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
