import winrm
import wmi
import getpass
import subprocess
import shutil
import os

def get_credentials():
    username = input("Please enter your username: ")
    password = getpass.getpass("Please enter your password: ")
    return username, password

def test_connection(ip, username, password):
    try:
        session = winrm.Session(f'http://{ip}:5985/wsman', auth=(username, password))
        result = session.run_ps("echo test")
        return result.status_code == 0
    except:
        return False

def fetch_logs(ip, log_types, username, password):
    logs = {}
    c = wmi.WMI(computer=ip, user=username, password=password)
    for log_type in log_types:
        # Create .evtx files using PowerShell
        ps_command = f"wevtutil epl {log_type} C:\\path\\to\\logs\\{log_type}.evtx"
        subprocess.run(['powershell', '-command', ps_command], capture_output=True)

        # Copy the .evtx file
        src_file = f"C:\\path\\to\\logs\\{log_type}.evtx"
        dst_file = f"\\\\fileserver\\sharedfolder\\{ip}-{log_type}.evtx"

        try:
            shutil.copy(src_file, dst_file)
            logs[log_type] = "Successfully copied"
        except Exception as e:
            logs[log_type] = f"Failed to copy: {e}"
    return logs


def main():
    # Define IP range and log types
    start_ip = '192.168.1.2'
    end_ip = '192.168.1.253'
    log_types = ['System', 'Application', 'Security']
    base_ip = '.'.join(start_ip.split('.')[:-1])
    start_last_octet = int(start_ip.split('.')[-1])
    end_last_octet = int(end_ip.split('.')[-1])

    username, password = get_credentials()

    for last_octet in range(start_last_octet, end_last_octet + 1):
        current_ip = f"{base_ip}.{last_octet}"

        if test_connection(current_ip, username, password):
            print(f"Fetching logs from {current_ip}")
            logs = fetch_logs(current_ip, log_types, username, password)

            # Update remote_share to your file share path
        else:
            print(f"{current_ip} is not responding, skipping.")

if __name__ == '__main__':
    main()
