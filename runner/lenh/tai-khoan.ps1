# Thu thập danh sách tài khoản Chrome (email đã che giữa) và tài khoản agy trên máy hiện tại,
# ghi hang-doi/may/<ma_may>-tai-khoan.json và đẩy lên nhánh hang-doi.
param(
    [string]$May = "",
    [string]$LocalState = "",
    [string]$RepoHangDoi = "",
    [switch]$XuatJson,
    [switch]$KhongGit,
    [switch]$EpGhi
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$runnerDir = Split-Path -Parent $PSScriptRoot
$scriptPy = Join-Path $runnerDir "so_tai_khoan.py"

$thamSo = @()
if ($May) {
    $thamSo += @("--may", $May)
}
if ($LocalState) {
    $thamSo += @("--local-state", $LocalState)
}
if ($RepoHangDoi) {
    $thamSo += @("--repo-hang-doi", $RepoHangDoi)
}
if ($XuatJson) {
    $thamSo += "--xuat-json"
}
if (-not $KhongGit) {
    $thamSo += "--cap-nhat-git"
}
if ($EpGhi) {
    $thamSo += "--ep-ghi"
}

& python $scriptPy @thamSo
exit $LASTEXITCODE
