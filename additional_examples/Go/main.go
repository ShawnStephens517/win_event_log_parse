package main


package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/masterzen/winrm"
	"github.com/StackExchange/wmi"
)

// Win32_NTLogEvent represents the WMI class
type Win32_NTLogEvent struct {
	EventCode int
	Message   string
}

func main() {
	// Define the IP range and log types
	startIP := "192.168.1.2"
	endIP := "192.168.1.253"
	logTypes := []string{"System", "Application", "Security"}

	// Split the IPs to get the octets
	startIPOctets := strings.Split(startIP, ".")
	endIPOctets := strings.Split(endIP, ".")

	// Extract base and last octets
	baseIP := strings.Join(startIPOctets[0:3], ".")
	startLastOctet := startIPOctets[3]
	endLastOctet := endIPOctets[3]

	// Convert last octets to int and loop through the range
	for lastOctet := startLastOctet; lastOctet <= endLastOctet; lastOctet++ {
		currentIP := fmt.Sprintf("%s.%s", baseIP, lastOctet)

		// Create WinRM client
		endpoint := winrm.NewEndpoint(currentIP, 5985, false, false, nil, nil, nil, 0)
		client, err := winrm.NewClient(endpoint, "username", "password")
		if err != nil {
			log.Printf("%s is not responding, skipping. Error: %v\n", currentIP, err)
			continue
		}

		// Test Connection
		_, err = client.Run("echo test", os.Stdout, os.Stderr)
		if err != nil {
			log.Printf("Failed to connect to %s, skipping. Error: %v\n", currentIP, err)
			continue
		}

		// Fetch logs
		for _, logType := range logTypes {
			var dst []Win32_NTLogEvent
			query := fmt.Sprintf("SELECT * FROM Win32_NTLogEvent WHERE Logfile = '%s'", logType)
			err := wmi.Query(query, &dst)
			if err != nil {
				log.Printf("Failed to query WMI: %v\n", err)
				continue
			}

			// Process the logs
			logContents := ""
			for _, event := range dst {
				logContents += fmt.Sprintf("EventID: %d - %s\n", event.EventCode, event.Message)
			}

			// Save logs to file
			remoteShare := "//fileserver/sharedfolder/"
			fileName := fmt.Sprintf("%s%s-%s-Log.txt", remoteShare, currentIP, logType)
			err = os.WriteFile(fileName, []byte(logContents), 0644)
			if err != nil {
				log.Printf("Failed to write to file: %v\n", err)
			}
			fmt.Printf("%s logs saved to %s\n", logType, fileName)
		}
	}
}
