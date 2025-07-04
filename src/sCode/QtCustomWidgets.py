# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve,QPoint,QEvent,QTimer,QLocale,QDateTime,Signal
from PySide6.QtWidgets import QWidget, QPushButton,QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem, QToolTip,QMenu
from PySide6.QtGui import QIcon
from Core.CoreHAL import HyprAL,WorkspacesHAL,EventBridge
from Core.CoreIAL import InterAL
import json
from pathlib import Path


class DockScrollClientArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollArea = QScrollArea()
        self.setFixedHeight(40)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.clientsLayout = QHBoxLayout(self.content_widget)
        self.clientsLayout.setContentsMargins(0, 0, 0, 0)
        
        self.scrollArea.setWidget(self.content_widget)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.scrollArea)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
                QWidget {
                    background: #2d2d2d;
                    border: 0px solid #505050;
                    border-radius: 4px;
                }
            """)

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
    def __init__(self, parent=None,size = [30,40],theme="dark"):
        super().__init__(parent)
        if theme == 'dark': self.theme = 'L'
        else: self.theme = 'D'
        SX,SY = size
        self.setFixedSize(SX,SY)
        self.setIcon(QIcon(f"/usr/share/NikoruDE/Image/Dock/icons/{self.theme}settings.svg"))
        self.setIconSize(QSize(SX - 5, SX - 5))
        self.update()
        self.setAttribute(Qt.WA_AlwaysShowToolTips)  
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
    def update(self):
        self.setToolTip("Settings")
        self.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 0px solid #505050;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #575757;
            }
            
        """)

    def openMenu(self, pos):
        pass  
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-5,-50)),self.toolTip(),self)
            return True
        return super().event(e)
    
class DockSVG(QPushButton):
    """отображение любого SVG"""
    def __init__(self,icon, parent=None,size = [30,40],theme="dark"):
        super().__init__(parent)
        if theme == 'dark': self.theme = 'L'
        else: self.theme = 'D'
        ico = icon
        SX,SY = size
        self.setFixedSize(SX,SY)
        self.setIcon(QIcon(f"/usr/share/NikoruDE/Image/Dock/icons/{self.theme+ico}.svg"))
        self.setIconSize(QSize(SX - 5, SX - 5))
        self.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 0px solid #505050;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #575757;
            }
            
        """)

class DockTerminal(QPushButton):
    """Кнопка с отображением времени и даты"""
    def __init__(self,HAL:HyprAL, parent=None,size = [30,40],theme="dark"):
        super().__init__(parent)
        if theme == 'dark': self.theme = 'L'
        else: self.theme = 'D'
        SX,SY = size
        self.HAL = HAL
        self.setFixedSize(SX,SY)
        self.setIcon(QIcon(f"/usr/share/NikoruDE/Image/Dock/icons/{self.theme}terminal.svg"))
        self.setIconSize(QSize(SX - 5, SX - 5))
        self.clicked.connect(lambda: self.HAL.RunProcess('kitty'))
        self.setToolTip("Open terminal")
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 0px solid #505050;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #575757;
            }
            
        """)
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-5,-50)),self.toolTip(),self)
            return True
        return super().event(e)
    
