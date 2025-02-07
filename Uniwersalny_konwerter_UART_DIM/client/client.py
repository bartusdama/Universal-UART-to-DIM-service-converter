import threading
import time
import tkinter as tk
from tkinter import ttk

import pydim
from pydim import DimRpcInfo

class ClientRpc(DimRpcInfo):
    def __init__(self, service_name='CAEN/RPC', gui=None):
        super().__init__(service_name, 'C', 'C', None)
        self.response = None
        self.monitoring_active = False
        self.stop_event = threading.Event()
        self.gui = gui

    def format_command(self, action, parameter, value=None):
        if value:
            return f"$BD:00,CH:0,CMD:{action},PAR:{parameter},VAL:{value}\n"
        elif action:
            return f"$BD:00,CH:0,CMD:{action},PAR:{parameter}\n"

    def extract_value(self, response):
        val_pos = response.find('VAL:')
        if val_pos != -1:
            raw_value = response[val_pos + 4:]
            return raw_value.lstrip('0') or '0'
        else:
            return 'VAL not found'

    def send_command(self, action, parameter, value=None):
        command = self.format_command(action, parameter, value)
        self.setData(command)
        self.response = self.extract_value(self.getString())
        time.sleep(1)
        return self.response if self.response else 'No response'

    def send_on_off(self, command):
        self.setData(command)
        response = self.getString()

    def monitor_commands(self):
        if self.monitoring_active:
            print("Monitoring is already active")
            return

        self.monitoring_active = True
        print("Started monitoring commands.")

        commands = [
            "$BD:00,CMD:MON,CH:0,PAR:VSET\n",
            "$BD:00,CMD:MON,CH:0,PAR:ISET\n",
            "$BD:00,CMD:MON,CH:0,PAR:RUP\n",
            "$BD:00,CMD:MON,CH:0,PAR:RDW\n",
        ]

        try:
            while not self.stop_event.is_set():
                for command, label in zip(
                    commands,
                    [
                        self.gui.voltage_label,
                        self.gui.current_label,
                        self.gui.ramp_up,
                        self.gui.ramp_down,
                    ],
                ):
                    self.setData(command)
                    response = self.extract_value(self.getString())
                    label.config(text=response)
                    time.sleep(1)
                time.sleep(10)
        finally:
            self.monitoring_active = False
            print("Stopped monitoring commands.")

