# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import json, os
from pathlib import Path


class ConfigManager():
    def __init__(self,path,production:bool):
        self.Logger = NLLogger(production,"ConfigManager")
        self.configPath = Path(path).expanduser().resolve()

    def LoadConfig(self) -> dict: 
        try:
            with open(self.configPath, 'r', encoding='utf-8') as file:
                return json.load(file) 
        except:
            self.Logger.Info("Can't load saved config,creatig new",ConColors.S,False)
            defconf = {}
            self.SaveConfig(defconf)
            return defconf
    
    def OpenRestricted(self,path):
        path = Path(path).expanduser().resolve()
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file) 
        except:
            self.Logger.Error(f"Can't load this config:{path}",False)
            return None
        
    def SaveRestricted(self,path:str,dataToSave:dict):
        try:
            resPath = Path(path).expanduser().resolve()
            if not resPath.exists(): resPath.parent.mkdir(parents=True,exist_ok=True)
            with open(resPath, 'w', encoding='utf-8') as file:
                json.dump(dataToSave, file, ensure_ascii=False, indent=4)

            self.Logger.Info(f'Saved restricted config {str(resPath)}',ConColors.V,False)
        except Exception as e:
            self.Logger.Error(str(e)+f", Can't save this config:{str(resPath)}",False)

    def SaveConfig(self,dataToSave):
        try:
            if not self.configPath.exists(): self.configPath.parent.mkdir(parents=True,exist_ok=True)
            with open(self.configPath, 'w', encoding='utf-8') as file:
                json.dump(dataToSave, file, ensure_ascii=False, indent=4)
            self.Logger.Info(f'Saved main config {str(self.configPath)}',ConColors.V,False)
        except Exception as e:
            self.Logger.Error(str(e)+f", Can't save this config:{str(self.configPath)}",False)


class ConColors: 
    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    B = "\033[94m"
    V = "\033[95m"
    S = "\033[0m"


class NLLogger:
    def __init__(self, production: bool, ComponentName: str = ''):
        self.production = production
        self.name = " " + ComponentName 

    def Warning(self,warn: str):
        print(f"{ConColors.Y} Warning{self.name}: {warn}{ConColors.S}")


    def Error(self,err:str,critical:bool):
        if critical:
            print(f"{ConColors.R} Critical Error{self.name}: {err}{ConColors.S}")
            exit(1)
        else:
            print(f"{ConColors.R} Error{self.name}: {err}{ConColors.S}")
    
    def Info(self,inf:str,color: ConColors, productionLatency: bool):
        if self.production:
            if productionLatency: print(f"{color} Info: {inf}{ConColors.S}")
        else: print(f"{color} Info{self.name}: {inf}{ConColors.S}")
  

class NLTranslator:
    def __init__(self,production:bool,language:str):
        self.writemode = False

        self.rootpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.Logger = NLLogger(production,'NLTranslator')
        self.CM = ConfigManager(self.rootpath+'/Settings.confJs',production)
        if language == 'Config':
            self.language = self.CM.LoadConfig()['language']
        else:
            self.language = language

        self.Logger.Info('Started',ConColors.G,False)

        self.Translation = {}
        self.LoadTranslation()

    def LoadTranslation(self):
        self.Translation = self.CM.OpenRestricted(self.rootpath+'/Translations/'+self.language+'.ntrl')

    def Translate(self,entry:str):
        try:
            return self.Translation[entry]
        except Exception as e:
            if not self.writemode:
                self.Logger.Error(str(e)+f", Can't load translation for this entry: {entry}",False)
                return entry
            else:
                self.Translation[entry] = 'writen'
                self.Logger.Info(f'Entry {entry} writen successfuly',ConColors.B,False)
                return 'writen'


    
