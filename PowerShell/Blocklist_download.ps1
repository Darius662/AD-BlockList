$apiUrl = "https://api.github.com/repos/AdguardTeam/HostlistsRegistry/contents/assets"
$downloadFolder = "C:\Users\dariu\Documents\GitHub\AD-BlockList\Adguard Official Lists"

# Create download folder if missing
if (!(Test-Path $downloadFolder)) {
    New-Item -ItemType Directory -Path $downloadFolder | Out-Null
}

# GitHub requires a user-agent header
$headers = @{
    "User-Agent" = "PowerShell"
}

$response = Invoke-RestMethod -Uri $apiUrl -Headers $headers

# Filter only filter_{number}.txt files
$files = $response | Where-Object {
    $_.name -match "^filter_\d+\.txt$"
}

foreach ($file in $files) {
    $downloadUrl = $file.download_url
    $outputPath = Join-Path $downloadFolder $file.name

    Write-Host "Downloading $($file.name)..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath
}

Write-Host "Done."