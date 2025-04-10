import sys
from PySide6.QtWidgets import QApplication
from widget import ActuatorControlGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ActuatorControlGUI()
    window.show()
    sys.exit(app.exec())