' Chay linhx-runner AN hoan toan (luat 02/11: khong mo console tren may cty)
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
d = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = d
thamSo = ""
For Each a In WScript.Arguments
    If InStr(a, " ") > 0 Then
        thamSo = thamSo & " """ & a & """"
    Else
        thamSo = thamSo & " " & a
    End If
Next
py1 = sh.ExpandEnvironmentStrings("%SystemRoot%\py.exe")
py2 = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Launcher\py.exe")
If fso.FileExists(py1) Or fso.FileExists(py2) Then
    lenhPy = "py -3.12"
Else
    lenhPy = "python"
End If
sh.Run lenhPy & " linhx_runner.py --log tho.log" & thamSo, 0, False
