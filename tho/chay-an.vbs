' Chay tien trinh an hoan toan tren Windows (cua so = 0, khong nhay console).
' Cach goi: wscript.exe //B chay-an.vbs <tap_tin_thuc_thi> [tham_so...]
Option Explicit

Sub KiemThamSoAnToan(xau)
  Dim kyTuCam, i
  kyTuCam = Array(vbCr, vbLf, Chr(0))
  For i = 0 To UBound(kyTuCam)
    If InStr(xau, kyTuCam(i)) > 0 Then
      WScript.Quit 3
    End If
  Next
End Sub

Sub KiemDuoiThucThiAnToan(fsoObj, duong)
  Dim duoi, dsCam, i
  duoi = LCase(fsoObj.GetExtensionName(CStr(duong)))
  dsCam = Array("bat", "cmd", "com", "ps1", "vbs", "wsf", "hta", "js", "jse", "msi", "scr", "sh")
  For i = 0 To UBound(dsCam)
    If duoi = dsCam(i) Then
      WScript.Quit 6
    End If
  Next
End Sub

Function BaoThamSo(xau)
  Dim s, canBao, ketQua, i, ch, demGach, k
  s = CStr(xau)
  Call KiemThamSoAnToan(s)
  If Len(s) = 0 Then
    BaoThamSo = """"""
    Exit Function
  End If
  canBao = (InStr(s, " ") > 0) Or (InStr(s, vbTab) > 0) Or (InStr(s, """") > 0)
  If Not canBao Then
    BaoThamSo = s
    Exit Function
  End If
  ketQua = """"
  demGach = 0
  For i = 1 To Len(s)
    ch = Mid(s, i, 1)
    If ch = "\" Then
      demGach = demGach + 1
    ElseIf ch = """" Then
      For k = 1 To (demGach * 2 + 1)
        ketQua = ketQua & "\"
      Next
      ketQua = ketQua & """"
      demGach = 0
    Else
      For k = 1 To demGach
        ketQua = ketQua & "\"
      Next
      ketQua = ketQua & ch
      demGach = 0
    End If
  Next
  For k = 1 To (demGach * 2)
    ketQua = ketQua & "\"
  Next
  ketQua = ketQua & """"
  BaoThamSo = ketQua
End Function

Dim sh, fso, env, pyExe, tapOut, thuMucGoc, duongChayAn
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
Set env = sh.Environment("PROCESS")

thuMucGoc = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = thuMucGoc

pyExe = env("LINHX_THO_PYTHON")
tapOut = env("LINHX_THO_STDOUT")
If Len(pyExe) > 0 And Len(tapOut) > 0 Then
  If Not fso.FileExists(pyExe) Then
    WScript.Quit 5
  End If
  Call KiemDuoiThucThiAnToan(fso, pyExe)
  duongChayAn = fso.BuildPath(thuMucGoc, "linhx_tho\_chay_an.py")
  If Not fso.FileExists(duongChayAn) Then
    WScript.Quit 4
  End If
  Dim lenhPy
  lenhPy = BaoThamSo(pyExe) & " -I -X utf8 " & BaoThamSo(duongChayAn)
  WScript.Quit sh.Run(lenhPy, 0, True)
End If

If WScript.Arguments.Count < 1 Then
  WScript.Quit 2
End If

Dim dau, idx, lenh
dau = WScript.Arguments(0)
If Not fso.FileExists(dau) Then
  WScript.Quit 5
End If
Call KiemDuoiThucThiAnToan(fso, dau)
lenh = BaoThamSo(dau)

For idx = 1 To WScript.Arguments.Count - 1
  lenh = lenh & " " & BaoThamSo(WScript.Arguments(idx))
Next

WScript.Quit sh.Run(lenh, 0, True)