class DockInternet(QPushButton):
    """Панель управления интернетом"""
    def __init__(self,IAL:InterAL, parent=None,size = [30,40],theme="dark"):
        super().__init__(parent)
        if theme == 'dark': self.theme = 'L'
        else: self.theme = 'D'
        self.SX,self.SY = size
        self.IAL = IAL
        self.status = ['noInternet','No connection']
        self.setFixedSize(self.SX,self.SY)
        self.clicked.connect(self.openInternetMenu)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.update()
        self.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 0px solid #505050;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #575757;
            }
            
        """)
    def update(self):
        self.setIcon(QIcon(f"/usr/share/NikoruDE/Image/Dock/icons/{self.theme+self.status[0]}.svg"))
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
    def __init__(self, parent=None,size = [72,40],locale = QLocale.Russian):
        super().__init__(parent)
        SX,SY = size
        self.localen = QLocale(locale)
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
        self.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 0px solid #505050;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #575757;
            }
        """)

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
    def __init__(self, HAL:HyprAL,title: str, icon: QIcon,IC: str, parent=None,pinned = False):
        super().__init__(parent)
        self.HAL = HAL

        #datas
        self.runned = {}
        self.hidden = {}

        self.pinned = pinned
        self.ids = []
        self.title = title
        self.icond = icon
        self.IC = IC
        self.clicked.connect(self.ToggleHide)
        self.setup_ui()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def setup_ui(self):
        if self.HAL.debug: print(self.title)
        self.setIcon(self.icond)
        self.setIconSize(QSize(38, 38))
        self.setFixedSize(40, 40) 
        self.setToolTip(self.title) #подсказка о названии приложения
        self.setAttribute(Qt.WA_AlwaysShowToolTips)  
        self.setStyleSheet("""
                    QPushButton {
                        background: #404040;border: 1px solid #505050;border-radius: 4px;
                    }
                    QPushButton:hover { 
                        background: #575757;
                    } 
                           """)
    #подсказка о названии приложения
    def nameToltip(self):
        QToolTip.showText(self.mapToGlobal(self.rect().bottomLeft),self.title)
    #открыть меню действий
    def openMenu(self, pos):
        menu = QMenu(self)
        menuh = 60

        globalPos = self.mapToGlobal(QPoint(-30,-60))
        destroy_action = menu.addAction("close")
        menu.exec(globalPos)

    def ToggleHide(self):
        idW = json.loads(self.HAL.hyprctl.send(b'j/activeworkspace'))['id']
        work = f'dispatch movetoworkspacesilent {idW},address:{self.ids[0]}'
        hidden = f'dispatch movetoworkspacesilent 99,address:{self.ids[0]}'
        if self.hidden:
            
            print(self.HAL.hyprctl.send(bytes(work,'utf-8'),waitAnswer=True))
        else:
            print(self.HAL.hyprctl.send(bytes(hidden,'utf-8'),waitAnswer=True))
        self.hidden = not self.hidden
    def delete(self):
        self.setParent(None)
        self.ids = []
        self.hidden = {}
        self.runned = {}
        self.deleteLater()
 
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-30,-50)),self.toolTip(),self)
            return True
        return super().event(e)

