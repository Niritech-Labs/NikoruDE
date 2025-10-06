# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve,QPoint,QEvent,QTimer,QLocale,QDateTime,Signal
from PySide6.QtWidgets import QWidget, QPushButton,QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem, QToolTip,QMenu
from PySide6.QtGui import QIcon
from Core.CoreHAL import HyprAL,WorkspacesHAL,EventBridge
from Core.CoreIAL import InterAL
from Core.NLUtils import ConfigManager
import json
import subprocess
from pathlib import Path
from Core.NLUtils import NLLogger,ConColors



class DockScrollClientArea(QWidget):
    def __init__(self, parent,Theme: dict):
        super().__init__(parent)
        self.Logger = NLLogger(False,"ClientArea")
        self.Logger.Info("started",ConColors.B,False)
        self.scrollArea = QScrollArea()
        self.setFixedHeight(40)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.Theme = Theme
        self.content_widget = QWidget()
        self.clientsLayout = QHBoxLayout(self.content_widget)
        self.clientsLayout.setContentsMargins(0, 0, 0, 0)
        
        self.scrollArea.setWidget(self.content_widget)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.scrollArea)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(self.Theme["ClientArea"])
        

        # Инициализация спейсеров
        self.left_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.right_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
    def scroll_to(self, direction):
        current = self.scrollArea.horizontalScrollBar().value()
        step = 300
        if direction == "left": position = max(0, current - step)
        else: position = min(self.scrollArea.horizontalScrollBar().maximum(),current + step)
        
        self.animation = QPropertyAnimation(self.scrollArea.horizontalScrollBar(),b"value")
        self.animation.setDuration(300)
        self.animation.setStartValue(current)
        self.animation.setEndValue(position)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()

    def setAlignment(self, alignment):
        # Удаляем старые спейсеры
        self.clientsLayout.removeItem(self.left_spacer)
        self.clientsLayout.removeItem(self.right_spacer)
        
        if alignment == Qt.AlignLeft: self.clientsLayout.addSpacerItem(self.right_spacer)
        elif alignment == Qt.AlignRight: self.clientsLayout.insertSpacerItem(0, self.left_spacer)
        elif alignment == Qt.AlignCenter: self.clientsLayout.insertSpacerItem(0, self.left_spacer); self.clientsLayout.addSpacerItem(self.right_spacer)
        
        self.clientsLayout.setAlignment(alignment)

class DockSettings(QPushButton):
    """Кнопка с отображением времени и даты"""
    def __init__(self, parent,size:list,Theme: dict):
        super().__init__(parent)
        self.Theme = Theme
        SX,SY = size
        self.Logger = NLLogger(False,"DockSettings")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(SX,SY)
        self.setIcon(QIcon(self.Theme["IconPath"]+"/settings.svg"))
        self.setIconSize(QSize(SX - 5, SX - 5))
        self.update()
        self.setAttribute(Qt.WA_AlwaysShowToolTips)  
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
    def update(self):
        self.setToolTip("Settings")
        self.setStyleSheet(self.Theme["Overview"])

    def openMenu(self, pos):
        pass  
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-5,-50)),self.toolTip(),self)
            return True
        return super().event(e)
    
class DockSVG(QPushButton):
    """отображение любого SVG"""
    def __init__(self,icon, parent,size:list,Theme:dict):
        super().__init__(parent)
        self.Theme = Theme
        ico = icon
        self.Logger = NLLogger(False,"DockSVG")
        self.Logger.Info("started",ConColors.B,False)
        SX,SY = size
        self.setFixedSize(SX,SY)
        self.setIcon(QIcon(self.Theme["IconPath"]+f"/{ico}.svg"))
        self.setIconSize(QSize(SX - 5, SX - 5))
        self.setStyleSheet(self.Theme["Overview"])

class DockTerminal(QPushButton):
    """Кнопка с отображением времени и даты"""
    def __init__(self,HAL:HyprAL, parent,size:list,Theme:dict):
        super().__init__(parent)
        self.Theme = Theme
        SX,SY = size
        self.HAL = HAL
        self.Logger = NLLogger(False,"DockTerminal")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(SX,SY)
        self.setIcon(QIcon(self.Theme["IconPath"]+"/terminal.svg"))
        self.setIconSize(QSize(SX - 5, SX - 5))
        self.clicked.connect(lambda: self.HAL.RunProcess('rio'))
        self.setToolTip("Open terminal")
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.setStyleSheet(self.Theme["Overview"])
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-5,-50)),self.toolTip(),self)
            return True
        return super().event(e)
    
