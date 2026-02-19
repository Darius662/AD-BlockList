# Convert AdGuard blocklist files to PiHole format
# PiHole uses plain domain list (one domain per line)
# AdGuard uses ||domain.com^ format

$sourceDir = "C:\Users\dariu\Desktop\ADGuard-BlockLists\AdGuard-Home"
$targetDir = "C:\Users\dariu\Desktop\ADGuard-BlockLists\PiHole"

# Create target directory if it doesn't exist
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force
}

# Create subdirectories if needed
$subdirs = @("split_by_source", "split_files")
foreach ($subdir in $subdirs) {
    $subdirPath = Join-Path $targetDir $subdir
    if (-not (Test-Path $subdirPath)) {
        New-Item -ItemType Directory -Path $subdirPath -Force
    }
}

function Convert-AdGuardToPiHole {
    param(
        [string]$inputFile,
        [string]$outputFile
    )
    
    Write-Host "Converting: $inputFile -> $outputFile"
    
    # Create StreamReader for input file
    $reader = [System.IO.StreamReader]::new($inputFile)
    # Create StreamWriter for output file
    $writer = [System.IO.StreamWriter]::new($outputFile)
    
    try {
        $lineCount = 0
        $domainCount = 0
        
        while ($null -ne ($line = $reader.ReadLine())) {
            $lineCount++
            $trimmed = $line.Trim()
            
            # Skip empty lines and comments
            if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
            if ($trimmed.StartsWith("!")) { continue }
            if ($trimmed.StartsWith("#")) { continue }
            if ($trimmed.StartsWith("//")) { continue }
            
            # Convert AdGuard format to PiHole format
            $domain = $trimmed
            
            # Remove AdGuard prefix || and suffix ^
            if ($domain.StartsWith("||")) {
                $domain = $domain.Substring(2)
            }
            if ($domain.EndsWith("^")) {
                $domain = $domain.Substring(0, $domain.Length - 1)
            }
            
            # Handle additional AdGuard modifiers (like ^$third-party)
            if ($domain.Contains("^$")) {
                $domain = $domain.Split("^$")[0]
            }
            
            # Skip if it's not a valid domain format
            if ($domain -match "^[a-zA-Z0-9]" -and $domain.Contains(".")) {
                $writer.WriteLine($domain)
                $domainCount++
            }
        }
        
        Write-Host "  Processed $lineCount lines, extracted $domainCount domains"
    }
    finally {
        $reader.Close()
        $writer.Close()
    }
}

# Process main files
$mainFiles = @(
    "BlockList.txt",
    "BlockList_clean.txt",
    "BlockList_unique.txt",
    "Romanian_Complete_Blocklist.txt"
)

foreach ($file in $mainFiles) {
    $sourcePath = Join-Path $sourceDir $file
    if (Test-Path $sourcePath) {
        $targetPath = Join-Path $targetDir $file
        Convert-AdGuardToPiHole -inputFile $sourcePath -outputFile $targetPath
    } else {
        Write-Host "Skipping (not found): $file"
    }
}

# Process split_files subdirectory
$splitFilesDir = Join-Path $sourceDir "split_files"
if (Test-Path $splitFilesDir) {
    $files = Get-ChildItem -Path $splitFilesDir -File
    foreach ($file in $files) {
        $sourcePath = $file.FullName
        $targetPath = Join-Path -Path (Join-Path -Path $targetDir -ChildPath "split_files") -ChildPath $file.Name
        Convert-AdGuardToPiHole -inputFile $sourcePath -outputFile $targetPath
    }
}

# Process split_by_source subdirectory
$splitSourceDir = Join-Path $sourceDir "split_by_source"
if (Test-Path $splitSourceDir) {
    $files = Get-ChildItem -Path $splitSourceDir -File
    foreach ($file in $files) {
        $sourcePath = $file.FullName
        $targetPath = Join-Path -Path (Join-Path -Path $targetDir -ChildPath "split_by_source") -ChildPath $file.Name
        Convert-AdGuardToPiHole -inputFile $sourcePath -outputFile $targetPath
    }
}

Write-Host ""
Write-Host "Conversion complete! PiHole files are in: $targetDir"
Write-Host ""
Write-Host "To use these files in PiHole:"
Write-Host "1. Copy the .txt files to your PiHole server"
Write-Host "2. Add them as blocklists in PiHole admin panel"
Write-Host "3. Run 'pihole -g' to update gravity"
