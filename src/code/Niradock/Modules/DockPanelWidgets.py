# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve,QPoint,QEvent,QTimer,QLocale,QDateTime,Signal
from PySide6.QtWidgets import QWidget, QPushButton,QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem, QToolTip
from PySide6.QtGui import QIcon

from Core.CoreHAL import HyprAL,WorkspacesHAL
from Core.CoreIAL import InternetAL
import json
import subprocess
from NLUtils.Logger import NLLogger,ConColors
from NLUtils.BlocksUtils import Blocks



class DockScrollClientArea(QWidget):
    def __init__(self, parent,Theme:str):
        super().__init__(parent)
        self.Logger = NLLogger(False,"ClientArea")
        self.Logger.Info("started",ConColors.B,False)
        self.ScrollArea = QScrollArea()
        self.currentAlignment = Qt.AlignLeft
        self.setFixedHeight(40)
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.Theme = Theme
        self.ContentClientGroup = QWidget()
        self.ContentClientGroup.setObjectName('DockRootWidget')
        self.ContentClientGroup.setStyleSheet(self.Theme['main'])
        self.ClientGroupsLayout = QHBoxLayout(self.ContentClientGroup)
        self.ClientGroupsLayout.setContentsMargins(0, 0, 0, 0)
        
        self.ScrollArea.setWidget(self.ContentClientGroup)
        
        self.MainLayout = QHBoxLayout(self)
        self.MainLayout.addWidget(self.ScrollArea)
        self.MainLayout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName('DockRootWidget')
        self.setStyleSheet(self.Theme['main'])
        

        self.LeftSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.RightSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
    def scroll_to(self, direction):
        current = self.ScrollArea.horizontalScrollBar().value()
        step = 300
        if direction == "left": position = max(0, current - step)
        else: position = min(self.ScrollArea.horizontalScrollBar().maximum(),current + step)
        
        self.animation = QPropertyAnimation(self.ScrollArea.horizontalScrollBar(),b"value")
        self.animation.setDuration(300)
        self.animation.setStartValue(current)
        self.animation.setEndValue(position)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()

    def setAlignment(self, alignment):
        # Удаляем старые спейсеры
        self.ClientGroupsLayout.removeItem(self.LeftSpacer)
        self.ClientGroupsLayout.removeItem(self.RightSpacer)
        
        if alignment == Qt.AlignmentFlag.AlignLeft: self.ClientGroupsLayout.addSpacerItem(self.RightSpacer)
        elif alignment == Qt.AlignmentFlag.AlignRight: self.ClientGroupsLayout.insertSpacerItem(0, self.LeftSpacer)
        elif alignment == Qt.AlignmentFlag.AlignCenter: self.ClientGroupsLayout.insertSpacerItem(0, self.LeftSpacer); self.ClientGroupsLayout.addSpacerItem(self.RightSpacer)
        
        self.ClientGroupsLayout.setAlignment(alignment)
        self.currentAlignment = alignment

    def AddClientGroup(self,ClientGroup:'DockClientGroup'):
        self.ClientGroupsLayout.addWidget(ClientGroup)

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
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)  
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
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)
        self.setObjectName('DockButtons')
        self.setStyleSheet(self.Theme["main"])
    def event(self, e):
        if e.type() == QEvent.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(-5,-50)),self.toolTip(),self)
            return True
        return super().event(e)
    
class DockInternet(QPushButton):
    """Панель управления интернетом"""
    def __init__(self,IAL:InternetAL, parent,size:list,Theme:dict):
        super().__init__(parent)
        self.Theme = Theme
        self.SX,self.SY = size
        self.IAL = IAL
        self.Logger = NLLogger(False,"DockInternet")
        self.Logger.Info("started",ConColors.B,False)
        self.status = ['noInternet','No connection']
        self.setFixedSize(self.SX,self.SY)
        self.clicked.connect(self.openInternetMenu)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)
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
    def __init__(self, parent=None,size = [72,40],locale = QLocale.Language.Russian,Theme = {}):
        super().__init__(parent)
        SX,SY = size
        self.localen = QLocale(locale)
        self.Theme = Theme
        self.Logger = NLLogger(False,"DockTime")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(SX,SY)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(5000) 
        self.update_time()
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)  
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

