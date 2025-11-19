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
from Utils.NLUtils import NLLogger, ConColors
from Settings.SettingsBackend import SettingsBackend
from Niradock.Modules.DockPanelWidgets import DockClientManager,DockSettings,DockTime,DockScrollClientArea,DockSVG,DockTerminal,DockInternet,DockPower,DockWorkspaces


class DockPanel(QMainWindow):
    """Док панель,здесь вы найдёте Нириса в качестве пасхалки"""
    def __init__(self,HyprlandAbstractionlayer:HyprAL):
        super().__init__()
        #constants
        self.C_STD_ICON_SIZE = [30,40]
        self.C_PRODUCTION = False
        ########################### LOGGER INIT ###########################
        self.LOG = NLLogger(False,"DockPanel")
        self.LOG.Info("started",ConColors.B,False)
        ###################################################################
        # Settings init/load theme/load lang
        self.SettingsBackend = SettingsBackend(False,self.C_PRODUCTION)
        self.SettingsBackend.LoadConfig()
        # Load Theme
        self.ThemeManager = NikoruThemeManager(self.SettingsBackend.AllSettings['system-style'],self.C_PRODUCTION)
        self.theme = self.ThemeManager.GetTheme()
        #init Hyprald Abstraction Layer
        self.HAL = HyprlandAbstractionlayer
       
        RootWidget = QWidget()
        RootWidget.setObjectName('DockRootWidget')
        self.setCentralWidget(RootWidget)

        self.RootLayout = QHBoxLayout(RootWidget)
        self.RootLayout.setContentsMargins(0, 0, 0, 0)
        self.RootLayout.setSpacing(0)

       ################### CHILD SETUP #################################
        self.leftSegmentSetup()
        self.clientSegmentSetup()
        self.rightSegmentSetup()


       #################################################################
       ################### QT MAIN SETUP ###############################
        self.setAligment(Qt.AlignmentFlag.AlignLeft)

        self.setObjectName('DockBase')
        self.setStyleSheet(self.theme["main"])

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.updateGeometry(40) 
        QApplication.primaryScreen().geometryChanged.connect(self.onScreenResize)
        #################################################################

    def clientSegmentSetup(self):
        self.ClientArea = DockScrollClientArea(None,self.theme)
        self.ClientArea.setObjectName('DockRootWidget')
        self.ClientManadger = DockClientManager(self.HAL,self.C_PRODUCTION,self.ClientArea,self.theme)
        self.HAL.CAL = self.ClientManadger.CAL
        self.HAL.SServer = self.ClientManadger.SServer

        self.RootLayout.addWidget(self.ClientArea,1)

    def leftSegmentSetup(self):
        LeftSegment = QWidget()
        LeftSegment.setObjectName('DockRootWidget')
        LeftSegmentLayout = QHBoxLayout(LeftSegment)
        LeftSegmentLayout.setContentsMargins(0, 0, 0, 0)
        LeftSegmentLayout.setSpacing(2)
        self.ScrollLeft = DockSVG("ArrowMiniLeft",None,self.C_STD_ICON_SIZE,self.theme)
        
        self.ScrollLeft.clicked.connect(lambda: self.ClientArea.scroll_to("left"))
        
        Power = DockPower(None,[40,40],self.theme,self.HAL)
        Layers = DockWorkspaces(None,None,self.C_STD_ICON_SIZE,self.theme)
        
        LeftSegmentLayout.addWidget(Power)
        LeftSegmentLayout.addWidget(Layers)
        LeftSegmentLayout.addWidget(self.ScrollLeft)

        self.RootLayout.addWidget(LeftSegment)

    def rightSegmentSetup(self):
        
        RightPanel = QWidget()
        RightPanel.setObjectName('DockRootWidget')
        RightLayout = QHBoxLayout(RightPanel)
        RightLayout.setContentsMargins(0, 0,0, 0)
        RightLayout.setSpacing(4)
        
        
       

        ScrollToRight = DockSVG("ArrowMiniRight",None,self.C_STD_ICON_SIZE,self.theme)
        ScrollToRight.clicked.connect(lambda: self.ClientArea.scroll_to("right"))
        
        #DockSettings = DockSettings(None,self.C_STD_ICON_SIZE,self.theme)
        time_btn = DockTime(None,[72,40],Theme=self.theme)
        Terminal = DockTerminal(self.HAL,None,self.C_STD_ICON_SIZE,self.theme)
        Menu = DockSVG('Menu',None,self.C_STD_ICON_SIZE,self.theme)

        Internet = DockInternet(None,None,self.C_STD_ICON_SIZE,self.theme)

        Spacer = QPushButton()
        Spacer.setObjectName('DockButtons')
        Spacer.setFixedSize(20, 40)
        Spacer.setStyleSheet(self.theme['main'])
        
        
        RightLayout.addWidget(ScrollToRight)
        RightLayout.addWidget(Menu)
        RightLayout.addWidget(Terminal)
        RightLayout.addWidget(Internet)
        #RightLayout.addWidget(DockSettings)
        RightLayout.addWidget(time_btn)
        RightLayout.addWidget(Spacer)

        self.RootLayout.addWidget(RightPanel)
   


    def setAligment(self, alignment):
        self.ClientManadger.setAlignment(alignment)


    def updateGeometry(self, height):
        Screen = QApplication.primaryScreen().availableGeometry()
        self.setFixedWidth(Screen.width())
        self.resize(Screen.width(), height)
        self.move(Screen.x(), Screen.y() + Screen.height() - height)


    def onScreenResize(self):
        currentHeight = self.height()
        self.updateGeometry(currentHeight)

App = QApplication(sys.argv)
Panel = DockPanel(HyprAL())
Panel.show()
sys.exit(App.exec())
