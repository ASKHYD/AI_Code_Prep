$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$profileDir = Join-Path $env:TEMP ("chrome_prof_" + [Guid]::NewGuid().ToString().Substring(0,8))
$chromeProc = Start-Process -FilePath $chrome -ArgumentList "--headless=new", "--disable-gpu", "--remote-debugging-port=9222", "--user-data-dir=$profileDir", "--window-size=1920,1080" -PassThru
Start-Sleep -Milliseconds 2000
try {
    node scratch/capture_r3.js
} finally {
    Stop-Process -Id $chromeProc.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    Remove-Item -Recurse -Force $profileDir -ErrorAction SilentlyContinue
}
