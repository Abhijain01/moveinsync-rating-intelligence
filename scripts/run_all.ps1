<#
Monthly refresh: clean a raw snapshot, print the headline, write the full report.
Usage (from the project root, venv active):
  .\scripts\run_all.ps1 -RawRun data\raw\run_20261110T090000Z
  .\scripts\run_all.ps1 -RawRun data\raw\run_20261110T090000Z -Prev data\processed\run_20261010T203205Z\reviews_clean.csv
#>
param(
    [Parameter(Mandatory = $true)][string]$RawRun,
    [string]$Prev = ""
)
$ErrorActionPreference = "Continue"

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
