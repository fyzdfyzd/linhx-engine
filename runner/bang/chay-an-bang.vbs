' Chay bang theo doi hang-doi AN hoan toan (dung lai cach cua chay-an-tho.vbs)
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
If InStr(thamSo, "--log") = 0 Then
    thamSo = thamSo & " --log C:\linhx\bang-hang-doi.log"
End If
py1 = sh.ExpandEnvironmentStrings("%SystemRoot%\py.exe")
py2 = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Launcher\py.exe")
If fso.FileExists(py1) Or fso.FileExists(py2) Then
    lenhPy = "py -3"
Else
    lenhPy = "python"
End If
sh.Run lenhPy & " bang.py" & thamSo, 0, False
