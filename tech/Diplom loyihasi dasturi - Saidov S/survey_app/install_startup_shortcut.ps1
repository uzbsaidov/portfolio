$target = Join-Path $PSScriptRoot 'start_flask_app.bat'
$WshShell = New-Object -ComObject WScript.Shell
$startUp = [Environment]::GetFolderPath('Startup')
$linkPath = Join-Path $startUp 'Start Flask App.lnk'
$shortcut = $WshShell.CreateShortcut($linkPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.WindowStyle = 1
$shortcut.Save()
Write-Host "Startup shortcut created:" $linkPath
