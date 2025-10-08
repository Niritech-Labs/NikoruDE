# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Widgets.AppBase import BaseWindow
from PySide6.QtWidgets import QApplication,QTabWidget,QWidget,QSizePolicy,QVBoxLayout,QStackedWidget,QButtonGroup,QPushButton
from PySide6.QtCore import Qt,QSize
from SettingsBackend import SettingsBackend
from Core.CoreStyle import NikoruThemeManager
import importlib
import inspect
from pathlib import Path
pluginPath = Path('~/.local/share/nikoru/plugins').expanduser()
sys.path.insert(0,str(pluginPath))

class Settings(BaseWindow):
    def __init__(self):
        super().__init__(800, 600, "Settings")
        self.plugins = []
        self.tabs = []
        self.tabPanel = None
        self.production = False

        self.SB = SettingsBackend(True,self.production)
        self.SB.LoadConfig()
        
        self.Style = self.SB.AllSettings['system-style']
        self.TM = NikoruThemeManager(self.Style,self.production)
        self.plugins = self.SB.AllSettings['settings-plugins']
        self.plugins.append('base-settings')
        self._InitBase()
    
    def _InitBase(self):
        self.rootLayout.setContentsMargins(0,0,0,0)
        self.rootLayout.setSpacing(0)
        self.tabPanel = QWidget()
        self.tabPanel.setFixedWidth(250)
        self.tabPanel.setObjectName('SettingsPanel')
        self.rootLayout.addWidget(self.tabPanel)

        self.PanelLayout = QVBoxLayout(self.tabPanel)
        self.PanelLayout.setContentsMargins(8,8,8,8)
        self.PanelLayout.setSpacing(2)
        self.PanelLayout.addStretch()

        self.TabArea = QStackedWidget()
        self.TabArea.setObjectName('SettingsArea')
        self.rootLayout.addWidget(self.TabArea)

        self.TabButtonGroup = QButtonGroup(self)
        self.TabButtonGroup.setExclusive(True)
        self.setStyleSheet(self.TM.ThemeLoad()['main'])
        self._InitPlugins()

        

    def _AddTab(self,widget,title,icon=None):
        index = self.TabArea.count()
        TabButton = QPushButton(title)
        TabButton.setCheckable(True)
        TabButton.setProperty("tab_button", "true")
        TabButton.setCursor(Qt.PointingHandCursor)
        if icon:
            TabButton.setIcon(icon)
            TabButton.setIconSize(QSize(16, 16))
        self.TabButtonGroup.addButton(TabButton, index)
        self.PanelLayout.insertWidget(index, TabButton)
        self.TabArea.addWidget(widget)
        TabButton.clicked.connect(lambda: self._setCurrentIndex(index))      
        if index == 0:
            TabButton.setChecked(True)
        return index
    
    def _setCurrentIndex(self, index):
        if 0 <= index < self.TabArea.count():
            button = self.TabButtonGroup.button(index)
            if button:
                button.setChecked(True)
                self.TabArea.setCurrentIndex(index)
    
    def WriteChanges(self):
        for tab in self.tabs:
            tab.Write()
        self.SB.WriteConfig()
    
    def _InitPlugins(self):
        for plugin in self.plugins:
            self._initPlugin(plugin)
        for tab in self.tabs:
            self._AddTab(tab.Tab,tab.Name)
    def _initPlugin(self,moduleName:str):
        plugin = importlib.import_module(moduleName)
        for name, userSetting in inspect.getmembers(plugin,inspect.isclass):
            if userSetting.__module__ == plugin.__name__ and name.startswith('GUI_Setting'):
                link = userSetting(self.SB.AllSettings)
                self.tabs.append(link)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Settings()
    window.show()
    sys.exit(app.exec())
