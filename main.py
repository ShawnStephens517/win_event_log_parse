import winrm
import wmi

# Define IP range and log types
start_ip = '192.168.1.1'
end_ip = '192.168.1.10'
log_types = ['System', 'Application', 'Security']

# Convert the base IP and last octet range
base_ip = '.'.join(start_ip.split('.')[:-1])
start_last_octet = int(start_ip.split('.')[-1])
end_last_octet = int(end_ip.split('.')[-1])

# Loop through IP range
for last_octet in range(start_last_octet, end_last_octet + 1):
    current_ip = f"{base_ip}.{last_octet}"

    # Test connection
    try:
        # Replace 'username' and 'password' with appropriate credentials
        session = winrm.Session(f'http://{current_ip}:5985/wsman', auth=('username', 'password'))
        result = session.run_ps("echo test")
        if result.status_code != 0:
            print(f"{current_ip} is not responding, skipping.")
            continue
    except:
        print(f"{current_ip} is not responding, skipping.")
        continue

    print(f"Fetching logs from {current_ip}")

    # Initialize WMI connection
    c = wmi.WMI(computer=current_ip, user="username", password="password")

    # Loop through each log type
    for log_type in log_types:
        log_entries = []
        try:
            for log in c.Win32_NTLogEvent(Logfile=log_type):
                log_entries.append(f"EventID: {log.EventCode} - {log.Message}")

            # Save logs to a file
            # Update remote_share to your file share path
            remote_share = "\\\\fileserver\\sharedfolder"
            with open(f"{remote_share}\\{current_ip}-{log_type}-Log.txt", 'a') as f:
                f.write('\n'.join(log_entries))

            print(f"{log_type} logs saved.")
        except Exception as e:
            print(f"Failed to retrieve or save {log_type} logs from {current_ip} : {e}")


