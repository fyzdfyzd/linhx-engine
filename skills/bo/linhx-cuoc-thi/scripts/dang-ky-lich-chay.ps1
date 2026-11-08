# Dang ky chay radar cuoc thi moi thu Hai 7:30 (chay 1 lan trong PowerShell, khong can admin)
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$action = New-ScheduledTaskAction -Execute "$dir\chay-radar.bat"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7:30am
Register-ScheduledTask -TaskName "LINHX Contest Radar" -Action $action -Trigger $trigger -Description "LAB022: quet cuoc thi, ghi output\digest" -Force
Write-Host "Da dang ky. Go bang: Unregister-ScheduledTask -TaskName LINHX Contest Radar"