class DockInternet(QPushButton):
    """Панель управления интернетом"""
    def __init__(self,IAL:InterAL, parent,size:list,Theme:dict):
        super().__init__(parent)
        self.Theme = Theme
        self.SX,self.SY = size
        self.IAL = IAL
        self.Logger = NLLogger(False,"DockInternet")
        self.Logger.Info("started",ConColors.B,False)
        self.status = ['noInternet','No connection']
        self.setFixedSize(self.SX,self.SY)
        self.clicked.connect(self.openInternetMenu)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.update()
        self.setStyleSheet(self.Theme["Overview"])
        
    def update(self):
        self.setIcon(QIcon(self.Theme["IconPath"]+f"/{self.status[0]}.svg"))
        self.setIconSize(QSize(self.SX - 5, self.SX - 5))
        self.setToolTip(self.status[1])

    def openInternetMenu(self):
        pass

    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-5,-50)),self.toolTip(),self)
            return True
        return super().event(e)    
    
class DockTime(QPushButton):
    """отображение времени и даты"""
    def __init__(self, parent=None,size = [72,40],locale = QLocale.Russian,Theme = ''):
        super().__init__(parent)
        SX,SY = size
        self.localen = QLocale(locale)
        self.Theme = Theme
        self.Logger = NLLogger(False,"DockTime")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(SX,SY)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(5000)  # Обновление каждую секунду
        self.update_time()
        self.setAttribute(Qt.WA_AlwaysShowToolTips)  
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
    def update_time(self):
        current_time = QDateTime.currentDateTime()
        self.setText(current_time.toString("HH:mm\n dd.MM.yyyy"))
        
        self.setToolTip(self.localen.toString(current_time,"d MMMM yyyy',' dddd"))
        self.setStyleSheet(self.Theme["Overview"])

    def openMenu(self, pos):
        pass  
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(75,-50)),self.toolTip(),self)
            return True
        return super().event(e)

class DockClient(QPushButton):
    """Графическая обёртка приложения для док панели"""
    destroing = Signal()
    def __init__(self, HAL:HyprAL,title: str, icon: QIcon,IC: str, parent=None,pinned = False,Theme = {"Clients":''}):
        super().__init__(parent)
        self.HAL = HAL
        

        #datas
        self.runned = {}
        self.visible = {}

        self.lastClient = ''
        self.Theme = Theme
        self.pin = pinned
        self.ids = []
        self.title = title
        self.icond = icon
        self.IC = IC
        self.clicked.connect(self.LClick)
        self.setup_ui()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        self.Logger = NLLogger(False,f"DockClient {self.title}")
        self.Logger.Info("started",ConColors.B,False)

    def setup_ui(self):
        if self.HAL.debug: print(self.title)
        self.setIcon(self.icond)
        self.setIconSize(QSize(38, 38))
        self.setFixedSize(40, 40) 
        self.setToolTip(self.title) #подсказка о названии приложения
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.setStyleSheet(self.Theme["Clients"])
    #подсказка о названии приложения
    def nameToltip(self):
        QToolTip.showText(self.mapToGlobal(self.rect().bottomLeft),self.title)
    #открыть меню действий
    def openMenu(self, pos):
        pos = self.mapToGlobal(QPoint(0,-40))
        panel = ['/bin/python','/usr/share/NikoruDE/Code/Menus/Nikoru@AppMenu.py',str(pos.x()),str(pos.y()),"D"] + ['New','HelloWorld']
        comand = subprocess.run(panel,capture_output=True,text=True,encoding='utf-8',errors='ignore')
        print(comand.stdout.strip())
        
    def LClick(self):
        print(self.visible,'u')
        if self.ids == [] and self.pin:
            self.run()
        if not self.visible == {}:
            for ID in self.visible:
                value = self.visible[ID]
                if value == False:
                    self.HideManager(True,ID)
                    self.lastClient = ID
                    print(self.visible,'ud')
                    return
            if self.lastClient == '':
                self.lastClient = self.ids[0]
            self.HideManager(False,self.lastClient)
            print('hide')
            print(self.visible,'d')
        
 
            
    def run():
        pass

    def HideManager(self,visible:bool,id:str):
        idActiveWorkspace = json.loads(self.HAL.hyprctl.send(b'j/activeworkspace'))['id']
        unhide = f'dispatch movetoworkspacesilent {idActiveWorkspace},address:{id}'
        hide = f'dispatch movetoworkspacesilent 99,address:{id}'
        setActive = f'dispatch focuswindow address:{id}'
        if visible:
            self.HAL.hyprctl.send(bytes(unhide,'utf-8'))
            self.HAL.hyprctl.send(bytes(setActive,'utf-8'))
        else:
            self.HAL.hyprctl.send(bytes(hide,'utf-8'))

    def HideManagerAll(self,visible:bool):
        idActiveWorkspace = json.loads(self.HAL.hyprctl.send(b'j/activeworkspace'))['id']
        for ID in self.visible:
            unhide = f'dispatch movetoworkspacesilent {idActiveWorkspace},address:{ID}'
            hide = f'dispatch movetoworkspacesilent 99,address:{ID}'
            if visible:
                self.HAL.hyprctl.send(bytes(unhide,'utf-8'))
            else:
                self.HAL.hyprctl.send(bytes(hide,'utf-8'))

    def delete(self):
        self.setParent(None)
        self.ids = []
        self.visible = {}
        self.runned = {}
        self.deleteLater()
 
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-30,-50)),self.toolTip(),self)
            return True
        return super().event(e)

