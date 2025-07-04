import sys
from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtCore import QPoint


x = int(sys.argv[1])
y = int(sys.argv[2])
style = sys.argv[3]
options = sys.argv[4:]

app = QApplication([])


menu = QMenu()


for option in options:
    menu.addAction(option)


action = menu.exec(QPoint(x, y))


if action:
    print(action.text())
else:
    print("")
    
sys.exit(0)