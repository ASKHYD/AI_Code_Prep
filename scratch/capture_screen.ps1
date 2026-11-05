param(
    [string]$url = "http://127.0.0.1:8501/?screen=home",
    [string]$out = "E:/resume_project/scratch/capture.png",
    [int]$waitMs = 3500,
    [int]$width = 1440,
    [int]$height = 900
)

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$profileDir = Join-Path $env:TEMP ("chrome_prof_" + [Guid]::NewGuid().ToString().Substring(0,8))
$chromeProc = Start-Process -FilePath $chrome -ArgumentList "--headless=new", "--disable-gpu", "--remote-debugging-port=9222", "--user-data-dir=$profileDir", "--window-size=$width,$height" -PassThru
Start-Sleep -Milliseconds 1800
try {
    node scratch/capture.js "$url" "$out" $waitMs
} finally {
    Stop-Process -Id $chromeProc.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 300
    Remove-Item -Recurse -Force $profileDir -ErrorAction SilentlyContinue
}
