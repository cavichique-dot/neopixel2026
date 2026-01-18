Set WshShell = CreateObject("WScript.Shell") 
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "venv\Scripts\pythonw.exe start.py", 0
Set WshShell = Nothing