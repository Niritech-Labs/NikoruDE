# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,QPushButton,QHBoxLayout,QSpacerItem,QSizePolicy 
from Core.CoreHAL import HyprAL
from QtCustomWidgets import DockClientManager,DockSettings,DockTime,DockScrollClientArea,DockSVG,DockTerminal,DockInternet,DockPower,DockWorkspaces
"""Вы уж извините,но использовать встроенный языковой переводчик я не буду, его написали больные мазохизмом люди! каждый перевод писать заново? ну уж нет!"""
class DockPanel(QMainWindow):
    """Док панель,здесь вы найдёте Нириса в качестве пасхалки"""
    def __init__(self,HAl:HyprAL,debug = False):
        super().__init__()
        self.buttons = []
        # Настройка окна
        self.debug = debug
        self.HAL = HAl
        self.app_alignment = 'center'
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background: #2D2D2D;")
        
        # Настройка начального размера и позиции
        rootWidget = QWidget()
        rootLayoutLRC = QHBoxLayout(rootWidget)
        rootLayoutLRC.setContentsMargins(0, 0, 0, 0)
        rootLayoutLRC.setSpacing(0)

       
        self._initLeftPanel()
        # Центральная область (растягивается)
        self.ClientArea = DockScrollClientArea()
        self.ClientManadger = DockClientManager(self.HAL,self.ClientArea,self)
        self._initRightPanel()
        #self.AppManadger.LoadApps()


        # Собираем все вместе
        rootLayoutLRC.addWidget(self.leftPanel)
        rootLayoutLRC.addWidget(self.ClientArea,1)
        rootLayoutLRC.addWidget(self.rightPanel)

        self.setCentralWidget(rootWidget)
        # Стилизация
        self.setStyleSheet("""
            QMainWindow {
                background: #2d2d2d;
                border-top: 2px solid #3e3e3e;
            }
        """)
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
        self.btn_left = DockSVG("ArrowMiniLeft")
        
        self.btn_left.clicked.connect(lambda: self.ClientArea.scroll_to("left"))
        if self.debug: self.leftPanel.setStyleSheet("""QWidget {background: #f54336;}""")
        
        power = DockPower()
        layers = DockWorkspaces(None)
        # Добавляем 2 кнопки
        left_layout.addWidget(power)
        left_layout.addWidget(layers)
        left_layout.addWidget(self.btn_left)

    def _initRightPanel(self):
        # Правая область (200px)
        self.rightPanel = QWidget()
        #right_widget.setFixedWidth(200)
        right_layout = QHBoxLayout(self.rightPanel)
        right_layout.setContentsMargins(0, 0,0, 0)
        right_layout.setSpacing(4)
        
        if self.debug: self.rightPanel.setStyleSheet("""QWidget {background: #ff1100;}""")
        # Добавляем 2 обычные кнопки и DateTimeButton

        btn_right = DockSVG("ArrowMiniRight")
        btn_right.clicked.connect(lambda: self.ClientArea.scroll_to("right"))
        
        dsettings = DockSettings()
        time_btn = DockTime()
        terminal = DockTerminal(self.HAL)
        menu = DockSVG('Menu')

        internet = DockInternet(None)

        btn = QPushButton()
        btn.setFixedSize(20, 40)
        btn.setStyleSheet("""
                QPushButton {
                    background: #2d2d2d;
                    border: 0px solid #505050;
                    border-radius: 4px;
                }
            """)
        
        right_layout.addWidget(btn_right)
        right_layout.addWidget(menu)
        right_layout.addWidget(terminal)
        right_layout.addWidget(internet)
        right_layout.addWidget(dsettings)
        right_layout.addWidget(time_btn)
        right_layout.addWidget(btn)
   

    def add_test_buttons(self, count):
        for i in range(count):
            btn = QPushButton(f"{i+1}")
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
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
            self.buttons.append(btn)
            self.ClientArea.clientsLayout.addWidget(btn)

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

    # Демонстрация изменения размера через таймер






sys.exit(app.exec())
