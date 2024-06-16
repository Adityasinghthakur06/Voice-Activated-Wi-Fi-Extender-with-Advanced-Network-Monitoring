import os
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from datetime import datetime, timedelta
import threading
import json
import time
import speech_recognition as sr
import pyttsx3
import psutil

LOG_FILE = 'wifi_extender.log'
SCHEDULE_FILE = 'schedule.json'
AUTHORIZED_MACS_FILE = 'authorized_macs.json'

# Initialize the speech engine
engine = pyttsx3.init()


# Logging function
def log_action(action):
    with open(LOG_FILE, 'a') as f:
        log_entry = f"{datetime.now()}: {action}\n"
        f.write(log_entry)


# Notification function
def notify_user(message):
    messagebox.showinfo("Notification", message)


def speak_message(message):
    engine.say(message)
    engine.runAndWait()


def run_command(command):
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, shell=True)
        log_action(f"Running command: {command}")
        log_action(f"STDOUT: {result.stdout.strip()}")
        log_action(f"STDERR: {result.stderr.strip()}")
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        log_action(f"Exception: {e}")
        return "", str(e)


def enable_mobile_hotspot(ssid, password, band):
    if not is_strong_password(password):
        notify_user("Password must be at least 8 characters long and include letters and numbers.")
        speak_message("Password must be at least 8 characters long and include letters and numbers.")
        return False

    log_action(f"Setting up mobile hotspot with SSID: {ssid}, Password: {password}, Band: {band}")
    cmd_set = f'Start-Process powershell -ArgumentList "netsh wlan set hostednetwork mode=allow ssid={ssid} key={password} band={band}" -Verb RunAs'
    stdout, stderr = run_command(cmd_set)
    if stderr:
        log_action(f"Error setting SSID and key: {stderr}")
        notify_user(f"Error setting SSID and key: {stderr}")
        speak_message(f"Error setting SSID and key: {stderr}")
        return False

    cmd_start = 'Start-Process powershell -ArgumentList "netsh wlan start hostednetwork" -Verb RunAs'
    stdout, stderr = run_command(cmd_start)
    if stderr:
        log_action(f"Error starting hosted network: {stderr}")
        notify_user(f"Error starting hosted network: {stderr}")
        speak_message(f"Error starting hosted network: {stderr}")
        return False

    log_action(f"Mobile Hotspot {ssid} started successfully")
    notify_user(f"Mobile Hotspot {ssid} started successfully")
    speak_message(f"Mobile Hotspot {ssid} started successfully")
    return True


def disable_mobile_hotspot():
    log_action("Stopping Mobile Hotspot...")
    cmd_stop = 'Start-Process powershell -ArgumentList "netsh wlan stop hostednetwork" -Verb RunAs'
    stdout, stderr = run_command(cmd_stop)
    if stderr:
        log_action(f"Error stopping hosted network: {stderr}")
        notify_user(f"Error stopping hosted network: {stderr}")
        speak_message(f"Error stopping hosted network: {stderr}")
    else:
        log_action("Mobile Hotspot stopped successfully")
        notify_user("Mobile Hotspot stopped successfully")
        speak_message("Mobile Hotspot stopped successfully")


def scan_networks():
    log_action("Scanning for networks...")
    cmd_scan = 'netsh wlan show networks mode=Bssid'
    stdout, stderr = run_command(cmd_scan)
    if stderr:
        log_action(f"Error scanning networks: {stderr}")
        notify_user(f"Error scanning networks: {stderr}")
        speak_message(f"Error scanning networks: {stderr}")
        return []

    networks = []
    for line in stdout.split('\n'):
        if "SSID" in line:
            ssid = line.split(":")[1].strip()
            if ssid:
                networks.append(ssid)
    log_action(f"Found networks: {networks}")
    return networks


def connect_to_network(ssid, password):
    log_action(f"Connecting to network {ssid} with password {password}")
    profile_content = f"""
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
"""
    with open(f"{ssid}.xml", "w") as file:
        file.write(profile_content)

    cmd_profile = f'netsh wlan add profile filename="{ssid}.xml" interface=Wi-Fi'
    stdout, stderr = run_command(cmd_profile)
    os.remove(f"{ssid}.xml")
    if stderr:
        log_action(f"Error adding profile: {stderr}")
        notify_user(f"Error adding profile: {stderr}")
        speak_message(f"Error adding profile: {stderr}")
        return False

    cmd_connect = f'netsh wlan connect name="{ssid}" ssid="{ssid}"'
    stdout, stderr = run_command(cmd_connect)
    if stderr:
        log_action(f"Error connecting to network: {stderr}")
        notify_user(f"Error connecting to network: {stderr}")
        speak_message(f"Error connecting to network: {stderr}")
        return False

    log_action(f"Successfully connected to {ssid}")
    notify_user(f"Successfully connected to {ssid}")
    speak_message(f"Successfully connected to {ssid}")
    return True


