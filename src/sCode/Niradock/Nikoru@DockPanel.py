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
from Widgets.DockPanelWidgets import DockClientManager,DockSettings,DockTime,DockScrollClientArea,DockSVG,DockTerminal,DockInternet,DockPower,DockWorkspaces

"""Вы уж извините,но использовать встроенный языковой переводчик я не буду (poka ne budu), его написали больные мазохизмом люди! каждый перевод писать заново? ну уж нет!"""
class DockPanel(QMainWindow):
    """Док панель,здесь вы найдёте Нириса в качестве пасхалки"""
    def __init__(self,HAl:HyprAL):
        super().__init__()
        # Настройка окна UwU
        self.Logger = NLLogger(False,"DockPanel")
        self.Logger.Info("started",ConColors.B,False)
        self.ThM = NikoruThemeManager()
        self.Theme = self.ThM.SYS_Th_Reload()['DockPanel']
        self.HAL = HAl
        self.StdIconSize = [30,40]
        self.app_alignment = 'center'
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(self.Theme["Overview"])
       
        
        # Настройка начального размера и позиции
        rootWidget = QWidget()
        rootLayoutLRC = QHBoxLayout(rootWidget)
        rootLayoutLRC.setContentsMargins(0, 0, 0, 0)
        rootLayoutLRC.setSpacing(0)

       
        self._initLeftPanel()
        # Центральная область (растягивается)
        self.ClientArea = DockScrollClientArea(None,self.Theme)
        self.ClientManadger = DockClientManager(self.HAL,self.ClientArea,self.Theme)
        self._initRightPanel()
        #self.AppManadger.LoadApps()


        # Собираем все вместе
        rootLayoutLRC.addWidget(self.leftPanel)
        rootLayoutLRC.addWidget(self.ClientArea,1)
        rootLayoutLRC.addWidget(self.rightPanel)

        self.setCentralWidget(rootWidget)
        # Стилизация
       
        #self.add_test_buttons(60)
        self.set_alignment(Qt.AlignLeft)
        
        self.update_geometry(40) 
        # Отслеживание изменений экрана
        QApplication.primaryScreen().geometryChanged.connect(self.handle_screen_resize)

    def _initLeftPanel(self):
          # Левая область (200px)
        self.leftPanel = QWidget()
        left_layout = QHBoxLayout(self.leftPanel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        self.btn_left = DockSVG("ArrowMiniLeft",None,self.StdIconSize,self.Theme)
        
        self.btn_left.clicked.connect(lambda: self.ClientArea.scroll_to("left"))
        
        power = DockPower(None,[40,40],self.Theme)
        layers = DockWorkspaces(None,None,self.StdIconSize,self.Theme)
        # Добавляем 2 кнопки
        left_layout.addWidget(power)
        left_layout.addWidget(layers)
        left_layout.addWidget(self.btn_left)

    def _initRightPanel(self):
        
        self.rightPanel = QWidget()
        right_layout = QHBoxLayout(self.rightPanel)
        right_layout.setContentsMargins(0, 0,0, 0)
        right_layout.setSpacing(4)
        
        
       

        btn_right = DockSVG("ArrowMiniRight",None,self.StdIconSize,self.Theme)
        btn_right.clicked.connect(lambda: self.ClientArea.scroll_to("right"))
        
        dsettings = DockSettings(None,self.StdIconSize,self.Theme)
        time_btn = DockTime(None,[72,40],Theme=self.Theme)
        terminal = DockTerminal(self.HAL,None,self.StdIconSize,self.Theme)
        menu = DockSVG('Menu',None,self.StdIconSize,self.Theme)

        internet = DockInternet(None,None,self.StdIconSize,self.Theme)

        btn = QPushButton()
        btn.setFixedSize(20, 40)
        btn.setStyleSheet(self.Theme["Overview"])
        
        
        right_layout.addWidget(btn_right)
        right_layout.addWidget(menu)
        right_layout.addWidget(terminal)
        right_layout.addWidget(internet)
        right_layout.addWidget(dsettings)
        right_layout.addWidget(time_btn)
        right_layout.addWidget(btn)
   


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
