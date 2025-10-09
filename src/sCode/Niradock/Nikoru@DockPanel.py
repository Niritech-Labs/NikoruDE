# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,QPushButton,QHBoxLayout
from Core.CoreHAL import HyprAL
from Core.CoreStyle import NikoruThemeManager
from Core.NLUtils import NLLogger, ConColors
from Settings.SettingsBackend import SettingsBackend
from Widgets.DockPanelWidgets import DockClientManager,DockSettings,DockTime,DockScrollClientArea,DockSVG,DockTerminal,DockInternet,DockPower,DockWorkspaces

"""Вы уж извините,но использовать встроенный языковой переводчик я не буду (poka ne budu), его написали больные мазохизмом люди! каждый перевод писать заново? ну уж нет!"""
class DockPanel(QMainWindow):
    """Док панель,здесь вы найдёте Нириса в качестве пасхалки"""
    def __init__(self,HAl:HyprAL):
        super().__init__()
        self.production = False
        # Настройка окна UwU
        self.setObjectName('DockBase')
        self.Logger = NLLogger(False,"DockPanel")
        self.Logger.Info("started",ConColors.B,False)
        self.SB = SettingsBackend(False,self.production)
        self.SB.LoadConfig()
        self.ThM = NikoruThemeManager(self.SB.AllSettings['system-style'],self.production)
        self.Theme = self.ThM.ThemeLoad()
        self.HAL = HAl
        self.StdIconSize = [30,40]
        self.app_alignment = 'center'
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(self.Theme["main"])
       
        
        # Настройка начального размера и позиции
        rootWidget = QWidget()
        rootWidget.setObjectName('DockRootWidget')
        rootLayoutLRC = QHBoxLayout(rootWidget)
        rootLayoutLRC.setContentsMargins(0, 0, 0, 0)
        rootLayoutLRC.setSpacing(0)

       
        self._initLeftPanel()
        # Центральная область (растягивается)
        self.ClientArea = DockScrollClientArea(None,self.Theme)
        self.ClientArea.setObjectName('DockRootWidget')
        self.ClientManadger = DockClientManager(self.HAL,self.production,self.ClientArea,self.Theme)
        self.HAL.CAL = self.ClientManadger.CAL
        self.HAL.SServer = self.ClientManadger.SServer
        self._initRightPanel()

        # Собираем все вместе
        rootLayoutLRC.addWidget(self.leftPanel)
        rootLayoutLRC.addWidget(self.ClientArea,1)
        rootLayoutLRC.addWidget(self.rightPanel)

        self.setCentralWidget(rootWidget)
        # Стилизация
       
        self.set_alignment(Qt.AlignLeft)
        
        self.update_geometry(40) 
        QApplication.primaryScreen().geometryChanged.connect(self.handle_screen_resize)

    def _initLeftPanel(self):
        self.leftPanel = QWidget()
        self.leftPanel.setObjectName('DockRootWidget')
        leftLayout = QHBoxLayout(self.leftPanel)
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(2)
        self.ScrollLeft = DockSVG("ArrowMiniLeft",None,self.StdIconSize,self.Theme)
        
        self.ScrollLeft.clicked.connect(lambda: self.ClientArea.scroll_to("left"))
        
        power = DockPower(None,[40,40],self.Theme,self.HAL)
        layers = DockWorkspaces(None,None,self.StdIconSize,self.Theme)
        
        leftLayout.addWidget(power)
        leftLayout.addWidget(layers)
        leftLayout.addWidget(self.ScrollLeft)

    def _initRightPanel(self):
        
        self.rightPanel = QWidget()
        self.rightPanel.setObjectName('DockRootWidget')
        rightLayout = QHBoxLayout(self.rightPanel)
        rightLayout.setContentsMargins(0, 0,0, 0)
        rightLayout.setSpacing(4)
        
        
       

        ScrollRight = DockSVG("ArrowMiniRight",None,self.StdIconSize,self.Theme)
        ScrollRight.clicked.connect(lambda: self.ClientArea.scroll_to("right"))
        
        dsettings = DockSettings(None,self.StdIconSize,self.Theme)
        time_btn = DockTime(None,[72,40],Theme=self.Theme)
        terminal = DockTerminal(self.HAL,None,self.StdIconSize,self.Theme)
        menu = DockSVG('Menu',None,self.StdIconSize,self.Theme)

        internet = DockInternet(None,None,self.StdIconSize,self.Theme)

        btn = QPushButton()
        btn.setObjectName('DockButtons')
        btn.setFixedSize(20, 40)
        btn.setStyleSheet(self.Theme['main'])
        
        
        rightLayout.addWidget(ScrollRight)
        rightLayout.addWidget(menu)
        rightLayout.addWidget(terminal)
        rightLayout.addWidget(internet)
        rightLayout.addWidget(dsettings)
        rightLayout.addWidget(time_btn)
        rightLayout.addWidget(btn)
   


    def set_alignment(self, alignment):
        self.ClientManadger.setAlignment(alignment)


    def update_geometry(self, height):
        screen = QApplication.primaryScreen().availableGeometry()
        self.setFixedWidth(screen.width())
        self.resize(screen.width(), height)
        self.move(screen.x(), screen.y() + screen.height() - height)

    def set_panel_height(self, height):
        self.update_geometry(height)

    def handle_screen_resize(self):
        current_height = self.height()
        self.update_geometry(current_height)

app = QApplication(sys.argv)
panel = DockPanel(HyprAL())
panel.show()
sys.exit(app.exec())
