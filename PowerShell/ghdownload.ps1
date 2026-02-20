$apiUrl = "https://api.github.com/repos/AdguardTeam/AdguardFilters/contents/BaseFilter/sections"
$downloadFolder = "C:\Users\dariu\Documents\GitHub\AD-BlockList\AdguardDNS Lists"

# Create folder if needed
if (!(Test-Path $downloadFolder)) {
    New-Item -ItemType Directory -Path $downloadFolder | Out-Null
}

# GitHub requires a user-agent
$headers = @{
    "User-Agent" = "PowerShell"
}

# Get file list
$response = Invoke-RestMethod -Uri $apiUrl -Headers $headers

# Filter .txt files only
$files = $response | Where-Object {
    $_.type -eq "file" -and $_.name -match "\.txt$"
}

foreach ($file in $files) {
    $downloadUrl = $file.download_url
    $outputPath = Join-Path $downloadFolder $file.name

    Write-Host "Downloading $($file.name)..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath
}

Write-Host "Done."