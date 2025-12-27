# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

import sys
from PySide6.QtWidgets import QApplication, QMenu,QMainWindow,QWidget
from PySide6.QtCore import QPoint
import time

x = int(sys.argv[1])
y = int(sys.argv[2])
style = sys.argv[3]
options = sys.argv[4:]

app = QApplication([])

root = QMainWindow()
root.resize(10,10)
root.move(x,y)
cWidg = QWidget()
root.setCentralWidget(cWidg)
menu = QMenu(cWidg)

for option in options:
    menu.addAction(option)

root.show()
root.activateWindow()

action = menu.exec(QPoint(x, y))


if action:
    print(action.text())
else:
    print("")
    
root.deleteLater()
app.quit()
sys.exit(app.exec())