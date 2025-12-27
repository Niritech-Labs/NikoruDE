# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ShareModules.AppBase import MenuBase
from PySide6.QtWidgets import QApplication, QSizePolicy, QPushButton, QWidget, QGridLayout, QLabel

class DesktopMenu(MenuBase):
    def __init__(self):
        super().__init__(500, 600, 'Nikoru@Desktops.py', False, b'close_Nikoru@Desktops.py')
        self._root.setSizePolicy(
            QSizePolicy.Policy.Fixed, 
            QSizePolicy.Policy.Fixed
        )
        self.QObjects = {}
        self.menuSetup()

    def menuSetup(self):
        pass
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesktopMenu()
    window.show()
    sys.exit(app.exec())