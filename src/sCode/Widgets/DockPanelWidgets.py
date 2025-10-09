# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve,QPoint,QEvent,QTimer,QLocale,QDateTime,Signal,QObject
from PySide6.QtWidgets import QWidget, QPushButton,QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem, QToolTip,QMenu
from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QLocalServer
from Core.CoreHAL import HyprAL,WorkspacesHAL,EventBridge
from Core.CoreIAL import InterAL
from Core.NLUtils import ConfigManager
import json
import subprocess
from pathlib import Path
from Core.NLUtils import NLLogger,ConColors



class DockScrollClientArea(QWidget):
    def __init__(self, parent,Theme:str):
        super().__init__(parent)
        self.Logger = NLLogger(False,"ClientArea")
        self.Logger.Info("started",ConColors.B,False)
        self.scrollArea = QScrollArea()
        self.currentAlignment = Qt.AlignLeft
        self.setFixedHeight(40)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.Theme = Theme
        self.contentClient = QWidget()
        self.contentClient.setObjectName('DockRootWidget')
        self.contentClient.setStyleSheet(self.Theme['main'])
        self.clientsLayout = QHBoxLayout(self.contentClient)
        self.clientsLayout.setContentsMargins(0, 0, 0, 0)
        
        self.scrollArea.setWidget(self.contentClient)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.scrollArea)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName('DockRootWidget')
        self.setStyleSheet(self.Theme['main'])
        

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
        self.currentAlignment = alignment

    def reloadAlignment(self):
        self.setAlignment(self.currentAlignment)
        

