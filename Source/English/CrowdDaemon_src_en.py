import yaml
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os
import subprocess
import serial.tools.list_ports  # For listing COM ports

# Load the YAML configuration file
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

# Save the YAML configuration file
def save_config(config):
    with open("config.yaml", "w") as file:
        yaml.dump(config, file, default_flow_style=False)

# Get a list of running applications
def get_running_apps():
    apps = []
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            if proc.info['name']:
                apps.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(set(apps))

# Get a list of available COM ports
def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Update the application name for a specific slider
def update_app(slider_index, app_name):
    config['slider_mapping'][slider_index] = app_name
    save_config(config)
    load_ui()

# Execute deej.exe
def run_deej():
    deej_path = "deej.exe"
    if os.path.exists(deej_path):
        subprocess.Popen(deej_path)
    else:
        messagebox.showerror("Error", f"{deej_path} app not found on the path. Make sure you are in the same dir with Deej.exe.")

# Kill deej.exe
def kill_deej():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == "deej.exe":
            proc.terminate()
            proc.wait()
            messagebox.showinfo("Info", "Deej app is closed")
            return
    messagebox.showerror("Error", "No running Deej apps found!")

# Refresh the list of running applications
def refresh_apps():
    app_dropdown['values'] = get_running_apps()

# Refresh the list of COM ports
def refresh_com_ports():
    com_port_dropdown['values'] = get_com_ports()
    com_port_var.set('')  # Clear the current selection

# Save the selected COM port
def save_com_port():
    selected_com_port = com_port_var.get()
    if selected_com_port:
        config['com_port'] = selected_com_port
        save_config(config)
        messagebox.showinfo("Info", f"COM Port set to {selected_com_port}!")
    else:
        messagebox.showerror("Error", "COM Port not specified!")

# Set slider 1 to "master"
def set_slider_1_to_master():
    config['slider_mapping'][1] = 'master'
    save_config(config)
    load_ui()

# Create a styled frame for better appearance
def create_styled_frame(parent, padding=(10, 10)):
    frame = ttk.Frame(parent, padding=padding)
    frame.grid(sticky="nsew")
    return frame

# Create a styled button
def create_styled_button(parent, text, command, padding=(5, 5)):
    button = ttk.Button(parent, text=text, command=command)
    button.grid(pady=padding[1], padx=padding[0], sticky="ew")
    return button

# Load the UI elements
def load_ui():
    for widget in frame.winfo_children():
        widget.destroy()

    slider_frame = create_styled_frame(frame, (10, 10))

    for slider_index, app_name in config['slider_mapping'].items():
        tk.Label(slider_frame, text=f"Slider {slider_index}:").grid(row=slider_index, column=0, padx=5, pady=5, sticky="w")

        app_var = tk.StringVar(value=app_name)
        app_dropdown = ttk.Combobox(slider_frame, textvariable=app_var)
        app_dropdown['values'] = get_running_apps()
        app_dropdown.grid(row=slider_index, column=1, padx=5, pady=5, sticky="ew")

        create_styled_button(slider_frame, "Update", lambda si=slider_index, av=app_var: update_app(si, av.get())).grid(row=slider_index, column=2, padx=5, pady=5)

        if slider_index == 1:
            create_styled_button(slider_frame, "Set as master volume", set_slider_1_to_master).grid(row=slider_index, column=3, padx=5, pady=5)

    # COM port selection
    com_port_frame = create_styled_frame(frame, (10, 10))
    tk.Label(com_port_frame, text=" COM Port Selector").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    
    global com_port_var
    com_port_var = tk.StringVar(value=config.get('com_port', ''))
    global com_port_dropdown
    com_port_dropdown = ttk.Combobox(com_port_frame, textvariable=com_port_var)
    com_port_dropdown['values'] = get_com_ports()
    com_port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    create_styled_button(com_port_frame, "Refresh ports", refresh_com_ports).grid(row=0, column=2, padx=5, pady=5)
    create_styled_button(com_port_frame, "Save port", save_com_port).grid(row=0, column=3, padx=5, pady=5)

    # Action buttons
    create_styled_button(frame, "Run deej", run_deej).grid(row=len(config['slider_mapping']) + 1, column=0, columnspan=4, pady=5, sticky="ew")
    create_styled_button(frame, "Close deej", kill_deej).grid(row=len(config['slider_mapping']) + 2, column=0, columnspan=4, pady=5, sticky="ew")
    print("Designed by Mert Ata Baber for CrowdDaemon")
# Initialize the main window
root = tk.Tk()
root.title("CrowdDaemon Audio Control Program")
root.geometry("700x500")  # Set initial window size

frame = create_styled_frame(root, (20, 20))

config = load_config()
load_ui()

# Make sure the frame expands with window resizing
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()