# Script to remove comments and clean blocklist
$InputFile = "C:\Users\dariu\Desktop\BlockList_unique.txt"
$OutputFile = "C:\Users\dariu\Desktop\BlockList_clean.txt"

Write-Host "Cleaning blocklist - removing comments and empty lines..."
$Reader = [System.IO.StreamReader]::new($InputFile)
$Writer = [System.IO.StreamWriter]::new($OutputFile)

$lineCount = 0
$commentCount = 0
$emptyCount = 0
$keptCount = 0

while ($null -ne ($line = $Reader.ReadLine())) {
    $lineCount++
    $trimmedLine = $line.Trim()
    
    # Skip empty lines
    if ($trimmedLine -eq "") {
        $emptyCount++
        continue
    }
    
    # Skip comment lines (starting with !, #, or containing :just a comment;)
    if ($trimmedLine.StartsWith("!") -or $trimmedLine.StartsWith("#") -or $trimmedLine -match ":just a comment;") {
        $commentCount++
        continue
    }
    
    # Keep the line
    $Writer.WriteLine($line)
    $keptCount++
    
    if ($lineCount % 100000 -eq 0) {
        Write-Host "Processed $lineCount lines, kept $keptCount, removed $commentCount comments and $emptyCount empty lines..."
    }
}

$Reader.Close()
$Writer.Close()

Write-Host "Complete! Processed $lineCount total lines."
Write-Host "Removed $commentCount comment lines and $emptyCount empty lines."
Write-Host "Kept $keptCount valid blocklist entries."
Write-Host "Clean file written to: $OutputFile"
