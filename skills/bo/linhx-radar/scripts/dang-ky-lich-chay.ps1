# Radar LINHX hop nhat: dang ky MOT lich chay moi sang 7:30 va go 4 lich cu (chay 1 lan trong PowerShell, khong can admin)
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($old in @("LINHX Community Radar", "LINHX Event Radar", "LINHX Contest Radar", "LINHX Grants Radar")) {
  if (Get-ScheduledTask -TaskName $old -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $old -Confirm:$false
    Write-Host "Da go lich cu: $old"
  }
}
$action = New-ScheduledTaskAction -Execute "$dir\chay-radar.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 7:30am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "LINHX Radar" -Action $action -Trigger $trigger -Settings $settings -Description "LAB035 radar hop nhat: ghi output\BAN-TIN-MOI-NHAT.md va output\RADAR-LINHX.xlsx" -Force
Write-Host "Da dang ky 'LINHX Radar' 7:30 moi sang. Go bang: Unregister-ScheduledTask -TaskName 'LINHX Radar'"