def check_authorized_mac():
    current_mac = get_current_mac_address()
    authorized_macs = load_authorized_macs()
    if current_mac in authorized_macs:
        return True
    else:
        log_action(f"Unauthorized MAC address detected: {current_mac}")
        notify_user(f"Unauthorized MAC address detected: {current_mac}")
        speak_message(f"Unauthorized MAC address detected: {current_mac}")
        return False


def get_current_mac_address():
    # Mocked current MAC address
    return "00:11:22:33:44:55"


def load_authorized_macs():
    if os.path.exists(AUTHORIZED_MACS_FILE):
        with open(AUTHORIZED_MACS_FILE, 'r') as f:
            return json.load(f)
    return ['00:11:22:33:44:55', '66:77:88:99:AA:BB']


def is_strong_password(password):
    return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)


# AI-based Auto-Channel Selection functions
def scan_wifi_channels():
    channels = range(1, 12)
    scan_results = {}

    for channel in channels:
        os.system(f"iwconfig wlan0 channel {channel}")
        time.sleep(1)  # Wait for the channel to switch
        result = os.popen("iwlist wlan0 scan").read()
        scan_results[channel] = result.count("Quality=")  # Count the number of networks

    return scan_results


def analyze_channels(scan_results):
    best_channel = min(scan_results, key=scan_results.get)
    return best_channel


def set_best_channel(best_channel):
    os.system(f"iwconfig wlan0 channel {best_channel}")
    log_action(f"Switched to the best channel: {best_channel}")
    notify_user(f"Switched to the best channel: {best_channel}")
    speak_message(f"Switched to the best channel: {best_channel}")