class DockClientGroup(QPushButton):
    """Графическая обёртка приложения для док панели"""
    destroing = Signal()
    def __init__(self, HAL:HyprAL,Theme:dict,ClientData:Blocks):
        super().__init__(None)
        self.HAL = HAL
        self.Theme = Theme
        self.ClientData = ClientData
       
        self.IDDB = []
        self.runned = {}
        self.visibleData = {}

    
        self.pinState = False
        self.title = self.ClientData.FindParam('title')[0][1]
        self.qtIcon = self.ClientData.FindParam('icon')[0][1]
        self.IC = self.ClientData.FindParam('IC')[0][1]


        self.lastClient = ''
        self.clicked.connect(self.leftClick)
        self.setupWidget()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClick)
        self.Logger = NLLogger(False,f"DockClient {self.title}")
        self.Logger.Info("started",ConColors.B,False)

    def PinClientGroup(self):
        self.pinState = True

    def UnpinClientGroup(self):
        self.PinClientGroup

    def GetIDDB(self)->list:
        return self.IDDB



    def setupWidget(self):
        self.setIcon(self.qtIcon)
        self.setIconSize(QSize(38, 38))
        self.setFixedSize(40, 40) 
        self.setToolTip(self.title) 
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)
        self.setObjectName('DockClients')
        self.setStyleSheet(self.Theme["main"])

    def nameToltip(self):
        QToolTip.showText(self.mapToGlobal(self.rect().bottomLeft),self.title)

    def rightClick(self, pos):
        pos = self.mapToGlobal(QPoint(0,-40))
        panel = ['/bin/python','/usr/share/NikoruDE/Code/Menus/Nikoru@AppMenu.py',str(pos.x()),str(pos.y()),"D"] + ['New','HelloWorld']
        comand = subprocess.run(panel,capture_output=True,text=True,encoding='utf-8',errors='ignore')
        print(comand.stdout.strip())
        
    def leftClick(self):
        if self.IDDB == [] and self.pinState:
            self.clientExec()
        if not self.visibleData == {}:
            for ID in self.visibleData:
                clientVisible = self.visibleData[ID]
                if clientVisible == False:
                   
                    self.Unhide(ID)
                    self.lastClient = ID
                    return
            if self.lastClient == '':
                self.lastClient = self.IDDB[0]
            
            self.Hide(self.lastClient)
            
        
 
            
    def clientExec():
        pass

    def Hide(self,ID:str):  
        self.HAL.HideClient(ID)
        print(self.visibleData,self.ClientData.name+' Client is hidden now: '+ID)

    def Unhide(self,ID:str):
        idActiveWorkspace = json.loads(self.HAL.HyprCtl.Send(b'j/activeworkspace'))['id']
        self.HAL.MoveToWorkspace(idActiveWorkspace,ID)
        self.HAL.SetClientActive(ID)
        print(self.visibleData,self.ClientData.name+' Client is visible now: '+ID)

    def HideAll(self,visible:bool):
        idActiveWorkspace = json.loads(self.HAL.HyprCtl.Send(b'j/activeworkspace'))['id']
        for ID in self.visibleData:
            if visible:
                self.HAL.MoveToWorkspace(idActiveWorkspace,ID)
            else:
                self.HAL.HideClient(ID)

    def Delete(self):
        self.setParent(None)
        self.IDDB = []
        self.visibleData = {}
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
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)
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

class DockLang(QPushButton):
    def __init__(self, parent=None,size = [72,40],Theme = {}):
        super().__init__(parent)
        SX,SY = size
        self.Theme = Theme
        self.Logger = NLLogger(False,"DockTime")
        self.Logger.Info("started",ConColors.B,False)
        self.setFixedSize(SX,SY)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateLang)
        self.timer.start(5000)  # Обновление каждую секунду
        self.updateLang()
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)  
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        
    def updateLang(self,lang:str):
        self.setText(lang)
        self.setObjectName('DockButtons')
        self.setStyleSheet(self.Theme["main"])

    def event(self, e):
        if e.type() == QEvent.Type.ToolTip:
            QToolTip.showText(self.mapToGlobal(QPoint(75,-50)),self.toolTip(),self)
            return True
        return super().event(e)