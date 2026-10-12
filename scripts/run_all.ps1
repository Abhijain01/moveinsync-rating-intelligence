<#
Monthly refresh: clean a raw snapshot, print the headline, write the full report.
Usage (from the project root, venv active):
  .\scripts\run_all.ps1                                   (uses the newest folder in data\raw)
  .\scripts\run_all.ps1 -RawRun data\raw\run_20261110T090000Z
  .\scripts\run_all.ps1 -RawRun data\raw\run_20261110T090000Z -Prev data\processed\run_20261010T203205Z\reviews_clean.csv
#>
param(
    [string]$RawRun = "",
    [string]$Prev = ""
)
$ErrorActionPreference = "Continue"

if ($RawRun -eq "") {
    $latest = Get-ChildItem "data\raw" -Directory -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName "reviews.jsonl") } |
        Sort-Object Name -Descending | Select-Object -First 1
    if (-not $latest) { throw "No snapshot with reviews.jsonl found in data\raw. Run scripts\ingest.py first." }
    $RawRun = Join-Path "data\raw" $latest.Name
    Write-Host "Using newest snapshot: $RawRun"
}

if (-not (Test-Path (Join-Path $RawRun "reviews.jsonl"))) { throw "No reviews.jsonl in $RawRun" }
$id = Split-Path $RawRun -Leaf
$csv = "data\processed\$id\reviews_clean.csv"
$manifest = Join-Path $RawRun "manifest.json"
$out = "reports\analysis_$id"

python -m rating_intel clean $RawRun
if ($LASTEXITCODE -ne 0) { throw "clean failed" }

python -m rating_intel status $csv --manifest $manifest
if ($LASTEXITCODE -ne 0) { throw "status failed" }

if ($Prev -ne "") {
    python -m rating_intel analyze $csv --prev $Prev --manifest $manifest --out $out
} else {
    python -m rating_intel analyze $csv --manifest $manifest --out $out
}
if ($LASTEXITCODE -ne 0) { throw "analyze failed" }
Write-Host "Report: $out\report.md"