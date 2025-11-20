# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Settings.Config.ConfigModules import *
import importlib, inspect
from Utils.NLUtils import NLLogger, ConfigManager, ConColors

C_NIKORU_SETTINGS_DIR = '~/.config/Nikoru'
C_PLUGIN_PATH = '~/.local/share/Nikoru/plugins'


class SettingsBackend:
    def __init__(self, FullFunc: bool, production: bool):
        self.Logger = NLLogger(production, "SettingsBackend")
        self.CM = ConfigManager(f'{C_NIKORU_SETTINGS_DIR}/System.confjs',production)

        self.AllSettingsBlocks = {}
        self.configTranslationPluginsClasses = {}

        self.loadConfig()
        self.plugins = self.AllSettingsBlocks['settings-plugins']
        #self.plugins.append('base-settings')
        self.initPlugins()
    
    def SettingsReset(self):
        pass
        
    def ReadConfig(self):
        for classInPluginName in self.configTranslationPluginsClasses:
            pluginClassLink = self.configTranslationPluginsClasses[classInPluginName]
            pluginClassLink.Read()
        
    def SaveAndTranslateConfig(self):
        for classInPluginName in self.configTranslationPluginsClasses:
            pluginClassLink = self.configTranslationPluginsClasses[classInPluginName]
            pluginClassLink.Write()
        self.CM.SaveConfig(self.AllSettingsBlocks)
        
        
    def initPlugins(self):
        for plugin in self.plugins:
            self.initPlugin(plugin)

    def initPlugin(self,moduleName:str):
        plugin = importlib.import_module(moduleName)
        for name, userSetting in inspect.getmembers(plugin,inspect.isclass):
            if userSetting.__module__ == plugin.__name__ and name.startswith('BASE_'):
                link = userSetting(self.AllSettingsBlocks)
                self.configTranslationPluginsClasses[name] = link
        
    def loadConfig(self): 
        self.AllSettingsBlocks = self.CM.LoadConfig()
    @staticmethod
    def GetConfig():
        CM = ConfigManager(f'{C_NIKORU_SETTINGS_DIR}/System.confjs',True)
        return CM.LoadConfig()
        




