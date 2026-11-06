' Chay linhx-runner AN hoan toan (luat 02/11: khong mo console tren may cty)
Set sh = CreateObject("WScript.Shell")
d = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = d
sh.Run "cmd /c py -3.12 linhx_runner.py >> tho.log 2>&1", 0, False
