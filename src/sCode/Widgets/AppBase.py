# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,QSizePolicy
#from PySide6.Qt import Qt


class BaseWindow(QMainWindow):
    def __init__(self, sx: int,sy: int ,title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(sx, sy)

        self.root = QWidget()
        self.setCentralWidget(self.root)

        self.root.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )


