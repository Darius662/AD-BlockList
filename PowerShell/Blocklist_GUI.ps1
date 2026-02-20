#requires -Version 5.1
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Windows.Forms

# Create the main window using Windows Forms
$form = New-Object System.Windows.Forms.Form
$form.Text = "AD-BlockList Manager"
$form.Size = New-Object System.Drawing.Size(1000, 800)
$form.StartPosition = "CenterScreen"
$form.BackColor = [System.Drawing.Color]::FromArgb(45, 45, 48)
$form.ForeColor = [System.Drawing.Color]::White
$form.Font = New-Object System.Drawing.Font("Segoe UI", 10)

# Header
$header = New-Object System.Windows.Forms.Panel
$header.Size = New-Object System.Drawing.Size(1000, 80)
$header.BackColor = [System.Drawing.Color]::FromArgb(0, 122, 204)
$header.Dock = [System.Windows.Forms.DockStyle]::Top

$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = "AD-BlockList Management Tool"
$titleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 20, [System.Drawing.FontStyle]::Bold)
$titleLabel.ForeColor = [System.Drawing.Color]::White
$titleLabel.Location = New-Object System.Drawing.Point(20, 15)
$titleLabel.Size = New-Object System.Drawing.Size(500, 40)
$header.Controls.Add($titleLabel)

$subtitleLabel = New-Object System.Windows.Forms.Label
$subtitleLabel.Text = "Manage, clean, convert, and download blocklist files"
$subtitleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$subtitleLabel.ForeColor = [System.Drawing.Color]::FromArgb(200, 200, 200)
$subtitleLabel.Location = New-Object System.Drawing.Point(20, 50)
$subtitleLabel.Size = New-Object System.Drawing.Size(400, 20)
$header.Controls.Add($subtitleLabel)

$form.Controls.Add($header)

# Main content panel with scroll
$contentPanel = New-Object System.Windows.Forms.Panel
$contentPanel.Location = New-Object System.Drawing.Point(0, 80)
$contentPanel.Size = New-Object System.Drawing.Size(980, 500)
$contentPanel.AutoScroll = $true
$form.Controls.Add($contentPanel)

$yPos = 20

# Helper function to create section headers
function Add-SectionHeader($text, $y) {
    $label = New-Object System.Windows.Forms.Label
    $label.Text = $text
    $label.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    $label.ForeColor = [System.Drawing.Color]::FromArgb(0, 122, 204)
    $label.Location = New-Object System.Drawing.Point(20, $y)
    $label.Size = New-Object System.Drawing.Size(900, 30)
    $contentPanel.Controls.Add($label)
    return $y + 35
}

# Helper function to create text boxes with browse button
function Add-FileSelector($label, $defaultValue, $y, [switch]$isFolder) {
    $lbl = New-Object System.Windows.Forms.Label
    $lbl.Text = $label
    $lbl.Location = New-Object System.Drawing.Point(20, $y)
    $lbl.Size = New-Object System.Drawing.Size(200, 20)
    $contentPanel.Controls.Add($lbl)
    
    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Text = $defaultValue
    $textY = $y + 22
    $textBox.Location = New-Object System.Drawing.Point(20, $textY)
    $textBox.Size = New-Object System.Drawing.Size(700, 25)
    $textBox.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $textBox.ForeColor = [System.Drawing.Color]::White
    $textBox.BorderStyle = "FixedSingle"
    $contentPanel.Controls.Add($textBox)
    
    $browseBtn = New-Object System.Windows.Forms.Button
    $browseBtn.Text = "Browse..."
    $btnY = $y + 20
    $browseBtn.Location = New-Object System.Drawing.Point(730, $btnY)
    $browseBtn.Size = New-Object System.Drawing.Size(100, 28)
    $browseBtn.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $browseBtn.ForeColor = [System.Drawing.Color]::White
    $browseBtn.FlatStyle = "Flat"
    $browseBtn.Add_Click({
        if ($isFolder) {
            $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
            if ($folderBrowser.ShowDialog() -eq "OK") {
                $textBox.Text = $folderBrowser.SelectedPath
            }
        } else {
            $fileBrowser = New-Object System.Windows.Forms.OpenFileDialog
            $fileBrowser.Filter = "Text files (*.txt)|*.txt|All files (*.*)|*.*"
            if ($fileBrowser.ShowDialog() -eq "OK") {
                $textBox.Text = $fileBrowser.FileName
            }
        }
    })
    $contentPanel.Controls.Add($browseBtn)
    
    return $textBox, ($y + 55)
}

