Smart Wi-Fi Extender with AI-Powered Voice Control
Overview
Welcome to the Smart Wi-Fi Extender project! This project leverages advanced AI technology and intuitive voice commands to enhance your Wi-Fi coverage, optimize network performance, and provide a seamless user experience. By combining sophisticated features and user-friendly design, this project aims to revolutionize the way you manage your Wi-Fi network.

Features
Voice Control Integration: Manage your Wi-Fi extender with simple voice commands such as “scan networks,” “connect to network,” “start extender,” and “stop extender.”
AI-Enhanced Channel Selection: Automatically selects the best Wi-Fi channel to minimize interference and enhance network performance.
Advanced Security Features: Enforces strong password policies and implements dynamic MAC address filtering to allow only authorized devices to connect.
Real-Time Network Monitoring: Displays real-time statistics on connected devices and their data usage.
User-Friendly Graphical Interface: Provides an intuitive GUI built with Tkinter for easy management and control of the Wi-Fi extender.
Scheduling Capabilities: Allows users to schedule network activities such as starting or stopping the extender at specified times.
Voice Feedback: Provides real-time voice feedback for commands and system status.
Comprehensive Logging and Notifications: Maintains a detailed log of all actions and events and notifies users of critical events and errors through graphical alerts and voice feedback.
Technologies Used
Python: Core programming language.
Tkinter: For creating the graphical user interface (GUI).
SpeechRecognition: For capturing and recognizing voice commands.
pyttsx3: For providing text-to-speech capabilities.
Subprocess: For executing system commands to manage network settings.
JSON: For managing configuration data, schedules, and authorized MAC addresses.
Threading: For implementing scheduled tasks.
Installation
Prerequisites
Make sure you have Python installed on your system. You can download it from python.org.

Dependencies
Install the required libraries using pip:

sh
Copy code
pip install SpeechRecognition pyaudio pyttsx3
Clone the Repository
Clone this repository to your local machine:

sh
Copy code
git clone https://github.com/yourusername/smart-wifi-extender.git
cd smart-wifi-extender
Usage
Run the Script:

Execute the main script:

sh
Copy code
python main.py
Graphical User Interface:

Use the GUI to scan networks, connect to networks, start and stop the extender, and schedule activities.
Click the "Voice Command" button to give voice commands.
Voice Commands:

Say commands like “scan networks,” “connect to network,” “start extender,” and “stop extender” for corresponding actions.
Key Functions
enable_mobile_hotspot(ssid, password, band): Sets up and starts the mobile hotspot with the specified SSID, password, and band.
disable_mobile_hotspot(): Stops the mobile hotspot.
scan_networks(): Scans for available Wi-Fi networks.
connect_to_network(ssid, password): Connects to the specified Wi-Fi network.
schedule_hotspot(action, time_str): Schedules the starting or stopping of the mobile hotspot.
recognize_voice_command(): Captures and processes voice commands.
process_voice_command(command, scan_and_display, connect_selected, start_extender, stop_extender): Executes the action based on the recognized voice command.
Contribution
Feel free to fork this repository and contribute by submitting a pull request. For major changes, please open an issue first to discuss what you would like to change.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
If you have any questions or suggestions, feel free to contact me at thakuradityaraj275@gmail.com
