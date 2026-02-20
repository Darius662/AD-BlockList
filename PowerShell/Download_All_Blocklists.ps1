# Combined Blocklist Downloader
# Downloads AdGuard filter lists from multiple GitHub repositories

$headers = @{
    "User-Agent" = "PowerShell"
}

function Get-GitHubFiles {
    param(
        [string]$apiUrl,
        [string]$downloadFolder,
        [string]$filePattern = "\.txt$",
        [string]$description = "files"
    )

    Write-Host "`n=== Downloading $description ==="
    Write-Host "Source: $apiUrl"
    Write-Host "Destination: $downloadFolder"

    # Create download folder if missing
    if (!(Test-Path $downloadFolder)) {
        New-Item -ItemType Directory -Path $downloadFolder | Out-Null
        Write-Host "Created folder: $downloadFolder"
    }

    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers

        # Filter files based on pattern
        $files = $response | Where-Object {
            $_.type -eq "file" -and $_.name -match $filePattern
        }

        Write-Host "Found $($files.Count) files matching pattern '$filePattern'"

        foreach ($file in $files) {
            $downloadUrl = $file.download_url
            $outputPath = Join-Path $downloadFolder $file.name

            Write-Host "  Downloading $($file.name)..."
            Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath
        }

        Write-Host "Completed: Downloaded $($files.Count) files to $downloadFolder"
    }
    catch {
        Write-Error "Failed to download from $apiUrl : $_"
    }
}

# === Source 1: AdGuard Hostlists Registry ===
Get-GitHubFiles `
    -apiUrl "https://api.github.com/repos/AdguardTeam/HostlistsRegistry/contents/assets" `
    -downloadFolder "C:\Users\dariu\Documents\GitHub\AD-BlockList\Adguard Official Lists" `
    -filePattern "^filter_\d+\.txt$" `
    -description "AdGuard Hostlists Registry (filter_*.txt)"

# === Source 2: AdGuard Filters - BaseFilter Sections ===
Get-GitHubFiles `
    -apiUrl "https://api.github.com/repos/AdguardTeam/AdguardFilters/contents/BaseFilter/sections" `
    -downloadFolder "C:\Users\dariu\Documents\GitHub\AD-BlockList\AdguardDNS Lists" `
    -filePattern "\.txt$" `
    -description "AdGuard Filters BaseFilter sections"

# === ADD MORE SOURCES HERE ===
# Example for adding another source:
# Get-GitHubFiles `
#     -apiUrl "https://api.github.com/repos/OWNER/REPO/contents/PATH" `
#     -downloadFolder "C:\Users\dariu\Documents\GitHub\AD-BlockList\Custom Folder" `
#     -filePattern "\.txt$" `
#     -description "Custom source description"

Write-Host "`n========================================"
Write-Host "All downloads completed!"
Write-Host "========================================"
