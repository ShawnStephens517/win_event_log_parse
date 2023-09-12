# Windows Event Log Copy and Clear

## About
This project is an example for performing log rotation functions
in accordance with many Defense industry standards.

This code is designed to be run on-demand or added as a scheduled task.
This repo contains python, powershell, and go examples.

### What it does

- Iterate through a range of IPs
- Copies Security, Application, and System Event Logs to a remote location
- Clears the current Logs
- Generates a new Security Event Log stating this application was ran


