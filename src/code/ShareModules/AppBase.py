# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PySide6.QtWidgets import QMainWindow, QWidget,QSizePolicy,QHBoxLayout,QVBoxLayout
from PySide6.QtNetwork import QLocalSocket
from PySide6.QtCore import QEvent
from Utils.NLUtils import NLLogger




class BaseWindow(QMainWindow):
    def __init__(self, sx: int,sy: int ,title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(sx, sy)



        self._root = QWidget()
        self.setCentralWidget(self._root)
        self.rootLayout = QHBoxLayout(self._root)

        self._root.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )


class MenuBase(QMainWindow):
    def __init__(self, sx: int,sy: int ,title: str,production:bool,command:str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(sx, sy)
        self.Logger = NLLogger(production,title)
        self.command = command
        self._root = QWidget()
        self.setCentralWidget(self._root)
        self.rootLayout = QVBoxLayout(self._root)

        self._root.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
       
    def _CloseClient(self):
        socket = QLocalSocket()
        socket.connectToServer('Niradock')

        if socket.waitForConnected(500):
            socket.write(self.command)
            socket.flush()
            socket.waitForBytesWritten(500)
            socket.disconnectFromServer()

    def event(self,event):
        if event.type() == QEvent.Leave:
            self._CloseClient()
            return True
        return super().event(event)