# Script to remove duplicates from large text files
$InputFile = "C:\Users\dariu\Desktop\BlockList.txt"
$OutputFile = "C:\Users\dariu\Desktop\BlockList_unique.txt"
$Hashset = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

Write-Host "Reading input file and removing duplicates..."
$Reader = [System.IO.StreamReader]::new($InputFile)
$Writer = [System.IO.StreamWriter]::new($OutputFile)

$lineCount = 0
$duplicateCount = 0

while ($null -ne ($line = $Reader.ReadLine())) {
    $lineCount++
    if ($line.Trim() -ne "") {  # Skip empty lines
        if ($Hashset.Add($line)) {
            $Writer.WriteLine($line)
        } else {
            $duplicateCount++
        }
    }
    
    if ($lineCount % 10000 -eq 0) {
        Write-Host "Processed $lineCount lines, removed $duplicateCount duplicates..."
    }
}

$Reader.Close()
$Writer.Close()

Write-Host "Complete! Processed $lineCount total lines."
Write-Host "Removed $duplicateCount duplicate entries."
Write-Host "Unique entries written to: $OutputFile"
