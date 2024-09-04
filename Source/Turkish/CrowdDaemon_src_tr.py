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

# Save baud_rate, invert_sliders, and noise_reduction individually
def save_baud_rate():
    try:
        baud_rate = int(baud_rate_var.get())
        config['baud_rate'] = baud_rate
        save_config(config)
        messagebox.showinfo("Info", "Baud rate updated successfully!")
    except ValueError:
        messagebox.showerror("Error", "Invalid baud rate value!")

def save_invert_sliders():
    config['invert_sliders'] = invert_sliders_var.get()
    save_config(config)
    messagebox.showinfo("Info", "Invert sliders setting updated successfully!")

def save_noise_reduction():
    config['noise_reduction'] = noise_reduction_var.get()
    save_config(config)
    messagebox.showinfo("Info", "Noise reduction setting updated successfully!")

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

    # Baud Rate
    global baud_rate_var
    baud_rate_var = tk.StringVar(value=str(config.get('baud_rate', '9600')))
    tk.Label(frame, text="Baud Rate:").grid(row=len(config['slider_mapping']) + 1, column=0, padx=5, pady=5, sticky="w")
    baud_rate_entry = ttk.Entry(frame, textvariable=baud_rate_var)
    baud_rate_entry.grid(row=len(config['slider_mapping']) + 1, column=1, padx=5, pady=5, sticky="ew")
    create_styled_button(frame, "Kaydet", save_baud_rate).grid(row=len(config['slider_mapping']) + 1, column=2, padx=5, pady=5)

    # Invert Sliders
    global invert_sliders_var
    invert_sliders_var = tk.BooleanVar(value=config.get('invert_sliders', False))
    tk.Label(frame, text="Invert Sliders:").grid(row=len(config['slider_mapping']) + 2, column=0, padx=5, pady=5, sticky="w")
    invert_sliders_checkbox = ttk.Checkbutton(frame, variable=invert_sliders_var)
    invert_sliders_checkbox.grid(row=len(config['slider_mapping']) + 2, column=1, padx=5, pady=5, sticky="w")
    create_styled_button(frame, "Kaydet", save_invert_sliders).grid(row=len(config['slider_mapping']) + 2, column=2, padx=5, pady=5)

    # Noise Reduction
    global noise_reduction_var
    noise_reduction_var = tk.StringVar(value=config.get('noise_reduction', 'high'))
    tk.Label(frame, text="Noise Reduction:").grid(row=len(config['slider_mapping']) + 3, column=0, padx=5, pady=5, sticky="w")
    noise_reduction_dropdown = ttk.Combobox(frame, textvariable=noise_reduction_var)
    noise_reduction_dropdown['values'] = ['low', 'medium', 'high']
    noise_reduction_dropdown.grid(row=len(config['slider_mapping']) + 3, column=1, padx=5, pady=5, sticky="ew")
    create_styled_button(frame, "Kaydet", save_noise_reduction).grid(row=len(config['slider_mapping']) + 3, column=2, padx=5, pady=5)

    # Action buttons
    create_styled_button(frame, "Kontrol Programını Yürüt", run_deej).grid(row=len(config['slider_mapping']) + 4, column=0, columnspan=4, pady=5, sticky="ew")
    create_styled_button(frame, "Kontrol Programını Kapat ", kill_deej).grid(row=len(config['slider_mapping']) + 5, column=0, columnspan=4, pady=5, sticky="ew")

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
