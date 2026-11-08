# Đăng ký Task Scheduler chạy chay-vong.ps1 mỗi N phút cho một thư mục việc. Linh chạy một lần trên MÁY CÔNG TY.
param([Parameter(Mandatory = $true)][string]$Viec, [int]$Phut = 20, [string]$Ten = "LINHX-AgyTuChay")
$ban = Join-Path $PSScriptRoot "chay-vong.ps1"
# Chạy ngầm hoàn toàn: wscript + chay-an.vbs mở PowerShell với cửa sổ 0 (powershell -WindowStyle Hidden vẫn chớp console).
$an = Join-Path $PSScriptRoot "chay-an.vbs"
$lenh = "//B //Nologo `"$an`" `"$ban`" -Viec `"$Viec`""
$hanhDong = New-ScheduledTaskAction -Execute "wscript.exe" -Argument $lenh -WorkingDirectory $Viec
$kichHoat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $Phut)
$caiDat = New-ScheduledTaskSettingsSet -Hidden -MultipleInstances IgnoreNew -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 60)
Register-ScheduledTask -TaskName $Ten -Action $hanhDong -Trigger $kichHoat -Settings $caiDat -Force | Out-Null
Write-Host "Đã đăng ký $Ten mỗi $Phut phút cho $Viec. Tắt: Unregister-ScheduledTask $Ten"
