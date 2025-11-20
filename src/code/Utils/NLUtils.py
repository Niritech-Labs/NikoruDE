# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import json, os
from pathlib import Path


class ConfigManager():
    def __init__(self,path,production:bool):
        self.LOG = NLLogger(production,"ConfigManager")
        self.configPath = Path(path).expanduser().resolve()

    def LoadConfig(self) -> dict: 
        try:
            with open(self.configPath, 'r', encoding='utf-8') as file:
                return json.load(file) 
        except:
            self.LOG.Info("Can't load saved config,creatig new",ConColors.S,False)
            defconf = {}
            self.SaveConfig(defconf)
            return defconf
    
    def OpenRestricted(self,path):
        path = Path(path).expanduser().resolve()
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file) 
        except:
            self.LOG.Error(f"Can't load this config:{path}",False)
            return None
        
    def SaveRestricted(self,path:str,dataToSave:dict):
        try:
            resPath = Path(path).expanduser().resolve()
            if not resPath.exists(): resPath.parent.mkdir(parents=True,exist_ok=True)
            with open(resPath, 'w', encoding='utf-8') as file:
                json.dump(dataToSave, file, ensure_ascii=False, indent=4)

            self.LOG.Info(f'Saved restricted config {str(resPath)}',ConColors.V,False)
        except Exception as e:
            self.LOG.Error(str(e)+f", Can't save this config:{str(resPath)}",False)

    def SaveConfig(self,dataToSave):
        try:
            if not self.configPath.exists(): self.configPath.parent.mkdir(parents=True,exist_ok=True)
            with open(self.configPath, 'w', encoding='utf-8') as file:
                json.dump(dataToSave, file, ensure_ascii=False, indent=4)
            self.LOG.Info(f'Saved main config {str(self.configPath)}',ConColors.V,False)
        except Exception as e:
            self.LOG.Error(str(e)+f", Can't save this config:{str(self.configPath)}",False)


class ConColors: 
    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    B = "\033[94m"
    V = "\033[95m"
    S = "\033[0m"


class NLLogger:
    def __init__(self, production: bool, ComponentName: str = '',logList:list = ['toConsole']):
        self.production = production
        self.toLogList = False
        self.logList = logList
        if not 'toConsole' in logList:
            self.toLogList = True
        self.name = " " + ComponentName 

    def Warning(self,warn: str):
        if self.toLogList:
            self.logList.append(f"{ConColors.Y} Warning{self.name}: {warn}{ConColors.S}")
        print(f"{ConColors.Y} Warning{self.name}: {warn}{ConColors.S}")


    def Error(self,err:str,critical:bool):
        if critical:
            if self.toLogList:
                self.logList.append(f"{ConColors.R} Critical Error{self.name}: {err}{ConColors.S}")
            print(f"{ConColors.R} Critical Error{self.name}: {err}{ConColors.S}")
            exit(1)
        else:
            if self.toLogList:
                self.logList.append(f"{ConColors.R} Error{self.name}: {err}{ConColors.S}")
            print(f"{ConColors.R} Error{self.name}: {err}{ConColors.S}")
    
    def Info(self,inf:str,color: ConColors, productionLatency: bool):
        if self.production:
            if productionLatency: 
                if self.toLogList:
                    self.logList.append(f"{color} Info{self.name}: {inf}{ConColors.S}")
                print(f"{color} Info{self.name}: {inf}{ConColors.S}")
        else:
            if self.toLogList:
                self.logList.append(f"{color} Info{self.name}: {inf}{ConColors.S}")
            print(f"{color} Info{self.name}: {inf}{ConColors.S}")
  

class NLTranslator:
    def __init__(self,production:bool,language:str,WRITEMODE = False):
        self.writemode = WRITEMODE

        self.rootpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.LOG = NLLogger(production,'NLTranslator')
        self.CM = ConfigManager(self.rootpath+'/Settings.confJs',production)
        if language == 'Config':
            self.language = self.CM.LoadConfig()['language']
        else:
            self.language = language

        self.LOG.Info('Started',ConColors.G,False)

        self.Translation = {}
        self.loadTranslation()

    def loadTranslation(self):
        self.Translation = self.CM.OpenRestricted(self.rootpath+'/Translations/'+self.language+'.ntrl')

    def Translate(self,entry:str):
        try:
            return self.Translation[entry]
        except Exception as e:
            if not self.writemode:
                self.LOG.Error(str(e)+f", Can't load translation for this entry: {entry}",False)
                return entry
            else:
                self.Translation[entry] = 'writen'
                self.LOG.Info(f'Entry {entry} writen successfuly',ConColors.B,False)
                return 'writen'


    
