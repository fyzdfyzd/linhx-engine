# Đăng ký lịch ENGINE-DieuPhoi: chạy canh/dieu-phoi-engine.ps1 của repo D:\LINHX\LINHX-ENGINE mỗi 10 phút, ẩn hoàn toàn qua chay-an.vbs. Linh tự chạy một lần.
param([int]$Phut = 10)
$ps1 = "D:\LINHX\LINHX-ENGINE\canh\dieu-phoi-engine.ps1"
$hanhDong = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "//B `"D:\LINHX\LINHX-OPC\CHIEMTINHSO-chung\chay-an.vbs`" `"$ps1`"" -WorkingDirectory "D:\LINHX\LINHX-ENGINE"
$kichHoat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $Phut)
$caiDat = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "ENGINE-DieuPhoi" -Action $hanhDong -Trigger $kichHoat -Settings $caiDat -Force | Out-Null
Write-Host "Đã đăng ký ENGINE-DieuPhoi mỗi $Phut phút. Tắt: Unregister-ScheduledTask ENGINE-DieuPhoi -Confirm:`$false"
