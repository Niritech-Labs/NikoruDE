# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve,QPoint,QEvent,QTimer,QLocale,QDateTime,Signal
from PySide6.QtWidgets import QWidget, QPushButton,QHBoxLayout, QScrollArea, QSizePolicy, QSpacerItem, QToolTip
from PySide6.QtGui import QIcon

from Core.CoreHAL import HyprAL,WorkspacesHAL
from Core.CoreIAL import InterAL
import json
import subprocess
from Utils.NLUtils import NLLogger,ConColors



class DockScrollClientArea(QWidget):
    def __init__(self, parent,Theme:str):
        super().__init__(parent)
        self.Logger = NLLogger(False,"ClientArea")
        self.Logger.Info("started",ConColors.B,False)
        self.scrollArea = QScrollArea()
        self.currentAlignment = Qt.AlignLeft
        self.setFixedHeight(40)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
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
    def __init__(self, HAL:HyprAL,title: str, icon: QIcon,IC: str,pinned:bool,iconPath:str,Theme:dict,toExec:str):
        super().__init__(None)
        self.HAL = HAL
        

        #datas
        self.runned = {}
        self.visible = {}

        self.lastClient = ''
        self.iconPath = iconPath
        self.Theme = Theme
        self.toExec = toExec
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

