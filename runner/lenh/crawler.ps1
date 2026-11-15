# Thu thập trạng thái các nguồn crawler trên máy hiện tại (không lưu nội dung đã quét hay cookie),
# ghi hang-doi/may/<ma_may>-crawler.json và đẩy lên nhánh hang-doi.
param(
    [string]$May = "",
    [string]$RepoHangDoi = "",
    [string]$XuatJson = "",
    [string[]]$ThuMucThu = @(),
    [switch]$KhongGit,
    [switch]$EpGhi
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$runnerDir = Split-Path -Parent $PSScriptRoot
$scriptPy = Join-Path $runnerDir "quet_cong_cu_may.py"

$thamSo = @("--loai", "crawler")
if ($May) {
    $thamSo += @("--may", $May)
}
if ($RepoHangDoi) {
    $thamSo += @("--repo-hang-doi", $RepoHangDoi)
}
if ($XuatJson) {
    $thamSo += @("--xuat-json", $XuatJson)
}
foreach ($tm in $ThuMucThu) {
    if ($tm) {
        $thamSo += @("--thu-muc-thu", $tm)
    }
}
if (-not $KhongGit) {
    $thamSo += "--cap-nhat-git"
}
if ($EpGhi) {
    $thamSo += "--ep-ghi"
}

& python $scriptPy @thamSo
exit $LASTEXITCODE
