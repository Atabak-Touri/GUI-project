import serial
import serial.tools.list_ports
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

class ActuatorControlGUI(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load("GUI_V4.ui", None)
        self.ui.setWindowTitle("Actuator Controller")

        self.serial_port = None
        self.direction = "CW"  # Track current direction

        # Connect UI elements to functions
        self.ui.pushButton_Run.clicked.connect(lambda: self.send_command("RUN\n"))  # Run button
        self.ui.pushButton_Stop.clicked.connect(lambda: self.send_command("STOP\n"))  # Stop button
        self.ui.pushButton_ChangeDirection.clicked.connect(self.toggle_direction)  # Change direction button
        self.ui.setSpeedPushButton.clicked.connect(self.set_speed)  # Set speed button
        self.ui.resetSpeedPushButton.clicked.connect(self.reset_speed)  # Reset speed button
        self.ui.setAnglePushButton.clicked.connect(self.set_angle)  # Set angle button
        self.ui.resetAnglePushButton.clicked.connect(self.reset_angle)  # Reset angle button
        self.ui.cycleSetPushButton.clicked.connect(self.set_cycle_number)  # Set cycle number button
        self.ui.pushButton_Connect.clicked.connect(self.connect_to_kit)  # Connect to kit button
        self.ui.homePosition_pushButton.clicked.connect(self.move_to_home_position)  # Home position button

        # Serial Port Handling
        self.refresh_ports()
        self.ui.connect_comboBox.currentIndexChanged.connect(self.port_selected)

        # Initialize battery level
        self.update_battery_level()

    def show(self):
        self.ui.show()

    def refresh_ports(self):
        """Refresh the list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        self.ui.connect_comboBox.clear()
        for port in ports:
            self.ui.connect_comboBox.addItem(port.device)
        if not ports:
            self.ui.connect_comboBox.addItem("No ports available")

    def port_selected(self):
        """Handle port selection from the combo box"""
        selected_port = self.ui.connect_comboBox.currentText()
        print(f"Selected port: {selected_port}")

    def connect_to_kit(self):
        """Connect to the kit"""
        selected_port = self.ui.connect_comboBox.currentText()
        try:
            self.serial_port = serial.Serial(selected_port, timeout=1)
            print(f"Connected to the kit on {selected_port}")
            self.ui.disconnected.setText("CONNECTED")
            self.ui.disconnected.setStyleSheet("color: green;")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.ui, "Connection Error", f"Failed to connect: {e}")

    def send_command(self, command):
        """Send a command to the actuator via serial port"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command.encode())
            print(f"Command sent: {command}")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "Connection Error", "No connection to the kit!")

    def toggle_direction(self):
        """Toggle the actuator's direction"""
        self.direction = "CCW" if self.direction == "CW" else "CW"
        self.send_command(f"DIR:{self.direction}\n")
        print(f"Direction set to: {self.direction}")

    def set_speed(self):
        """Set speed from spin box value"""
        speed = self.ui.speedSpinBox.value()
        self.send_command(f"SPD:{speed}\n")
        print(f"Speed set to: {speed}")

    def reset_speed(self):
        """Reset speed to default"""
        self.ui.speedSpinBox.setValue(0)
        print("Speed reset to default")

    def set_angle(self):
        """Set angle from line edits"""
        if self.validate_angle_inputs():
            min_angle = self.ui.minLineEdit.text()
            max_angle = self.ui.maxLineEdit.text()
            self.send_command(f"ANG:{min_angle},{max_angle}\n")
            print(f"Angle set to: {min_angle}, {max_angle}")
        else:
            print("Invalid angle inputs")

    def reset_angle(self):
        """Reset angle inputs to default"""
        self.ui.minLineEdit.setText("")
        self.ui.maxLineEdit.setText("")
        print("Angle reset to default")

    def validate_angle_inputs(self):
        """Check if angle inputs are valid floats"""
        min_angle = self.ui.minLineEdit.text()
        max_angle = self.ui.maxLineEdit.text()
        try:
            float(min_angle)
            float(max_angle)
            return True
        except ValueError:
            QtWidgets.QMessageBox.warning(self.ui, "Input Error", "Please enter valid numbers for angle!")
            return False

    def set_cycle_number(self):
        """Set the cycle number from the line edit"""
        cycle_number = self.ui.numCycleLineEdit.text()
        if cycle_number.isdigit():
            self.send_command(f"CYC:{cycle_number}\n")
            print(f"Cycle number set to: {cycle_number}")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "Input Error", "Please enter a valid number!")

    def move_to_home_position(self):
        """Move the actuator to the home position"""
        self.send_command("HOME\n")
        print("Moved to home position")

    def update_battery_level(self):
        """Update the battery level in the GUI"""
        # Placeholder for battery level logic
        # Replace this with actual logic to retrieve battery level if available
        battery_level = 75  # Example: 75%
        self.ui.batteryStatus_label.setText(f"Battery Level: {battery_level}%")
        print(f"Battery level: {battery_level}%")