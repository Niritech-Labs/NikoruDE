# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Widgets.AppBase import BaseWindow
from PySide6.QtWidgets import QApplication
import sys

class Settings(BaseWindow):
    def __init__():
        super().__init__(800, 600, "Settings")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Settings()
    window.show()
    sys.exit(app.exec())
