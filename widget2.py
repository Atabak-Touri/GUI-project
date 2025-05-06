import serial
import serial.tools.list_ports
import json
import os
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

PATIENTS_FILE = "patients.json"

class ActuatorControlGUI(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load("GUI_V4.ui", None)
        self.ui.setWindowTitle("Actuator Controller")

        self.serial_port = None
        self.direction = "CW"  # Track current direction

        # Actuator Controls
        self.ui.pushButton_Run.clicked.connect(lambda: self.send_command("RUN\n"))
        self.ui.pushButton_Stop.clicked.connect(lambda: self.send_command("STOP\n"))
        self.ui.pushButton_ChangeDirection.clicked.connect(self.toggle_direction)
        self.ui.setAnglePushButton.clicked.connect(self.set_angle)
        self.ui.resetAnglePushButton.clicked.connect(self.reset_angle)
        self.ui.speedSpinBox.valueChanged.connect(self.set_speed)
        self.ui.homePosition_pushButton.clicked.connect(self.move_to_home_position)

        # Patient Management
        self.ui.savePushButton.clicked.connect(self.save_patient)
        self.ui.patientLoadPushButton.clicked.connect(self.load_patient)
        self.ui.selectPatient_radioButton.toggled.connect(self.toggle_patient_mode)
        self.ui.newPatient_radioButton.toggled.connect(self.toggle_patient_mode)

        self.ui.patientsComboBox.setEnabled(False)
        self.ui.patientLoadPushButton.setEnabled(False)
        self.ui.firstNameLineEdit.setEnabled(False)
        self.ui.lastNameLineEdit.setEnabled(False)

        self.load_patient_list()

        # Serial Port Handling
        self.refresh_ports()
        self.ui.pushButton_Connect.clicked.connect(self.connect_to_kit)
        self.ui.connect_comboBox.currentIndexChanged.connect(self.port_selected)

        # Battery status placeholder
        self.update_battery_level()

    def show(self):
        self.ui.show()

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.ui.connect_comboBox.clear()
        for port in ports:
            self.ui.connect_comboBox.addItem(port.device)
        if not ports:
            self.ui.connect_comboBox.addItem("No ports available")

    def port_selected(self):
        selected_port = self.ui.connect_comboBox.currentText()
        print(f"Selected port: {selected_port}")

    def connect_to_kit(self):
        selected_port = self.ui.connect_comboBox.currentText()
        try:
            self.serial_port = serial.Serial(selected_port, timeout=1)
            print(f"Connected to the kit on {selected_port}")
            self.ui.disconnected.setText("CONNECTED")
            self.ui.disconnected.setStyleSheet("color: green;")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.ui, "Connection Error", f"Failed to connect: {e}")

    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command.encode())
            print(f"Command sent: {command.strip()}")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "Connection Error", "No connection to the kit!")

    def toggle_direction(self):
        self.direction = "CCW" if self.direction == "CW" else "CW"
        self.send_command(f"DIR:{self.direction}\n")
        print(f"Direction set to: {self.direction}")

    def set_speed(self):
        speed = self.ui.speedSpinBox.value()
        self.send_command(f"SPD:{speed}\n")
        print(f"Speed set to: {speed}")

    def set_angle(self):
        if self.validate_angle_inputs():
            min_angle = self.ui.minLineEdit.text()
            max_angle = self.ui.maxLineEdit.text()
            self.send_command(f"ANG:{min_angle},{max_angle}\n")
            print(f"Angle set to: {min_angle}, {max_angle}")

    def reset_angle(self):
        self.ui.minLineEdit.setText("")
        self.ui.maxLineEdit.setText("")
        print("Angle reset to default")

    def validate_angle_inputs(self):
        min_angle = self.ui.minLineEdit.text()
        max_angle = self.ui.maxLineEdit.text()
        try:
            float(min_angle)
            float(max_angle)
            return True
        except ValueError:
            QtWidgets.QMessageBox.warning(self.ui, "Input Error", "Enter valid numbers for angles!")
            return False

    def move_to_home_position(self):
        self.send_command("HOME\n")
        print("Moved to home position")

    def update_battery_level(self):
        battery_level = 75  # Placeholder
        self.ui.batteryStatus_label.setText(f"Battery Level: {battery_level}%")
        print(f"Battery level: {battery_level}%")

    def toggle_patient_mode(self):
        if self.ui.selectPatient_radioButton.isChecked():
            self.ui.patientsComboBox.setEnabled(True)
            self.ui.patientLoadPushButton.setEnabled(True)
            self.ui.firstNameLineEdit.setEnabled(False)
            self.ui.lastNameLineEdit.setEnabled(False)
        elif self.ui.newPatient_radioButton.isChecked():
            self.ui.patientsComboBox.setEnabled(False)
            self.ui.patientLoadPushButton.setEnabled(False)
            self.ui.firstNameLineEdit.setEnabled(True)
            self.ui.lastNameLineEdit.setEnabled(True)

    def save_patient(self):
        first = self.ui.firstNameLineEdit.text()
        last = self.ui.lastNameLineEdit.text()
        if not first or not last:
            QtWidgets.QMessageBox.warning(self.ui, "Input Error", "Enter both first and last names.")
            return
        name = f"{first} {last}"
        patient_data = {"first": first, "last": last}

        patients = self.load_patient_data()
        patients[name] = patient_data

        with open(PATIENTS_FILE, "w") as f:
            json.dump(patients, f)

        self.ui.patientsComboBox.addItem(name)
        QtWidgets.QMessageBox.information(self.ui, "Success", f"Patient {name} saved.")

    def load_patient(self):
        name = self.ui.patientsComboBox.currentText()
        patients = self.load_patient_data()
        if name in patients:
            patient = patients[name]
            self.ui.firstNameLineEdit.setText(patient["first"])
            self.ui.lastNameLineEdit.setText(patient["last"])
            print(f"Loaded patient: {name}")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "Load Error", f"Patient {name} not found.")

    def load_patient_data(self):
        if os.path.exists(PATIENTS_FILE):
            with open(PATIENTS_FILE, "r") as f:
                return json.load(f)
        return {}

    def load_patient_list(self):
        patients = self.load_patient_data()
        self.ui.patientsComboBox.clear()
        self.ui.patientsComboBox.addItems(patients.keys())
