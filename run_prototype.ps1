$ErrorActionPreference = "Stop"

& "$PSScriptRoot\venv\Scripts\python.exe" `
    "$PSScriptRoot\main.py" `
    "$PSScriptRoot\dataset\BHC_MIMIC-IV.csv" `
    --text-column input `
    --rows 0,1,2,3 `
    --output-dir "$PSScriptRoot\outputs\prototype"