class DockPower(QPushButton):
    """кнопка питания"""
    def __init__(self, parent,size:list,Theme: dict):
        super().__init__(parent)
        SX,SY = size
        self.Theme = Theme
        self.Logger = NLLogger(False,"DockPower")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(SX,SY)
        self.setToolTip('power')
        self.setAttribute(Qt.WA_AlwaysShowToolTips)  
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        self.setIcon(QIcon(self.Theme["IconPath"]+"/power.svg"))
        self.setIconSize(QSize(SX - 15, SX - 15))
    
        self.setStyleSheet(self.Theme["Overview"])

    def openMenu(self, pos):
        pass  
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(75,-50)),self.toolTip(),self)
            return True
        return super().event(e)
    
class DockWorkspaces(QPushButton):
    """Панель управления рабочими столами"""
    def __init__(self,WHAL:WorkspacesHAL, parent,size:list,Theme:dict):
        super().__init__(parent)
        self.Theme = Theme
        self.SX,self.SY = size
        self.WHAL = WHAL
        self.Logger = NLLogger(False,"DockWorkspaces")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(self.SX,self.SY)
        self.clicked.connect(self.openInternetMenu)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.update()
        
    def update(self):
        self.setStyleSheet(self.Theme["Overview"])
        self.setIcon(QIcon(self.Theme["IconPath"]+"/Layers.svg"))
        self.setIconSize(QSize(self.SX - 5, self.SX - 5))
        self.setToolTip("Control Workspaces")

    def openInternetMenu(self):
        pass

    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-5,-50)),self.toolTip(),self)
            return True
        return super().event(e)   