# Helper function to create action buttons
function Add-ActionButton($text, $y, $clickAction) {
    $btn = New-Object System.Windows.Forms.Button
    $btn.Text = $text
    $btn.Location = New-Object System.Drawing.Point(730, $y)
    $btn.Size = New-Object System.Drawing.Size(200, 50)
    $btn.BackColor = [System.Drawing.Color]::FromArgb(0, 122, 204)
    $btn.ForeColor = [System.Drawing.Color]::White
    $btn.FlatStyle = "Flat"
    $btn.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
    $btn.Add_Click($clickAction)
    $contentPanel.Controls.Add($btn)
    return $btn
}

# SECTION 1: Remove Duplicates
$yPos = Add-SectionHeader "1. Remove Duplicates from Blocklist" $yPos
$txtDupInput, $yPos = Add-FileSelector "Input file (large blocklist):" "C:\temp\blocklist.txt" $yPos
$txtDupOutput, $yPos = Add-FileSelector "Output file (deduplicated):" "C:\temp\blocklist_unique.txt" $yPos
$btnDup = Add-ActionButton "Remove Duplicates" ($yPos - 50) {
    $inputFile = $txtDupInput.Text
    $outputFile = $txtDupOutput.Text
    
    if (!(Test-Path $inputFile)) {
        [System.Windows.Forms.MessageBox]::Show("Input file not found!", "Error", "OK", "Error")
        return
    }
    
    $btnDup.Enabled = $false
    $btnDup.Text = "Processing..."
    $logBox.AppendText("`r`n=== Removing Duplicates ===`r`n")
    $logBox.AppendText("Input: $inputFile`r`n")
    $logBox.AppendText("Output: $outputFile`r`n")
    
    try {
        $seen = [System.Collections.Generic.HashSet[string]]::new()
        $reader = [System.IO.StreamReader]::new($inputFile)
        $writer = [System.IO.StreamWriter]::new($outputFile)
        $count = 0
        $unique = 0
        
        while ($null -ne ($line = $reader.ReadLine())) {
            $count++
            if ($count % 10000 -eq 0) {
                $logBox.AppendText("Processed $count lines...`r`n")
                [System.Windows.Forms.Application]::DoEvents()
            }
            
            $trimmed = $line.Trim()
            if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
            
            if ($seen.Add($trimmed)) {
                $writer.WriteLine($trimmed)
                $unique++
            }
        }
        
        $reader.Close()
        $writer.Close()
        
        $logBox.AppendText("`r`nComplete! Processed $count lines, $unique unique entries.`r`n")
        [System.Windows.Forms.MessageBox]::Show("Removed duplicates successfully!`nProcessed $count lines, kept $unique unique entries.", "Success", "OK", "Information")
    }
    catch {
        $logBox.AppendText("`r`nERROR: $_`r`n")
        [System.Windows.Forms.MessageBox]::Show("Error: $_", "Error", "OK", "Error")
    }
    finally {
        $btnDup.Enabled = $true
        $btnDup.Text = "Remove Duplicates"
    }
}

$yPos += 20

# SECTION 2: Clean Blocklist
$yPos = Add-SectionHeader "2. Clean Blocklist (Remove Comments)" $yPos
$txtCleanInput, $yPos = Add-FileSelector "Input file (with comments):" "C:\temp\blocklist_unique.txt" $yPos
$txtCleanOutput, $yPos = Add-FileSelector "Output file (cleaned):" "C:\temp\blocklist_clean.txt" $yPos
$btnClean = Add-ActionButton "Clean Blocklist" ($yPos - 50) {
    $inputFile = $txtCleanInput.Text
    $outputFile = $txtCleanOutput.Text
    
    if (!(Test-Path $inputFile)) {
        [System.Windows.Forms.MessageBox]::Show("Input file not found!", "Error", "OK", "Error")
        return
    }
    
    $btnClean.Enabled = $false
    $btnClean.Text = "Processing..."
    $logBox.AppendText("`r`n=== Cleaning Blocklist ===`r`n")
    
    try {
        $reader = [System.IO.StreamReader]::new($inputFile)
        $writer = [System.IO.StreamWriter]::new($outputFile)
        $count = 0
        $kept = 0
        
        while ($null -ne ($line = $reader.ReadLine())) {
            $count++
            if ($count % 10000 -eq 0) {
                $logBox.AppendText("Processed $count lines...`r`n")
                [System.Windows.Forms.Application]::DoEvents()
            }
            
            $trimmed = $line.Trim()
            
            # Skip comments and empty lines
            if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
            if ($trimmed.StartsWith("!")) { continue }
            if ($trimmed.StartsWith("#")) { continue }
            if ($trimmed.StartsWith("//")) { continue }
            if ($trimmed -match "^:.*:$") { continue }
            
            $writer.WriteLine($trimmed)
            $kept++
        }
        
        $reader.Close()
        $writer.Close()
        
        $logBox.AppendText("`r`nComplete! Processed $count lines, kept $kept entries.`r`n")
        [System.Windows.Forms.MessageBox]::Show("Cleaned successfully!`nRemoved comments from $count lines, kept $kept entries.", "Success", "OK", "Information")
    }
    catch {
        $logBox.AppendText("`r`nERROR: $_`r`n")
        [System.Windows.Forms.MessageBox]::Show("Error: $_", "Error", "OK", "Error")
    }
    finally {
        $btnClean.Enabled = $true
        $btnClean.Text = "Clean Blocklist"
    }
}

