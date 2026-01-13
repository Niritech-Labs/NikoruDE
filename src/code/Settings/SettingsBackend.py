# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import sys, shutil
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Settings.Config.ConfigModules import *
import importlib.util, inspect
from NLUtils.Logger import NLLogger, ConColors
from NLUtils.JSONUtils import ConfigManager
from NLUtils.Parser import NLParser, NLParserObject
from NLUtils.BaseParserRealizations import BlocksParser
from NLUtils.BlocksUtils import Blocks
from pathlib import Path
from Globals import *



class SettingsBackend:
    def __init__(self, production: bool):
        self.Logger = NLLogger(production, "SettingsBackend")


        self.Parser = NLParser(production)
        self.Parser.SetParserRealization('blocks',BlocksParser)
        self.SM:NLParserObject = self.Parser.OpenFile(f'{C_NIKORU_SETTINGS_DIR}/System.blocks','blocks')

        self.SettingsRoot:Blocks = self.SM.Read()

        self.SBRealizations = {}

        self.loadConfig()
        params = self.SettingsRoot.FindParam('load-plugin')
        if not params:
            params = []
        self.plugins = []
        for param in params:
            self.plugins.append(param[1])
        self.loadPlugins()
    
    
        
    def ReadSBRSettings(self):
        for SBSR in self.SBRealizations:
            PluginSettingRealization = self.SBRealizations[SBSR]
            PluginSettingRealization.ReadSetting()
        
    def Apply(self):
        for SBSettingRealization in self.SBRealizations:
            PluginSettingRealization = self.SBRealizations[SBSettingRealization]
            PluginSettingRealization.WriteSetting()
        self.SM.Write(self.SettingsRoot)

    def AddPlugin(self,pluginName):
        if self.initPlugin(pluginName):
            self.SettingsRoot.AddParam(['load-plugin',pluginName])
        else:
            self.Logger.Warning('Plugin is not valid')

    
    def RemovePlugin(self,pluginName):
        path = Path(C_PLUGIN_PATH+f'/{pluginName}.py').expanduser()
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(pluginName, str(path))
            module = importlib.util.module_from_spec(spec)

            for className, SBRClass in inspect.getmembers(module,inspect.isclass):
                if SBRClass.__module__ == module.__name__ and className.startswith('SBR'):
                    if className in self.SBRealizations:
                        self.SBRealizations[className].RemoveSetting()
                        del self.SBRealizations[className]

            pluginList = self.SettingsRoot.FindParam('load-plugin')
            for plugin in pluginList:
                if plugin[1] == pluginName:
                    plugin[0] = None
            self.SettingsRoot.DeleteMarkedObjects()
        else:
            self.Logger.Warning(f'Plugin {pluginName} not found')
            
    def loadPlugins(self):
        for pluginName in self.plugins:
            self.loadPlugin(pluginName)

    def loadPlugin(self,moduleName:str):
        path = Path(C_PLUGIN_PATH+f'/{moduleName}.py').expanduser()
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(moduleName, str(path))
            module = importlib.util.module_from_spec(spec)

            for className, SBRClass in inspect.getmembers(module,inspect.isclass):
                if SBRClass.__module__ == module.__name__ and className.startswith('SBR'):
                    SBRealization = self.checkSBR(SBRClass)
                    if SBRealization:
                        pointer = SBRClass(self.SettingsRoot)
                        self.SBRealizations[className] = pointer
        else:
            self.Logger.Warning(f'Plugin {moduleName} not found')

    def initPlugin(self,moduleName:str):
        path = Path(C_PLUGIN_PATH+f'/{moduleName}.py').expanduser()
        if os.path.exists(path):
            
            spec = importlib.util.spec_from_file_location(moduleName, str(path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for className, SBRClass in inspect.getmembers(module,inspect.isclass):
                if SBRClass.__module__ == module.__name__ and className.startswith('SBR'):
                  
                    SBRealization = self.checkSBR(SBRClass)
                    if SBRealization:
                     
                        pointer = SBRClass(self.SettingsRoot)
                        pointer.InitSetting()
                        self.SBRealizations[className] = pointer
            return True
        else:
            self.Logger.Warning(f'Plugin {moduleName} not found')
            return False

    

    def checkSBR(self,realization):
        try:
            if not (callable(getattr(realization,'WriteSetting')) 
                and callable(getattr(realization,'ReadSetting'))
                and callable(getattr(realization,'InitSetting'))
                and callable(getattr(realization,'RemoveSetting'))
                ):
                return None
    
            else:
                return realization
            
        except Exception:
            self.Logger.Warning(str(type(realization))+'is not valid')

        
    def loadConfig(self): 
        self.SettingsRoot:Blocks = self.SM.Read()

    @staticmethod
    def GetConfig() -> Blocks | None:
        Parser = NLParser(True)
        Parser.SetParserRealization('blocks',BlocksParser)
        SM:NLParserObject = Parser.OpenFile(f'{C_NIKORU_SETTINGS_DIR}/System.blocks','blocks')
        return SM.Read()
    

    @staticmethod
    def SettingsSetup():
        Parser = NLParser(True)
        Parser.SetParserRealization('blocks',BlocksParser)

        ######### CREATE PATHS ###########
        NSettingsPath = Path(C_NIKORU_SETTINGS_DIR).expanduser()
        NSettingsPath.mkdir(parents=True, exist_ok=True)
        NSettingsPath.chmod(0o700)
        NPluginPath = Path(C_PLUGIN_PATH).expanduser()
        NPluginPath.mkdir(parents=True, exist_ok=True)
        NPluginPath.chmod(0o700)

        shutil.copyfile(C_APPDATA_DIR+'/Configs/Nikoru.py',str(Path(C_PLUGIN_PATH+'/Nikoru.py').expanduser()))


        SM:NLParserObject = Parser.OpenFile(f'{C_NIKORU_SETTINGS_DIR}/System.blocks','blocks')
        root = Blocks('settings')
        root.AddParam(['meta','autogenerated'])
        SM.Write(root)

        SB = SettingsBackend(True)
        SB.AddPlugin('Nikoru')
        SB.Apply()
        
        
        




