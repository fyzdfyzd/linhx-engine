' Chạy một lệnh PowerShell hoàn toàn ngầm (cửa sổ 0, không chớp console). Dùng cho mọi lệnh agy theo lịch.
' wscript.exe //B //Nologo chay-an.vbs <file.ps1> [tham số...]
Set a = WScript.Arguments
cmd = "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File """ & a(0) & """"
For i = 1 To a.Count - 1
  cmd = cmd & " """ & a(i) & """"
Next
CreateObject("WScript.Shell").Run cmd, 0, True
