# Define the IP range
$startIP = "192.168.1.2"
$endIP = "192.168.1.253"

# Remote file share path
$remoteShare = "\\fileserver\sharedfolder"

# Log types to capture
$logTypes = @("System", "Application", "Security")

# Parse the IPs to get the octets
$startIPOctets = $startIP.Split('.')
$endIPOctets = $endIP.Split('.')

# Extract the first three octets and last octet
$baseIP = [string]::Join('.', $startIPOctets[0..2])
$startLastOctet = [int]$startIPOctets[3]
$endLastOctet = [int]$endIPOctets[3]

# Loop through the range of IPs
for ($lastOctet = $startLastOctet; $lastOctet -le $endLastOctet; $lastOctet++) {
    $currentIP = "$baseIP.$lastOctet"

    # Check for host liveliness
    if (Test-Connection -ComputerName $currentIP -Count 1 -Quiet) {
        Write-Host "Fetching logs from $currentIP"

        # Loop through each log type
        foreach ($logType in $logTypes) {
            try {
                $query = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='$logType'"
                $events = Get-WmiObject -Query $query -ComputerName $currentIP

                # Prepare text content
                $content = @()
                foreach ($event in $events) {
                    $content += "EventID: $($event.EventCode) - $($event.Message)"
                }

                # Define filename
                $filename = "$remoteShare\$currentIP-$logType-Log.txt"

                # Write to remote file
                $content | Out-File -FilePath $filename -Append

                Write-Host "$logType logs saved to $filename"
            } catch {
                Write-Host "Failed to retrieve or save $logType logs from $currentIP : $_"
            }
        }
    } else {
        Write-Host "$currentIP is not responding, skipping."
    }
}
