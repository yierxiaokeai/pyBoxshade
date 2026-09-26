$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    & $pythonPath -m PyInstaller --noconfirm pyboxshade-modern.spec
    if ($LASTEXITCODE -ne 0) { throw 'Application build failed.' }
    Copy-Item -LiteralPath LICENSE -Destination dist\pyBoxshade\LICENSE
    Copy-Item -LiteralPath README.md,INSTALL.txt,使用说明.md -Destination dist\pyBoxshade
    Copy-Item -LiteralPath examples -Destination dist\pyBoxshade\examples -Recurse
} finally {
    Pop-Location
}