class DockPower(QPushButton):
    """кнопка питания"""
    def __init__(self, parent=None,size = [40,40],theme="dark"):
        super().__init__(parent)
        SX,SY = size
        if theme == 'dark': self.theme = 'L'
        else: self.theme = 'D'
        self.setFixedSize(SX,SY)
        self.setToolTip('power')
        self.setAttribute(Qt.WA_AlwaysShowToolTips)  
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        self.setIcon(QIcon(f"/usr/share/NikoruDE/Image/Dock/icons/{self.theme}power.svg"))
        self.setIconSize(QSize(SX - 15, SX - 15))
    
        self.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 0px solid #505050;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #575757;
            }
        """)

    def openMenu(self, pos):
        pass  
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(75,-50)),self.toolTip(),self)
            return True
        return super().event(e)
    
class DockWorkspaces(QPushButton):
    """Панель управления рабочими столами"""
    def __init__(self,WHAL:WorkspacesHAL, parent=None,size = [30,40],theme="dark"):
        super().__init__(parent)
        if theme == 'dark': self.theme = 'L'
        else: self.theme = 'D'
        self.SX,self.SY = size
        self.WHAL = WHAL
        self.setFixedSize(self.SX,self.SY)
        self.clicked.connect(self.openInternetMenu)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.update()
        self.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 0px solid #505050;
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #575757;
            }
            
        """)
    def update(self):
        self.setIcon(QIcon(f"/usr/share/NikoruDE/Image/Dock/icons/{self.theme}Layers.svg"))
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
    def __init__(self,HAL:HyprAL,ClientArea:DockScrollClientArea, debug=False, configPath= "~/.config/NikoruDE/ClientPanel.confJs"):
        self.eventBridge = EventBridge()
        self.eventBridge.eventSignal.connect(self.UpdateManager)

        self.debug = debug
        self.ClientArea = ClientArea
        self.HAL = HAL
        self.currentAlignment = Qt.AlignLeft

        self.configPath = Path(configPath).expanduser().resolve()
        self.AppsConfig = self.LoadConfig()

        self.IC = {}
        self.ID = {}

        self.targetEvents = ["openwindow", "closewindow", "movewindow"]
        
        # Регистрируем обработчики только для нужных событий
        
        for event_type in self.targetEvents:
            self.HAL.hyprEvent.bind(event_type, self._asyncYunkEvent)
        self.HAL.hyprEvent.start()

        self.InitClients()

    def LoadConfig(self):
        try:
            with open(self.configPath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            if(self.debug): print("can't load saved apps,creatig new config")
            defconf = {}
            self.SaveConfig(defconf)
            return defconf

    def SaveConfig(self,configD):
        if not self.configPath.exists(): self.configPath.parent.mkdir(parents=True,exist_ok=True)
        with open(self.configPath, 'w', encoding='utf-8') as file:
            json.dump(configD, file, ensure_ascii=False, indent=4)

    def setAlignment(self, alignment):
        self.currentAlignment = alignment
        self.ClientArea.setAlignment(alignment)

    def InitClients(self):
        ClientsData = self.HAL.GetClients()
        for clientData in ClientsData:
            if clientData["initialClass"] in self.IC:
                self.IC[clientData["initialClass"]].ids.append(clientData["address"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]

                #self.IDtoIC[clientData["address"]] = clientData["initialClass"]

                self.IC[clientData["initialClass"]].runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    self.IC[clientData["initialClass"]].hidden[clientData["address"]] = False
                else:
                    self.IC[clientData["initialClass"]].hidden[clientData["address"]] = True
            else:
                icoPath,title,ico = self.HAL.getClientInfo(clientData["initialClass"])
                icon = QIcon.fromTheme(ico) or QIcon(icoPath) or QIcon.fromTheme(self.HAL._getName(clientData["initialClass"]).lower()) or QIcon.fromTheme(clientData["initialClass"].lower())
                client = DockClient(self.HAL,title,icon,clientData["initialClass"])
                client.ids.append(clientData["address"])

                #self.IDtoIC[clientData["address"]] = clientData["initialClass"]

                client.runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    client.hidden[clientData["address"]] = False
                else:
                    client.hidden[clientData["address"]] = True

                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)
            
    def CloseClient(self,id):
        client = self.ID[id]
        if len(client.ids) > 1:
            client.ids.remove(id)
            del client.hidden[id]
            del client.runned[id] 
        elif len(client.ids) == 1:
            if not client.pinned:
                self.ClientArea.clientsLayout.removeWidget(client)
                client.delete()
                self.ClientArea.setAlignment(self.currentAlignment)
                del self.IC[client.IC]
            else:
                client.ids = []
                client.hidden = {}
                client.runned = {}
        #del self.IDtoIC[id]
        del self.ID[id]

    def OpenClient(self,id):
        clientData = self.HAL.GetClient(id)
        if not clientData == None:
            if clientData["initialClass"] in self.IC:
                self.IC[clientData["initialClass"]].ids.append(clientData["address"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]

                #self.IDtoIC[clientData["address"]] = clientData["initialClass"]

                self.IC[clientData["initialClass"]].runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    self.IC[clientData["initialClass"]].hidden[clientData["address"]] = False
                else:
                    self.IC[clientData["initialClass"]].hidden[clientData["address"]] = True
            else:
                icoPath,title,ico = self.HAL.getClientInfo(clientData["initialClass"])
                icon = QIcon.fromTheme(ico) or QIcon(icoPath) or QIcon.fromTheme(self.HAL._getName(clientData["initialClass"]).lower()) or QIcon.fromTheme(clientData["initialClass"].lower())
                client = DockClient(self.HAL,title,icon,clientData["initialClass"])
                client.ids.append(clientData["address"])

                #self.IDtoIC[clientData["address"]] = clientData["initialClass"]

                client.runned[clientData["address"]] = True
                if clientData["hidden"] == "false":
                    client.hidden[clientData["address"]] = False
                else:
                    client.hidden[clientData["address"]] = True

                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)

    def _asyncYunkEvent(self, raw_data):
        self.eventBridge.eventSignal.emit(raw_data)

    def UpdateHiddenClient(self,id,state):
        client = self.ID[id]
        client.hidden[id] = state
    def UpdateManager(self,data: str):
        Bevent, Bdata = data.split(b'>>')
        print(data)
        if b',' in Bdata:
            Bdata = Bdata.split(b',')
            id = Bdata[0].decode('utf-8', errors='ignore')
        else:
            id = Bdata.decode('utf-8', errors='ignore')
        if Bevent == b'openwindow':
            self.OpenClient('0x'+id)
        if Bevent == b'closewindow':
            self.CloseClient('0x'+id)
        if Bevent == b'movewindow':
            if Bdata[1] == b'99':
                self.UpdateHiddenClient("0x"+id,True)
            else:
                self.UpdateHiddenClient("0x"+id,False)