class DockSettings(QPushButton):
    """Кнопка с отображением времени и даты"""
    def __init__(self, parent,size:list,Theme: str):
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
        self.setObjectName('DockButtons')
        self.setToolTip("Settings")
        self.setStyleSheet(self.Theme['main'])

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
        self.setObjectName('DockButtons')
        self.setStyleSheet(self.Theme["main"])

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
        self.setObjectName('DockButtons')
        self.setStyleSheet(self.Theme["main"])
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
        self.setObjectName('DockButtons')
        self.setStyleSheet(self.Theme["main"])
        
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
    def __init__(self, parent=None,size = [72,40],locale = QLocale.Russian,Theme = {}):
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
        self.setObjectName('DockButtons')
        self.setStyleSheet(self.Theme["main"])

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
    def __init__(self, HAL:HyprAL,title: str, icon: QIcon,IC: str,pinned:bool,icoPath:tuple,Theme:dict):
        super().__init__(None)
        self.HAL = HAL
        

        #datas
        self.runned = {}
        self.visible = {}

        self.lastClient = ''
        self.iconPath = icoPath
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
        self.setIcon(self.icond)
        self.setIconSize(QSize(38, 38))
        self.setFixedSize(40, 40) 
        self.setToolTip(self.title) #подсказка о названии приложения
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.setObjectName('DockClients')
        self.setStyleSheet(self.Theme["main"])
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
        if self.ids == [] and self.pin:
            self.run()
        if not self.visible == {}:
            for ID in self.visible:
                clientVisible = self.visible[ID]
                if clientVisible == False:
                    #print(self.visible,self.IC+' Client set command to visible : '+ID)
                    self.HideManager(True,ID)
                    self.lastClient = ID
                    return
            if self.lastClient == '':
                self.lastClient = self.ids[0]
            #print(self.visible,self.IC+' Client set command to hide : '+ID)
            self.HideManager(False,self.lastClient)
            
        
 
            
    def run():
        pass

    def HideManager(self,visible:bool,ID:str):
        idActiveWorkspace = json.loads(self.HAL.hyprctl.send(b'j/activeworkspace'))['id']
        unhide = f'dispatch movetoworkspacesilent {idActiveWorkspace},address:{ID}'
        hide = f'dispatch movetoworkspacesilent 99,address:{ID}'
        setActive = f'dispatch focuswindow address:{ID}'
        if visible:
            self.HAL.hyprctl.send(bytes(unhide,'utf-8'))
            self.HAL.hyprctl.send(bytes(setActive,'utf-8'))
            print(self.visible,self.IC+' Client is visible now: '+ID)
        else:
            self.HAL.hyprctl.send(bytes(hide,'utf-8'))
            print(self.visible,self.IC+' Client is hidden now: '+ID)

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
    def __init__(self, parent,size:list,Theme: dict,HAL:HyprAL):
        super().__init__(parent)
        SX,SY = size
        self.Theme = Theme
        self.HAL = HAL
        self.Logger = NLLogger(False,"DockPower")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(SX,SY)
        self.setToolTip('power')
        self.setAttribute(Qt.WA_AlwaysShowToolTips)  
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        self.setIcon(QIcon(self.Theme["IconPath"]+"/power.svg"))
        self.setIconSize(QSize(SX - 15, SX - 15))
        self.setObjectName('DockButtons')
        self.setStyleSheet(self.Theme["main"])
        self.clicked.connect(self.LClick)
    def LClick(self):
        #self.HAL.CAL.SavePinned(s)
        self.HAL.SServer.unhideWindow('Nikoru@Power.py')
        
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
        self.setStyleSheet(self.Theme["main"])
        self.setObjectName('DockButtons')
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
    def __init__(self,HAL:HyprAL,production:bool,ClientArea:DockScrollClientArea,Theme = {"Clients":''}, configPath= "~/.config/Nikoru/Clients.confJs"):
        self.eventBridge = EventBridge()
        self.eventBridge.eventSignal.connect(self.UpdateManager)
        self.production = production

        self.Logger = NLLogger(False,"DockClient-Manager")
        self.Logger.Info("started",ConColors.B,False)
        self.ClientArea = ClientArea
        self.HAL = HAL
        self.currentAlignment = Qt.AlignLeft

        self.CM = ConfigManager(configPath,self.production)
        self.SavedClients = self.CM.LoadConfig()
        if self.SavedClients == None or self.SavedClients == '':
            self.SavedClients = {}

        self.IC = {}
        self.ID = {}
        self.blacklist = []

        self.SServer = SockServer(self.HAL,self.Logger)
        self.SServer._SetupServer()

        self.Theme = Theme

        self.CAL = ClientAL(self.HAL,self.Theme,self.ClientArea,self.SavedClients,self.CM) 

        self.targetEvents = ["openwindow", "closewindow", "movewindowv2"]
        for eventType in self.targetEvents:
            self.HAL.hyprEvent.bind(eventType, self._CallbackHyprEvent)
        self.HAL.hyprEvent.start()

        self.InitClients()


    def setAlignment(self, alignment):
        self.currentAlignment = alignment
        self.ClientArea.setAlignment(alignment)

    def InitClients(self):
        for savedClient in self.SavedClients:
            client = self.CAL.LoadPinned(savedClient)
            self.IC[clientData["initialClass"]] = client
            self.ClientArea.clientsLayout.addWidget(client)
            self.ClientArea.setAlignment(self.currentAlignment)
        ClientsData = self.HAL.GetClients()
        for clientData in ClientsData:
            if "Nikoru@" in clientData["initialClass"]:
                self.SServer.ICS[clientData["initialClass"]] = clientData["address"]
            if clientData["initialClass"] in self.IC:
                self.CAL.Reinit(client=self.IC[clientData["initialClass"]],clid=clientData["address"],hidden=clientData["hidden"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]
            else:
                client = self.CAL.Add(IC=clientData["initialClass"],clid=clientData["address"],hidden=clientData["hidden"])
                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)
            self.Logger.Info('Init: Client opened: '+clientData["address"],ConColors.G,False)
            
    def CloseClient(self,id):
        self.Logger.Info('Event: Client closed: '+id,ConColors.G,False)
        self.CAL.Delete(self.ID[id])
        del self.ID[id]

    def OpenClient(self,ID):
        self.Logger.Info('Event: Client opened: '+ID,ConColors.G,False)
        clientData = self.HAL.GetClient(ID)
        # if client exists in Hyprland
        if not clientData == None:
            if clientData["initialClass"] in self.IC:
                #if client on a DockPanel
                self.CAL.Reinit(client=self.IC[clientData["initialClass"]],clid=clientData["address"],hidden=clientData["hidden"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]
            else:
                #if client not on a DockPanel
                client = self.CAL.Add(IC=clientData["initialClass"],clid=clientData["address"],hidden=clientData["hidden"])
                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)

    def _CallbackHyprEvent(self, bEvent):
        self.eventBridge.eventSignal.emit(bEvent)

    def UpdateHiddenClient(self,ID,state:bool):
        self.Logger.Info('Event: Client set visible to: '+str(state),ConColors.G,False)
        client = self.ID[ID]
        client.visible[ID] = state

    def ClientFilter(self,byteData:str,byteEvent):
        try:
            if byteData.count(b',') > 0:
                splitedData = byteData.split(b',')
                bid = splitedData[0]
            else:
                bid = byteData
            if byteData.count(b',') > 2:
                btitle = splitedData[3]
                if b'@' in btitle:
                    sys,_name = btitle.split(b'@')
                    if sys == b'Nikoru':
                        title = btitle.decode('utf-8', errors='ignore')
                        if byteEvent == b'openwindow':
                            bid = bid.decode('utf-8', errors='ignore')
                            self.SServer.ICS[title] = "0x"+bid
                            self.Logger.Info('Opened menu window'+title,ConColors.Y,False)
                        if byteEvent == b'closewindow':
                            self.SServer.ICS[title] = None
                            self.Logger.Info('Closed menu window'+title,ConColors.Y,False)
                        if not bid in self.blacklist:
                            self.blacklist.append(bid)
                            return False
                elif btitle == b'':
                    if not bid in self.blacklist:
                        self.blacklist.append(bid)
                    return False
                
            elif bid in self.blacklist:
                return False
            else:
                return True
        except Exception as e:
            self.Logger.Error('Filter: '+str(e))
            return True

    def UpdateManager(self,bEvent: str):
        self.Logger.Info('Current Event: '+bEvent.decode('utf-8', errors='ignore'),ConColors.Y,False)
        bClientEvent, bData = bEvent.split(b'>>')
        if self.ClientFilter(byteData=bData,byteEvent=bClientEvent):
            if b',' in bData:
                bData = bData.split(b',')
                ID = bData[0]
            else:
                ID = bData
            if not ID in self.blacklist:
                ID = ID.decode('utf-8', errors='ignore')
                if bClientEvent == b'openwindow':
                    self.OpenClient('0x'+ID)
                if bClientEvent == b'closewindow':
                    self.CloseClient('0x'+ID)
                if bClientEvent == b'movewindowv2':
                    if bData[1] == b'99':
                        self.UpdateHiddenClient("0x"+ID,state=False)
                    else:
                        self.UpdateHiddenClient("0x"+ID,state=True)
        else:
            self.Logger.Info('Filtered event system service',ConColors.V,False)
           
