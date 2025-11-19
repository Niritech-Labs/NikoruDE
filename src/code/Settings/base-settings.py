from PySide6.QtWidgets import QWidget,QVBoxLayout

class GUI_SettingMonitor():
    def __init__(self,settings: dict):
        self.settings = settings
        self._blockName = 'NMonitors'
        self.settingBlock = self.settings[self._blockName]
        self.Tab = QWidget()
        self.Name = 'Monitors'
    
    def Write(self):
        self.settings[self._blockName] = self.settingBlock

class GUI_SettingThemes():
    def __init__(self,settings: dict):
        self.settings = settings
        self._blockName = 'system-style'
        self.settingBlock = self.settings[self._blockName]
        self.Tab = QWidget()
        self.Name = 'Themes'
    
    def Write(self):
        self.settings[self._blockName] = self.settingBlock