# Voice Command Functions
def recognize_voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for voice commands...")
        speak_message("Listening for voice commands...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            log_action(f"Recognized command: {command}")
            speak_message(f"Recognized command: {command}")
            return command.lower()
        except sr.UnknownValueError:
            log_action("Could not understand the audio")
            notify_user("Could not understand the audio")
            speak_message("Could not understand the audio")
        except sr.RequestError as e:
            log_action(f"Could not request results; {e}")
            notify_user(f"Could not request results; {e}")
            speak_message(f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            log_action("Listening timed out")
            notify_user("Listening timed out")
            speak_message("Listening timed out")

    return ""


def process_voice_command(command, scan_and_display, connect_selected, start_extender, stop_extender):
    if "scan networks" in command:
        scan_and_display()
    elif "connect to network" in command:
        connect_selected()
    elif "start extender" in command:
        start_extender()
    elif "stop extender" in command:
        stop_extender()
    elif "set best channel" in command:
        scan_results = scan_wifi_channels()
        best_channel = analyze_channels(scan_results)
        set_best_channel(best_channel)
    else:
        log_action("Command not recognized")
        notify_user("Command not recognized")
        speak_message("Command not recognized")


def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"Battery is at {battery.percent}%"
    return "Battery status not available"


def get_connected_devices():
    cmd_connected_devices = 'arp -a'
    stdout, stderr = run_command(cmd_connected_devices)
    if stderr:
        log_action(f"Error retrieving connected devices: {stderr}")
        notify_user(f"Error retrieving connected devices: {stderr}")
        speak_message(f"Error retrieving connected devices: {stderr}")
        return []

    devices = []
    for line in stdout.split('\n'):
        if "dynamic" in line:
            devices.append(line)
    log_action(f"Connected devices: {devices}")
    return devices


def main():
    root = tk.Tk()
    root.title("Wi-Fi Extender Manager")
    root.geometry("500x600")

    def scan_and_display():
        networks = scan_networks()
        listbox.delete(0, tk.END)
        for network in networks:
            listbox.insert(tk.END, network)
        speak_message("Networks scanned successfully")

    def connect_selected():
        if not check_authorized_mac():
            return
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a network to connect.")
            speak_message("Please select a network to connect.")
            return
        ssid = listbox.get(selection[0])
        password = simpledialog.askstring("Input", f"Enter password for {ssid}:", show='*')
        if connect_to_network(ssid, password):
            messagebox.showinfo("Success", f"Successfully connected to {ssid}")
            speak_message(f"Successfully connected to {ssid}")
        else:
            messagebox.showerror("Error", f"Failed to connect to {ssid}")
            speak_message(f"Failed to connect to {ssid}")

    def start_extender():
        ext_ssid = simpledialog.askstring("Input", "Enter SSID for the extender:")
        ext_password = simpledialog.askstring("Input", "Enter password for the extender:", show='*')
        band = simpledialog.askstring("Input", "Enter band (2.4GHz/5GHz):")
        if enable_mobile_hotspot(ext_ssid, ext_password, band):
            messagebox.showinfo("Success", f"Wi-Fi extender started with SSID: {ext_ssid}")
            speak_message(f"Wi-Fi extender started with SSID: {ext_ssid}")
        else:
            messagebox.showerror("Error",
                                 "Failed to start the Mobile Hotspot. Ensure your adapter supports hosted networks and try again.")
            speak_message(
                "Failed to start the Mobile Hotspot. Ensure your adapter supports hosted networks and try again.")

    def stop_extender():
        disable_mobile_hotspot()
        messagebox.showinfo("Success", "Wi-Fi extender stopped")
        speak_message("Wi-Fi extender stopped")

    def schedule_hotspot(action, time_str):
        time_obj = datetime.strptime(time_str, "%H:%M")
        now = datetime.now()
        schedule_time = datetime(now.year, now.month, now.day, time_obj.hour, time_obj.minute)
        if schedule_time < now:
            schedule_time += timedelta(days=1)
        delay = (schedule_time - now).total_seconds()

        if action == "enable":
            threading.Timer(delay, start_extender).start()
            log_action(f"Scheduled to enable hotspot at {time_str}")
            speak_message(f"Scheduled to enable hotspot at {time_str}")
        elif action == "disable":
            threading.Timer(delay, stop_extender).start()
            log_action(f"Scheduled to disable hotspot at {time_str}")
            speak_message(f"Scheduled to disable hotspot at {time_str}")

    def save_schedule(action, time_str):
        schedule = {"action": action, "time": time_str}
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(schedule, f)
        log_action(f"Schedule saved: {schedule}")

    def load_schedule():
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f:
                schedule = json.load(f)
            log_action(f"Loaded schedule: {schedule}")
            return schedule
        return None

    def schedule_action(action):
        time_str = simpledialog.askstring("Input", "Enter time (HH:MM) to schedule:")
        if time_str:
            schedule_hotspot(action, time_str)
            save_schedule(action, time_str)
            messagebox.showinfo("Success", f"Scheduled to {action} hotspot at {time_str}")
            speak_message(f"Scheduled to {action} hotspot at {time_str}")

    def show_battery_status():
        battery_status = get_battery_status()
        messagebox.showinfo("Battery Status", battery_status)
        speak_message(battery_status)

    def show_connected_devices():
        devices = get_connected_devices()
        listbox_devices.delete(0, tk.END)
        for device in devices:
            listbox_devices.insert(tk.END, device)
        speak_message("Connected devices listed")

    schedule = load_schedule()
    if schedule:
        if schedule["action"] == "enable":
            threading.Timer(1, start_extender).start()
        elif schedule["action"] == "disable":
            threading.Timer(1, stop_extender).start()

    frame = tk.Frame(root)
    frame.pack(pady=20)

    listbox = tk.Listbox(frame, width=50, height=10)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    scan_button = tk.Button(root, text="Scan Networks", command=scan_and_display)
    scan_button.pack(pady=10)

    connect_button = tk.Button(root, text="Connect", command=connect_selected)
    connect_button.pack(pady=10)

    start_extender_button = tk.Button(root, text="Start Extender", command=start_extender)
    start_extender_button.pack(pady=10)

    stop_extender_button = tk.Button(root, text="Stop Extender", command=stop_extender)
    stop_extender_button.pack(pady=10)

    schedule_enable_button = tk.Button(root, text="Schedule Enable", command=lambda: schedule_action("enable"))
    schedule_enable_button.pack(pady=10)

    schedule_disable_button = tk.Button(root, text="Schedule Disable", command=lambda: schedule_action("disable"))
    schedule_disable_button.pack(pady=10)

    battery_status_button = tk.Button(root, text="Battery Status", command=show_battery_status)
    battery_status_button.pack(pady=10)

    connected_devices_button = tk.Button(root, text="Show Connected Devices", command=show_connected_devices)
    connected_devices_button.pack(pady=10)

    listbox_devices = tk.Listbox(root, width=50, height=10)
    listbox_devices.pack(pady=10)

    voice_command_button = tk.Button(root, text="Voice Command", command=lambda: process_voice_command(
        recognize_voice_command(), scan_and_display, connect_selected, start_extender, stop_extender))
    voice_command_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
