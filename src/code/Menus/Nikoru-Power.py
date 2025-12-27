# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ShareModules.AppBase import MenuBase
from PySide6.QtWidgets import QApplication,QSizePolicy,QPushButton,QWidget,QGridLayout,QLabel

class PowerMenu(MenuBase):
    def __init__(self):
        super().__init__(500, 600, 'Nikoru@Power.py',False,b'close_Nikoru@Power.py')
        self._root.setSizePolicy(
            QSizePolicy.Policy.Fixed, 
            QSizePolicy.Policy.Fixed
        )
        self.QObjects = {}
        self.MenuSetup()
    def MenuSetup(self):
        self.User = QWidget()
        self.User.setObjectName('PowerUserBackground')
        self.rootLayout.addWidget(self.User)
        self.userLayout = QGridLayout(self.User)

        self.Username = QLabel('Niris')
        self.userLayout.addWidget(self.Username,0,1)

        self.Systemname = QLabel('wm-almalinux-10')
        self.userLayout.addWidget(self.Systemname,1,1)

        self.UIcon = QLabel('Icon')
        self.userLayout.addWidget(self.UIcon,0,0)
        

        buttons = ['Shutdown','Sleep','Exit']
        for buttonName in buttons:
            button = QPushButton(buttonName,parent=None)
            button.setObjectName('PowerButton')
            self.QObjects[buttonName] = button
            self.rootLayout.addWidget(button)
            
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PowerMenu()
    window.show()
    sys.exit(app.exec())

