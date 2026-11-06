# Dang ky linhx-runner tu chay khi dang nhap (khong can quyen quan tri). Chay 1 lan.
$d = Split-Path -Parent $MyInvocation.MyCommand.Path
$a = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$d\chay-an-tho.vbs`""
$t = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 99 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "LINHX-Runner" -Action $a -Trigger $t -Settings $s -Force | Out-Null
Start-ScheduledTask -TaskName "LINHX-Runner"
"LINHX-Runner da dang ky va dang chay. Log: $d\tho.log"