class DockClientManager():
    def __init__(self,HAL:HyprAL,ClientArea:DockScrollClientArea,Theme = {"Clients":''}, configPath= "~/.config/NikoruDE/ClientPanel.confJs"):
        self.eventBridge = EventBridge()
        self.eventBridge.eventSignal.connect(self.UpdateManager)


        self.Logger = NLLogger(False,"DockClient-Manager")
        self.Logger.Info("started",ConColors.B,False)
        self.ClientArea = ClientArea
        self.HAL = HAL
        self.currentAlignment = Qt.AlignLeft

        self.config = ConfigManager(configPath)
        self.AppsConfig = self.config.LoadConfig()

        self.IC = {}
        self.ID = {}
        self.blacklist = []

        self.Theme = Theme

        self.targetEvents = ["openwindow", "closewindow", "movewindow"]
        
        # Регистрируем обработчики только для нужных событий
        
        for event_type in self.targetEvents:
            self.HAL.hyprEvent.bind(event_type, self._asyncYunkEvent)
        self.HAL.hyprEvent.start()

        self.InitClients()


    def setAlignment(self, alignment):
        self.currentAlignment = alignment
        self.ClientArea.setAlignment(alignment)

    def InitClients(self):
        ClientsData = self.HAL.GetClients()
        for clientData in ClientsData:
            if clientData["initialClass"] in self.IC:
                self.IC[clientData["initialClass"]].ids.append(clientData["address"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]


                self.IC[clientData["initialClass"]].runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    self.IC[clientData["initialClass"]].visible[clientData["address"]] = False
                else:
                    self.IC[clientData["initialClass"]].visible[clientData["address"]] = True
            else:
                icoPath,title,ico = self.HAL.getClientInfo(clientData["initialClass"])
                icon = QIcon.fromTheme(ico) or QIcon(icoPath) or QIcon.fromTheme(self.HAL._getName(clientData["initialClass"]).lower()) or QIcon.fromTheme(clientData["initialClass"].lower())
                client = DockClient(self.HAL,title,icon,clientData["initialClass"],Theme=self.Theme)
                client.ids.append(clientData["address"])


                client.runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    client.visible[clientData["address"]] = False
                else:
                    client.visible[clientData["address"]] = True

                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)
            
    def CloseClient(self,id):
        client = self.ID[id]
        if len(client.ids) > 1:
            client.ids.remove(id)
            del client.visible[id]
            del client.runned[id] 
        elif len(client.ids) == 1:
            if not client.pin:
                self.ClientArea.clientsLayout.removeWidget(client)
                client.delete()
                self.ClientArea.setAlignment(self.currentAlignment)
                del self.IC[client.IC]
            else:
                client.ids = []
                client.visible = {}
                client.runned = {}
        #del self.IDtoIC[id]
        del self.ID[id]

    def OpenClient(self,id):
        clientData = self.HAL.GetClient(id)
        if not clientData == None:
            if clientData["initialClass"] in self.IC:
                self.IC[clientData["initialClass"]].ids.append(clientData["address"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]


                self.IC[clientData["initialClass"]].runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    self.IC[clientData["initialClass"]].visible[clientData["address"]] = False
                else:
                    self.IC[clientData["initialClass"]].visible[clientData["address"]] = True
            else:
                icoPath,title,ico = self.HAL.getClientInfo(clientData["initialClass"])
                icon = QIcon.fromTheme(ico) or QIcon(icoPath) or QIcon.fromTheme(self.HAL._getName(clientData["initialClass"]).lower()) or QIcon.fromTheme(clientData["initialClass"].lower())
                client = DockClient(self.HAL,title,icon,clientData["initialClass"],Theme=self.Theme)
                client.ids.append(clientData["address"])

                client.runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    client.visible[clientData["address"]] = False
                else:
                    client.visible[clientData["address"]] = True

                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)

    def _asyncYunkEvent(self, raw_data):
        self.eventBridge.eventSignal.emit(raw_data)

    def UpdateHiddenClient(self,id,state:bool):
        client = self.ID[id]
        client.visible[id] = state
        print('hidState:',state)

    def ClientFilter(self,byteData:str):
        try:
            splitedData = byteData.split(b',')
            clid = splitedData[0]
            dd = splitedData[2]
            Title = splitedData[3]
            if b'@' in Title:
                sys,name = Title.split(b'@')
            if sys == b'Nikoru':
                if not clid in self.blacklist:
                    self.blacklist.append(clid)
                return False
            elif dd == b'' and Title == b'':
                if not clid in self.blacklist:
                    self.blacklist.append(clid)
                return False
            else:
                return True
        except:
            return True

    def UpdateManager(self,data: str):
        byteEvent, byteData = data.split(b'>>')
        print(byteData)
        if self.ClientFilter(byteData=byteData):
            if b',' in byteData:
                byteData = byteData.split(b',')
                id = byteData[0]
            else:
                id = byteData
            if not id in self.blacklist:
                id = id.decode('utf-8', errors='ignore')
                if byteEvent == b'openwindow':
                    self.OpenClient('0x'+id)
                if byteEvent == b'closewindow':
                    self.CloseClient('0x'+id)
                if byteEvent == b'movewindow':
                    if byteData[1] == b'99':
                        self.UpdateHiddenClient("0x"+id,state=False)
                    else:
                        self.UpdateHiddenClient("0x"+id,state=True)