class ClientAL:
    def __init__(self,HAL:HyprAL,Theme:dict,CA:DockScrollClientArea,savedClients:dict,ConfigManager:ConfigManager):
        self.client = None
        self.HAL = HAL
        self.CM = ConfigManager
        self.SvCl = savedClients
        self.Theme = Theme
        self.ClientArea = CA

    def Reinit(self,client:DockClient,clid:str,hidden:str):
        client.ids.append(clid)
        if hidden == 'false':
            client.visible[clid] = False
        else:
            client.visible[clid] = True
        client.runned[clid] = True

    def Add(self,IC:str,clid:str,hidden:str):
        icoPath,title,ico = self.HAL.getClientInfo(IC)
        icon = QIcon.fromTheme(ico) or QIcon(icoPath) or QIcon.fromTheme(self.HAL._getName(IC).lower()) or QIcon.fromTheme(IC.lower())
        client = DockClient(self.HAL,title,icon,IC,icoPath=(ico,icoPath),pinned=False,Theme=self.Theme)
        client.ids.append(clid)
        if hidden == 'false':
            client.visible[clid] = False
        else:
            client.visible[clid] = True
        client.runned[clid] = True
        return client
    
    def LoadPinned(self,LoadedClient:dict):
        IC = LoadedClient['IC']
        title = LoadedClient['title']
        ico = LoadedClient['icon']
        icoPath = LoadedClient['icon-path']
        icoPath,title,ico 
        icon = QIcon.fromTheme(ico) or QIcon(icoPath) or QIcon.fromTheme(self.HAL._getName(IC).lower()) or QIcon.fromTheme(IC.lower())
        client = DockClient(self.HAL,title,icon,IC,icoPath=(ico,icoPath),Theme=self.Theme,pinned=True)
        return client
    
    def SavePinned(self,client:DockClient):
        SavedClient = {}
        ico, icoPath = client.iconPath
        SavedClient['IC'] = client.IC
        SavedClient['title'] = client.title
        SavedClient['icon'] = ico
        SavedClient['icon-path'] = icoPath
        self.SvCl[client.IC] = SavedClient
        self.CM.SaveConfig(self.SvCl)

    
    def Delete(self,client:DockClient):
        if len(client.ids) > 1:
            client.ids.remove(id)
            del client.visible[id]
            del client.runned[id] 
        elif len(client.ids) == 1:
            if not client.pin:
                self.ClientArea.clientsLayout.removeWidget(client)
                client.delete()
                self.ClientArea.reloadAlignment()
                del self.IC[client.IC]
            else:
                client.ids = []
                client.visible = {}
                client.runned = {}
        

class SockServer(QWidget):
    def __init__(self,HAL:HyprAL,Logger:NLLogger):
        super().__init__(None)
        
        self.ICS = {}
        self.HAL = HAL
        self.Logger = Logger
        self.serverName = 'Niradock'
       
    def _SetupServer(self):
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
            clid = self.ICS[IC]
            idActiveWorkspace = json.loads(self.HAL.hyprctl.send(b'j/activeworkspace'))['id']
            unhide = f'dispatch movetoworkspacesilent {idActiveWorkspace},address:{clid}'
            setActive = f'dispatch focuswindow address:{clid}'

            self.HAL.hyprctl.send(bytes(unhide,'utf-8'))
            self.HAL.hyprctl.send(bytes(setActive,'utf-8'))
        except Exception as e:
            self.Logger.Error("Menu isn't exists:"+str(e),False)
            
    def hideWindow(self,IC):
        try:
            print(self.ICS)
            print(IC)
            clid = self.ICS[IC]
            hide = f'dispatch movetoworkspacesilent 99,address:{clid}'
            self.HAL.hyprctl.send(bytes(hide,'utf-8'))
        except Exception as e:
            self.Logger.Error("Menu isn't exists:"+str(e),False)
    
       
     