class PowerSupplyGUI:
    def __init__(self, root):
        root.title('CEAN SUPPLY')
        root.geometry('400x550')

        self.client_rpc = None

        tk.Label(root, text="OUTPUT VOLTAGE [V]").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.voltage_label = tk.Label(root, text="0.0", relief="sunken", width=15)
        self.voltage_label.grid(row=1, column=0, padx=10, pady=5)

        tk.Label(root, text="OUTPUT CURRENT [uA]").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.current_label = tk.Label(root, text="0.0", relief="sunken", width=15)
        self.current_label.grid(row=1, column=1, padx=10, pady=5)

        self.voltage_var = tk.StringVar(value="0000.0")
        self.current_var = tk.StringVar(value="0000.00")

        tk.Label(root, text="SET VOLTAGE [V]").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.voltage_entry = tk.Entry(root, textvariable=self.voltage_var)
        self.voltage_entry.grid(row=3, column=0, padx=10, pady=5)

        tk.Label(root, text="SET CURRENT [uA]").grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.current_entry = tk.Entry(root, textvariable=self.current_var)
        self.current_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(root, text="RAMP TRIB:").grid(row=5, column=0, padx=10, pady=5, sticky="w")

        tk.Label(root, text="UP").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.ramp_up = tk.Label(root, text="0.0", relief="sunken", width=15)
        self.ramp_up.grid(row=6, column=1, padx=10, pady=5)
        tk.Label(root, text="[V/Sec]").grid(row=6, column=2, padx=10, pady=5, sticky="w")

        tk.Label(root, text="DOWN").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.ramp_down = tk.Label(root, text="0.0", relief="sunken", width=15)
        self.ramp_down.grid(row=7, column=1, padx=10, pady=5)
        tk.Label(root, text="[V/Sec]").grid(row=7, column=2, padx=10, pady=5, sticky="w")

        voltage_button = ttk.Button(root, text="SET", command=self.set_voltage)
        voltage_button.grid(row=4, column=0, padx=10, pady=10)

        current_button = ttk.Button(root, text="SET", command=self.set_current)
        current_button.grid(row=4, column=1, padx=10, pady=10)

        kill_button = ttk.Button(root, text="KILL", command=self.kill_cean)
        kill_button.grid(row=10, column=0, padx=10, pady=10)

        frame = tk.Frame(root)
        frame.grid(row=11, column=0, columnspan=3, pady=20)

        on_button = ttk.Button(frame, text="ON", command=self.power_on, width=10)
        on_button.grid(row=11, column=0, padx=10, pady=10)

        power_label = tk.Label(frame, text="POWER", font=("Arial", 10))
        power_label.grid(row=11, column=1, padx=10, pady=10)

        off_button = ttk.Button(frame, text="OFF", command=self.power_off, width=10)
        off_button.grid(row=11, column=2, padx=10, pady=10)

        dim_frame = tk.Frame(root, relief="groove", borderwidth=2)
        dim_frame.grid(row=12, column=0, columnspan=3, pady=20, padx=10, sticky="nsew")

        tk.Label(dim_frame, text="DIM ADDRESS").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.dim_address_var = tk.StringVar()
        self.dim_address_entry = tk.Entry(dim_frame, textvariable=self.dim_address_var, width=30)
        self.dim_address_entry.grid(row=1, column=0, padx=10, pady=5, columnspan=2)

        connection_label = tk.Label(dim_frame, text="CONNECTION")
        connection_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        ok_button = ttk.Button(dim_frame, text="OK", command=self.dim_connection_ok, width=10)
        ok_button.grid(row=3, column=0, padx=5, pady=5)

        false_button = ttk.Button(dim_frame, text="FALSE", command=self.dim_connection_false, width=10)
        false_button.grid(row=3, column=1, padx=5, pady=5)

    def on_closing(self):
        if self.client_rpc and self.client_rpc.stop_event:
            self.client_rpc.stop_event.set()
        root.destroy()

    def kill_cean(self):
        if self.client_rpc:
            response = "$BD:00,CMD:SET,CH:0,PAR:PDWN,VAL:KILL\n"
            self.client_rpc.send_on_off(response)
            print(response)

    def set_voltage(self):
        if self.client_rpc:
            response = self.voltage_var.get()
            self.client_rpc.send_command("SET", "VSET", response)
            print(f'set_voltage: {response}')

    def set_current(self):
        if self.client_rpc:
            response = self.current_var.get()
            self.client_rpc.send_command("SET", "ISET", response)
            print(f'set_current: {response}')

    def power_on(self):
        if self.client_rpc:
            response = "$BD:00,CMD:SET,CH:0,PAR:ON\n"
            self.client_rpc.send_on_off(response)
            print(response)

    def power_off(self):
        if self.client_rpc:
            response = "$BD:00,CMD:SET,CH:0,PAR:OFF\n"
            self.client_rpc.send_on_off(response)
            print(response)

    def dim_connection_ok(self):
        address = self.dim_address_var.get()
        pydim.dic_set_dns_node(address)
        print(f"Connected to DIM DNS at: {pydim.dic_get_dns_node()}")

        if self.client_rpc is None:
            self.client_rpc = ClientRpc("CAEN/RPC", gui=self)
        elif self.client_rpc.monitoring_active:
            print("Monitoring is already active. No new thread will be started.")
            return

        if not self.client_rpc.stop_event.is_set():
            monitoring_thread = threading.Thread(target=self.client_rpc.monitor_commands, daemon=True)
            monitoring_thread.start()

    def dim_connection_false(self):
        if self.client_rpc:
            if not self.client_rpc.stop_event.is_set():
                self.client_rpc.stop_event.set()
                print("Stopping monitoring commands...")
            while self.client_rpc.monitoring_active:
                time.sleep(0.1)
            self.client_rpc = None

root = tk.Tk()
app = PowerSupplyGUI(root)

root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
