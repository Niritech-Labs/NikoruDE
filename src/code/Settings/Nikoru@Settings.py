# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ShareModules.AppBase import BaseWindow
from PySide6.QtWidgets import QApplication,QTabWidget,QWidget,QSizePolicy,QVBoxLayout,QStackedWidget,QButtonGroup,QPushButton
from PySide6.QtCore import Qt,QSize
from SettingsBackend import SettingsBackend, C_PLUGIN_PATH
from Core.CoreStyle import NikoruThemeManager
import importlib
import inspect
from pathlib import Path

sys.path.insert(0,str(Path(C_PLUGIN_PATH).expanduser()))

class Settings(BaseWindow):
    def __init__(self):
        super().__init__(800, 600, "Settings")
        self.plugins = []
        self.tabs = []
        self.tabPanel = None
        self.production = False

        self.SB = SettingsBackend(True,self.production)
        self.BTCPClasses = self.SB.configTranslationPluginsClasses
        self.SB.loadConfig()
        
        self.systemStyleSettingsBlock = self.SB.AllSettingsBlocks['system-style']
        self.TM = NikoruThemeManager(self.systemStyleSettingsBlock,self.production)
        self.plugins = self.SB.AllSettingsBlocks['settings-plugins']
        #self.plugins.append('base-settings')
        self.initBase()
    
    def initBase(self):
        self.rootLayout.setContentsMargins(0,0,0,0)
        self.rootLayout.setSpacing(0)
        self.tabPanel = QWidget()
        self.tabPanel.setFixedWidth(250)
        self.tabPanel.setObjectName('color+1')
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
        self.setStyleSheet(self.TM.GetTheme()['main'])
        self.initPlugins()

        

    def addTab(self,widget,title,icon=None):
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
        TabButton.clicked.connect(lambda: self.setCurrentIndex(index))      
        if index == 0:
            TabButton.setChecked(True)
        return index
    
    def setCurrentIndex(self, index):
        if 0 <= index < self.TabArea.count():
            button = self.TabButtonGroup.button(index)
            if button:
                button.setChecked(True)
                self.TabArea.setCurrentIndex(index)
    
    def writeChanges(self):
        for tab in self.tabs:
            tab.Write()
        self.SB.SaveAndTranslateConfig()
    
    def initPlugins(self):
        for plugin in self.plugins:
            self.initPlugin(plugin)
        for tab in self.tabs:
            self.addTab(tab.Tab,tab.Name)
    def initPlugin(self,moduleName:str):
        plugin = importlib.import_module(moduleName)
        for name, userSetting in inspect.getmembers(plugin,inspect.isclass):
            if userSetting.__module__ == plugin.__name__ and name.startswith('GUI_Setting'):
                settingsGUIObject = userSetting(self.SB.AllSettingsBlocks)
                if settingsGUIObject.Requires in self.BTCPClasses or settingsGUIObject.Requires == None:
                    self.tabs.append(settingsGUIObject)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Settings()
    window.show()
    sys.exit(app.exec())

