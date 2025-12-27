# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.\
from PySide6.QtWidgets import QWidget
from PySide6.QtNetwork import QLocalServer

import json

from NLUtils.Logger import NLLogger
from Core.CoreHAL import HyprAL

class SockServer(QWidget):
    def __init__(self,HAL:HyprAL,Logger:NLLogger,ICS:dict):
        super().__init__(None)
        
        self.ICS = ICS
        self.HAL = HAL
        self.Logger = Logger
        self.serverName = 'Niradock'
       
    def SetupServer(self):
        self.server = QLocalServer(self)

        QLocalServer.removeServer(self.serverName)

        if self.server.listen(self.serverName):
            self.server.newConnection.connect(self.connection)
        else:
            self.Logger.Error('Failed to start server:'+self.server.errorString(),True)

    def connection(self):
        soket = self.server.nextPendingConnection()
        if soket:
            soket.readyRead.connect(lambda:self.processCommand(soket))
            soket.disconnected.connect(soket.deleteLater)

    def processCommand(self,socket):
        data = socket.readAll().data().decode().strip()
        command,IC = data.split('_')
        if command == 'open':
            self.unhideWindow(IC)
        elif command == 'close':
            self.hideWindow(IC)
    def unhideWindow(self,IC):
        try:
            ID = self.ICS[IC]
            idActiveWorkspace = json.loads(self.HAL.HyprCtl.Send(b'j/activeworkspace'))['id']

            self.HAL.MoveToWorkspace(idActiveWorkspace,ID)
            self.HAL.SetClientActive(ID)
        except KeyError:
            self.Logger.Error("Panel isn't exists:",False)
        except Exception as e:
            self.Logger.Error(str(e),False)
            
    def hideWindow(self,IC):
        try:
            ID = self.ICS[IC]
            self.HAL.MoveToWorkspace(ID)
        except KeyError:
            self.Logger.Error("Panel isn't exists:",False)
        except Exception as e:
            self.Logger.Error(str(e),False)
    