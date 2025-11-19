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