import serial
import serial.tools.list_ports
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

class ActuatorControlGUI(QtCore.QObject):  # Object wrapper around UI
    def __init__(self):
        super().__init__()
        self.ui = loader.load("GUI_V3.ui", None)
        self.ui.setWindowTitle("Actuator Control")

        self.serial_port = None
        self.direction = "CW"  # Track current direction

        # Connect UI elements to functions
        self.ui.pushButton_Run.clicked.connect(lambda: self.send_command("RUN\n"))  # Run button
        self.ui.pushButton_Stop.clicked.connect(lambda: self.send_command("STOP\n"))  # Stop button
        self.ui.pushButton_ChangeDirection.clicked.connect(self.toggle_direction)  # Change direction button
        self.ui.setSpeedPushButton.clicked.connect(self.set_speed)  # Set speed button
        self.ui.setAnglePushButton.clicked.connect(self.set_angle) # Set angle button
        self.ui.resetSpeedPushButton.clicked.connect(self.reset_speed)  # Reset speed button
        self.ui.angleResetPushButton.clicked.connect(self.reset_angle)  # Reset angle button
        self.ui.cycleSetPushButton.clicked.connect(self.set_cycle_number)  # Set cycle number button
        self.ui.pushButton_Connect.clicked.connect(self.connect_to_kit)  # Connect to kit button

        # Serial Port Handling
        self.refresh_ports()
        self.ui.selectPort_comboBox.currentIndexChanged.connect(self.port_selected)
        # self.ui.pushButton_RefreshPorts.clicked.connect(self.refresh_ports)

    def show(self):
        self.ui.show()

    def refresh_ports(self):
        """Refresh the list of available serial ports"""
        self.ui.selectPort_comboBox.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.ui.selectPort_comboBox.addItem(port.device)

    def port_selected(self):
        """Handle port selection from combo box"""
        selected_port = self.ui.selectPort_comboBox.currentText()
        baud_rate = self.ui.baudRate_lineEdit.text()
        self.connect_serial(selected_port, baud_rate)

    def connect_serial(self, port, baud_rate):
        """Connect to selected serial port"""
        try:
            self.serial_port = serial.Serial(port, int(baud_rate), timeout=1)
            print(f"Connected to {port} at {baud_rate} baud")
        except Exception as e:
            print(f"Connection error: {e}")

    def send_command(self, command):
        """Send command over serial"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command.encode())
        else:
            print("Serial port not connected!")

    def toggle_direction(self):
        """Toggle actuator direction"""
        self.direction = "CCW" if self.direction == "CW" else "CW"
        self.send_command(f"DIR:{self.direction}\n")

    def reset_speed(self):
        """Reset speed slider to default"""
        self.ui.resistanceSlider.setValue(0)
        print("Speed reset to default")

    def set_speed(self):
        """Set speed from slider value"""
        speed = self.ui.resistanceSlider.value()
        self.send_command(f"SPD:{speed}\n")
        print(f"Speed set to: {speed}")
    def set_angle(self):
        """Set angle from line edits"""
        if self.validate_angle_inputs():
            angle_1 = self.ui.minLineEdit_2.text()
            angle_2 = self.ui.maxLineEdit.text()
            self.send_command(f"ANG:{angle_1},{angle_2}\n")
            print(f"Angle set to: {angle_1}, {angle_2}")
        else:
            print("Invalid angle inputs")

    def reset_angle(self):
        """Reset angle inputs to default"""
        self.ui.minLineEdit_2.setText("")
        self.ui.maxLineEdit.setText("")
        print("Angle reset to default")

    def validate_angle_inputs(self):
        """Check if angle inputs are valid floats"""
        angle_1 = self.ui.minLineEdit_2.text()  # Correct object name for minimum angle
        angle_2 = self.ui.maxLineEdit.text()   # Correct object name for maximum angle

        try:
            float(angle_1)
            float(angle_2)
            return True
        except ValueError:
            QtWidgets.QMessageBox.warning(self.ui, "Input Error", "Please enter valid numbers for angle!")
            return False

    def set_cycle_number(self):
        """Set the cycle number from the line edit"""
        cycle_number = self.ui.numCycleLineEdit.text()
        if cycle_number.isdigit():
            print(f"Cycle number set to: {cycle_number}")
        else:
            QtWidgets.QMessageBox.warning(self.ui, "Input Error", "Please enter a valid number!")

    def connect_to_kit(self):
        """Connect to the kit"""
        selected_port = self.ui.selectPort_comboBox.currentText()
        try:
            # Attempt to connect to the selected port
            self.serial_port = serial.Serial(selected_port, timeout=1)
            print(f"Connected to the kit on {selected_port}")
            QtWidgets.QMessageBox.information(self.ui, "Connection Successful", f"Connected to {selected_port}")
        except Exception as e:
            # Handle connection errors
            QtWidgets.QMessageBox.warning(self.ui, "Connection Error", f"Failed to connect: {e}")