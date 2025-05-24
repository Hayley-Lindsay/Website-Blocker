import os
import sys
import ctypes
import platform
import tkinter as tk
from tkinter import messagebox

# List of websites to block - add your distracting sites here
BLOCKED_SITES = [
    "www.doordash.com", "doordash.com",
    "www.ubereats.com", "ubereats.com",
    "www.grubhub.com", "grubhub.com",
]

# Custom error message
ERROR_MESSAGE = "Cook some food fatass"

# Path to the hosts file
if platform.system() == "Windows":
    HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
elif platform.system() in ["Darwin", "Linux"]:  # macOS or Linux
    HOSTS_PATH = "/etc/hosts"
else:
    print("Unsupported operating system")
    sys.exit(1)

# IP address to redirect to (localhost)
REDIRECT = "127.0.0.1"


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # On Unix systems, root has UID 0
            return os.geteuid() == 0
    except:
        return False


def block_websites():
    """Add website redirects to the hosts file."""
    if not is_admin():
        print("This script needs administrator privileges to modify the hosts file.")
        print("Please run it as administrator/root.")
        return False

    try:
        # Read current hosts file
        with open(HOSTS_PATH, 'r') as file:
            content = file.read()

        # Check if sites are not already blocked
        sites_to_add = []
        for site in BLOCKED_SITES:
            if not any(
                    line.strip().endswith(site) for line in content.splitlines() if not line.strip().startswith("#")):
                sites_to_add.append(f"{REDIRECT} {site}")

        if not sites_to_add:
            print("All sites are already blocked!")
            return True

        # Add the sites to the hosts file
        with open(HOSTS_PATH, 'a') as file:
            file.write("\n# Added by website blocker script\n")
            for entry in sites_to_add:
                file.write(entry + "\n")

        print(f"Successfully blocked {len(sites_to_add)} websites!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def unblock_websites():
    """Remove website redirects from the hosts file."""
    if not is_admin():
        print("This script needs administrator privileges to modify the hosts file.")
        print("Please run it as administrator/root.")
        return False

    try:
        # Read current hosts file
        with open(HOSTS_PATH, 'r') as file:
            lines = file.readlines()

        # Remove lines that block our sites
        with open(HOSTS_PATH, 'w') as file:
            for line in lines:
                if not any(site in line for site in BLOCKED_SITES):
                    file.write(line)

        print("Successfully unblocked websites!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def create_custom_browser_error():
    """Create a simple HTML page that will serve as the error message and set up a local server."""
    error_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_page")
    os.makedirs(error_dir, exist_ok=True)

    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Site Blocked</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f8f8f8;
        }}
        .message {{
            padding: 40px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="message">{ERROR_MESSAGE}</div>
</body>
</html>'''

    html_path = os.path.join(error_dir, "blocked.html")
    with open(html_path, "w") as f:
        f.write(html_content)

    print(f"Created error page at {html_path}")

    # Create a simple redirect server script
    server_script = '''import http.server
import socketserver
import sys

PORT = 80
MESSAGE = "Cook some food fatass"

class RedirectHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Site Blocked</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f8f8f8;
        }}
        .message {{
            padding: 40px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="message">{MESSAGE}</div>
</body>
</html>"""

        self.wfile.write(html.encode())

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), RedirectHandler) as httpd:
            print(f"Server running at http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error: {e}")
        if "Permission denied" in str(e):
            print("You need to run this script as administrator to use port 80.")
        elif "Address already in use" in str(e):
            print("Port 80 is already in use. Close any web servers or run on a different port.")
        sys.exit(1)
'''

    server_path = os.path.join(error_dir, "redirect_server.py")
    with open(server_path, "w") as f:
        f.write(server_script)

    print(f"Created redirect server script at {server_path}")
    print("To run the redirect server (requires admin privileges):")
    print(f"python {server_path}")

    # Create a batch file to run the server as admin (Windows)
    if platform.system() == "Windows":
        batch_content = f'''@echo off
echo Starting Website Blocker Redirect Server...
powershell -Command "Start-Process python -ArgumentList '{server_path}' -Verb RunAs"
'''
        batch_path = os.path.join(error_dir, "run_server.bat")
        with open(batch_path, "w") as f:
            f.write(batch_content)
        print(f"Created Windows batch file at {batch_path}")

    # Create a shell script for Unix systems
    elif platform.system() in ["Darwin", "Linux"]:
        shell_content = f'''#!/bin/bash
echo "Starting Website Blocker Redirect Server..."
sudo python3 "{server_path}"
'''
        shell_path = os.path.join(error_dir, "run_server.sh")
        with open(shell_path, "w") as f:
            f.write(shell_content)
        os.chmod(shell_path, 0o755)  # Make executable
        print(f"Created Unix shell script at {shell_path}")

    return html_path


def show_popup(message):
    """Shows a popup with the error message."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Site Blocked", message)
    root.destroy()


def main():
    print("Website Blocker Script")
    print("---------------------")
    print("1. Block websites")
    print("2. Unblock websites")
    print("3. Test custom error message")
    print("4. Start redirect server")
    print("5. Exit")

    choice = input("Enter your choice (1-5): ")

    if choice == "1":
        block_websites()
        error_page = create_custom_browser_error()
        print("\nTo see the custom error message when visiting blocked sites:")
        print("Run this script again and choose option 4 to start the redirect server")
    elif choice == "2":
        unblock_websites()
    elif choice == "3":
        show_popup(ERROR_MESSAGE)
    elif choice == "4":
        # Start the redirect server
        error_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_page")
        server_path = os.path.join(error_dir, "redirect_server.py")

        if not os.path.exists(server_path):
            print("Error: Redirect server script not found.")
            print("Please run option 1 first to create the necessary files.")
            return

        try:
            if platform.system() == "Windows":
                # On Windows, try to run the batch file
                batch_path = os.path.join(error_dir, "run_server.bat")
                if os.path.exists(batch_path):
                    os.startfile(batch_path)
                else:
                    print(f"Running server directly. You may need to allow admin access.")
                    if is_admin():
                        os.system(f'python "{server_path}"')
                    else:
                        print("This option requires admin privileges. Please run the script as administrator.")
            else:
                # On Unix, try to run the shell script
                shell_path = os.path.join(error_dir, "run_server.sh")
                if os.path.exists(shell_path):
                    os.system(f'"{shell_path}"')
                else:
                    print(f"Running server directly. You may need to enter your password.")
                    os.system(f'sudo python3 "{server_path}"')
        except Exception as e:
            print(f"Error starting server: {e}")
    elif choice == "5":
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