$yPos += 20

# SECTION 3: Convert to PiHole
$yPos = Add-SectionHeader "3. Convert AdGuard to PiHole Format" $yPos
$txtConvertInput, $yPos = Add-FileSelector -isFolder "AdGuard folder (source):" "C:\temp\AdGuard-BlockLists\AdGuard-Home" $yPos
$txtConvertOutput, $yPos = Add-FileSelector -isFolder "PiHole folder (destination):" "C:\temp\AdGuard-BlockLists\PiHole" $yPos
$btnConvert = Add-ActionButton "Convert to PiHole" ($yPos - 50) {
    $sourceDir = $txtConvertInput.Text
    $targetDir = $txtConvertOutput.Text
    
    if (!(Test-Path $sourceDir)) {
        [System.Windows.Forms.MessageBox]::Show("Source folder not found!", "Error", "OK", "Error")
        return
    }
    
    $btnConvert.Enabled = $false
    $btnConvert.Text = "Converting..."
    $logBox.AppendText("`r`n=== Converting to PiHole Format ===`r`n")
    $logBox.AppendText("Source: $sourceDir`r`n")
    $logBox.AppendText("Destination: $targetDir`r`n`r`n")
    
    try {
        # Create target directory
        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        # Process main files
        $mainFiles = @("BlockList.txt", "BlockList_clean.txt", "BlockList_unique.txt", "Romanian_Complete_Blocklist.txt")
        foreach ($file in $mainFiles) {
            $sourcePath = Join-Path $sourceDir $file
            if (Test-Path $sourcePath) {
                $logBox.AppendText("Converting $file...`r`n")
                [System.Windows.Forms.Application]::DoEvents()
                
                $targetPath = Join-Path $targetDir $file
                $reader = [System.IO.StreamReader]::new($sourcePath)
                $writer = [System.IO.StreamWriter]::new($targetPath)
                
                while ($null -ne ($line = $reader.ReadLine())) {
                    $trimmed = $line.Trim()
                    if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
                    if ($trimmed.StartsWith("!")) { continue }
                    
                    # Convert AdGuard format to PiHole
                    $domain = $trimmed
                    if ($domain.StartsWith("||")) {
                        $domain = $domain.Substring(2)
                    }
                    if ($domain.EndsWith("^")) {
                        $domain = $domain.Substring(0, $domain.Length - 1)
                    }
                    if ($domain.Contains("^$")) {
                        $domain = $domain.Split("^$")[0]
                    }
                    
                    if ($domain -match "^[a-zA-Z0-9]" -and $domain.Contains(".")) {
                        $writer.WriteLine($domain)
                    }
                }
                
                $reader.Close()
                $writer.Close()
            }
        }
        
        $logBox.AppendText("`r`nConversion complete!`r`n")
        [System.Windows.Forms.MessageBox]::Show("Conversion completed successfully!", "Success", "OK", "Information")
    }
    catch {
        $logBox.AppendText("`r`nERROR: $_`r`n")
        [System.Windows.Forms.MessageBox]::Show("Error: $_", "Error", "OK", "Error")
    }
    finally {
        $btnConvert.Enabled = $true
        $btnConvert.Text = "Convert to PiHole"
    }
}

$yPos += 20

# SECTION 4: Download Blocklists
$yPos = Add-SectionHeader "4. Download Blocklists from GitHub" $yPos
$lblDownload = New-Object System.Windows.Forms.Label
$lblDownload.Text = "Download AdGuard blocklists from official GitHub repositories"
$lblDownload.Location = New-Object System.Drawing.Point(20, $yPos)
$lblDownload.Size = New-Object System.Drawing.Size(700, 20)
$contentPanel.Controls.Add($lblDownload)

$btnDownload = New-Object System.Windows.Forms.Button
$btnDownload.Text = "Download All"
$btnYPos = $yPos - 5
$btnDownload.Location = New-Object System.Drawing.Point(730, $btnYPos)
$btnDownload.Size = New-Object System.Drawing.Size(200, 50)
$btnDownload.BackColor = [System.Drawing.Color]::FromArgb(0, 122, 204)
$btnDownload.ForeColor = [System.Drawing.Color]::White
$btnDownload.FlatStyle = "Flat"
$btnDownload.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$btnDownload.Add_Click({
    $btnDownload.Enabled = $false
    $btnDownload.Text = "Downloading..."
    $logBox.AppendText("`r`n=== Downloading Blocklists ===`r`n")
    
    try {
        $headers = @{ "User-Agent" = "PowerShell" }
        
        # Source 1: AdGuard Hostlists Registry
        $logBox.AppendText("Downloading from AdGuard Hostlists Registry...`r`n")
        $apiUrl = "https://api.github.com/repos/AdguardTeam/HostlistsRegistry/contents/assets"
        $downloadFolder = "C:\Users\dariu\Documents\GitHub\AD-BlockList\Adguard Official Lists"
        
        if (!(Test-Path $downloadFolder)) {
            New-Item -ItemType Directory -Path $downloadFolder | Out-Null
        }
        
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers
        $files = $response | Where-Object { $_.name -match "^filter_\d+\.txt$" }
        
        foreach ($file in $files) {
            $logBox.AppendText("  - $($file.name)...`r`n")
            [System.Windows.Forms.Application]::DoEvents()
            $outputPath = Join-Path $downloadFolder $file.name
            Invoke-WebRequest -Uri $file.download_url -OutFile $outputPath
        }
        
        # Source 2: AdGuard Filters
        $logBox.AppendText("`r`nDownloading from AdGuard Filters...`r`n")
        $apiUrl2 = "https://api.github.com/repos/AdguardTeam/AdguardFilters/contents/BaseFilter/sections"
        $downloadFolder2 = "C:\Users\dariu\Documents\GitHub\AD-BlockList\AdguardDNS Lists"
        
        if (!(Test-Path $downloadFolder2)) {
            New-Item -ItemType Directory -Path $downloadFolder2 | Out-Null
        }
        
        $response2 = Invoke-RestMethod -Uri $apiUrl2 -Headers $headers
        $files2 = $response2 | Where-Object { $_.type -eq "file" -and $_.name -match "\.txt$" }
        
        foreach ($file in $files2) {
            $logBox.AppendText("  - $($file.name)...`r`n")
            [System.Windows.Forms.Application]::DoEvents()
            $outputPath = Join-Path $downloadFolder2 $file.name
            Invoke-WebRequest -Uri $file.download_url -OutFile $outputPath
        }
        
        $logBox.AppendText("`r`nDownload complete!`r`n")
        [System.Windows.Forms.MessageBox]::Show("All blocklists downloaded successfully!", "Success", "OK", "Information")
    }
    catch {
        $logBox.AppendText("`r`nERROR: $_`r`n")
        [System.Windows.Forms.MessageBox]::Show("Error: $_", "Error", "OK", "Error")
    }
    finally {
        $btnDownload.Enabled = $true
        $btnDownload.Text = "Download All"
    }
})
$contentPanel.Controls.Add($btnDownload)

# Log Panel at bottom
$logPanel = New-Object System.Windows.Forms.Panel
$logPanel.Location = New-Object System.Drawing.Point(0, 600)
$logPanel.Size = New-Object System.Drawing.Size(1000, 200)
$logPanel.BackColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
$logPanel.Dock = [System.Windows.Forms.DockStyle]::Bottom

$logLabel = New-Object System.Windows.Forms.Label
$logLabel.Text = "Activity Log:"
$logLabel.ForeColor = [System.Drawing.Color]::FromArgb(0, 122, 204)
$logLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$logLabel.Location = New-Object System.Drawing.Point(10, 5)
$logLabel.Size = New-Object System.Drawing.Size(200, 20)
$logPanel.Controls.Add($logLabel)

$logBox = New-Object System.Windows.Forms.RichTextBox
$logBox.Location = New-Object System.Drawing.Point(10, 30)
$logBox.Size = New-Object System.Drawing.Size(970, 160)
$logBox.BackColor = [System.Drawing.Color]::FromArgb(45, 45, 48)
$logBox.ForeColor = [System.Drawing.Color]::White
$logBox.Font = New-Object System.Drawing.Font("Consolas", 9)
$logBox.ReadOnly = $true
$logBox.Multiline = $true
$logBox.ScrollBars = "Vertical"
$logBox.BorderStyle = "FixedSingle"
$logBox.Text = "AD-BlockList Manager ready.`r`nSelect an operation above to begin.`r`n"
$logPanel.Controls.Add($logBox)

$form.Controls.Add($logPanel)

# Status bar
$statusBar = New-Object System.Windows.Forms.StatusStrip
$statusLabel = New-Object System.Windows.Forms.ToolStripStatusLabel
$statusLabel.Text = " Ready"
$statusBar.Items.Add($statusLabel)
$form.Controls.Add($statusBar)

# Show the form
$form.Add_Shown({ $form.Activate() })
[void]$form.ShowDialog()
