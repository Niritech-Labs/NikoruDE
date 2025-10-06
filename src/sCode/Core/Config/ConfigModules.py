# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import sys, os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from NLUtils import NLLogger,ConColors
from pathlib import Path
class NSClientRules():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NSClientRules")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def Write(self,rules:list):
        rulesv2 = ''
        for rule in rules:
            rulesv2 = rulesv2 + "windowrulev2 = "+rule+'\n'
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(rulesv2)
    def Read(self) -> list:
        try:
            rules = []
            with open(self.path, 'r', encoding='utf-8') as file:
                for line in file:
                    _n,rule = line.split('=')
                    rule = rule.rstrip('\n')
                    rules.append(rule)
                return rules    
        except Exception as e:
            self.Logger.Error(e,False)
            return []

class NSessionEnviroments():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NSessionEnviroments")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def Write(self,envs:list):
        envsw = ''
        for env in envs:
            envsw = envsw + "env = "+env+'\n'
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(envsw)
    def Read(self) -> list:
        try:
            envs = []
            with open(self.path, 'r', encoding='utf-8') as file:
                for line in file:
                    _n,env = line.split('=')
                    env = env.rstrip('\n')
                    envs.append(env)
                return envs    
        except Exception as e:
            self.Logger.Error(e,False)
            return []

class NSessionAutostart():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NSessionAutostart")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def Write(self,srvcs:list):
        srvcw = ''
        for srvc in srvcs:
            srvcw = srvcw + "exec-once = "+srvc+'\n'
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(srvcw)
    def Read(self) -> list:
        try:
            srvcs = []
            with open(self.path, 'r', encoding='utf-8') as file:
                for line in file:
                    _n,srvc = line.split('=')
                    srvc = srvc.rstrip('\n')
                    srvcs.append(srvc)
                return srvcs    
        except Exception as e:
            self.Logger.Error(e,False)
            return []
###########################################################       
class NKeyBindings():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NKeyBindings")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def Write(self,srvcs:list):
        srvcw = ''
        for srvc in srvcs:
            srvcw = srvcw + "key = "+srvc+'\n'
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(srvcw)
    def Read(self) -> list:
        try:
            srvcs = []
            with open(self.path, 'r', encoding='utf-8') as file:
                for line in file:
                    _n,srvc = line.split('=')
                    srvc = srvc.rstrip('\n')
                    srvcs.append(srvc)
                return srvcs    
        except Exception as e:
            self.Logger.Error(e,False)
            return []    
#################################################################
class NMonitors():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NMonitors")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def Write(self,dsetings:list):
        dsetingsw = ''
        for dseting in dsetings:
            dsetingsw = dsetingsw + "monitor = "+dseting+'\n'
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(dsetingsw)
    def Read(self) -> list:
        try:
            dsetings = []
            with open(self.path, 'r', encoding='utf-8') as file:
                for line in file:
                    _n,dseting = line.split('=')
                    dseting = dseting.rstrip('\n')
                    dsetings.append(dseting)
                return dsetings    
        except Exception as e:
            self.Logger.Error(e,False)
            return []
        
class NInputDevices():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NInputDevices")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def _getParam(self,line):
        _n,seting = line.split('=')
        return seting.rstrip('\n')

    def Write(self,input:dict):
        inputset = input
        settingstp = 'input {\n' + inputset['touchpad'] + '\n'
        settingsmb = 'input {\n' + f'kb_layout = {inputset['layouts']} \n' + f'kb_options = {inputset['keybind']} \n' + f'follow_mouse = {inputset['follow-mouse']} \n' + f'sensitivity = {inputset['mouse-sensitivity']} \n'
        settingsstr = settingsmb + settingstp + '} \n}'
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(settingsstr)
    def Read(self) -> list:
        try:
            inputset = {}
            with open(self.path, 'r', encoding='utf-8') as file:
                readyR = False
                readed = ''
                for line in file:
                    if 'kb_lay' in line:
                        inputset['layouts'] = self._getParam(line)
                    if 'kb_opt' in line:
                        inputset['keybind'] = self._getParam(line)
                    if 'follow' in line:
                        inputset['follow-mouse'] = self._getParam(line)
                    if 'sensi' in line:
                        inputset['mouse-sensitivity']= self._getParam(line)
                    if readyR and '}' in line:
                        inputset['touchpad'] = readed
                        readyR = False
                    if readyR:
                        readed = readed + line
                    if 'touch' in line:
                        readyR = True
                return inputset    
        except Exception as e:
            self.Logger.Error(e,False)
            return []
##############################################################
class NCompositorAppereance():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NCompositorAppereance")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def _getParam(self,line:str):
        _n,seting = line.split('=')
        return _n.rstrip('\n'),seting.rstrip('\n')

    def Write(self,compositor:dict):
        hyprbar = compositor['windowbar']
        general = compositor['general']
        decoration = compositor['decoration']
        blur = compositor['blur']
        dwindle = compositor['dwindle']
        shadow = compositor['shadow']

        settings = 'plugin { \n hyprbars { \n'
        for key in hyprbar:
            settings = settings + key + ' = ' + hyprbar[key] + '\n'
        settings = settings + '}\n}\ngeneral {\n'
        for key in general:
            settings = settings + key + ' = ' + general[key] + '\n'
        settings = settings + '}\nshadow {\n'
        for key in general:
            settings = settings + key + ' = ' + shadow[key] + '\n'
        settings = settings + '}\ndecoration {\n'
        for key in decoration:
            settings = settings + key + ' = ' + decoration[key] + '\n'
        settings = settings + '}\nblur {\n'
        for key in blur:
            settings = settings + key + ' = ' + blur[key] + '\n'
        settings = settings + '}\ndwindle {\n'
        for key in dwindle:
            settings = settings + key + ' = ' + dwindle[key] + '\n'
        settings = settings + '}\nmaster {\nnew_status = master \n}\nmisc {\nforce_default_wallpaper = -1\ndisable_hyprland_logo = false\n}\ngestures {\nworkspace_swipe = false \n}\n'

        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(settings)
    def Read(self) -> list:
        try:
            hyprbar = {}
            general = {}
            decoration = {}
            compositor = {}
            shadow = {}
            blur = {}
            dwindle = {}
            lineW = 0
            with open(self.path, 'r', encoding='utf-8') as file:
                for line in file:
                    if '}' in line:
                        lineW = 0
                    if lineW == 1:
                        key,param = self._getParam(line)
                        hyprbar[key] = param

                    if lineW == 2:
                        key,param = self._getParam(line)
                        general[key] = param

                    if lineW == 3:
                        key,param = self._getParam(line)
                        decoration[key] = param

                    if lineW == 6:
                        key,param = self._getParam(line)
                        shadow[key] = param

                    if lineW == 4:
                        key,param = self._getParam(line)
                        blur[key] = param

                    if lineW == 5:
                        key,param = self._getParam(line)
                        dwindle[key] = param

                    if 'shadow {' in line:
                        lineW = 6
                    if 'blur {' in line:
                        lineW = 4
                    if 'hyprbars {' in line:
                        lineW = 1
                    if 'dwindle {' in line:
                        lineW = 5
                    if 'decoration {' in line:
                        lineW = 3
                    if 'general {' in line:
                        lineW = 2

                compositor['windowbar'] = hyprbar
                compositor['general'] = general
                compositor['decoration'] = decoration
                compositor['blur'] = blur
                compositor['dwindle'] = dwindle
                compositor['shadow'] = shadow
                return compositor  
        except Exception as e:
            self.Logger.Error(e,False)
            return {}
######################################################################       
class NSessionAnimations():
    def __init__(self,path:str,production:bool):
        self.Logger = NLLogger(production,"NSessionAnimations")
        self.Logger.Info("started",ConColors.V,False)
        self.path = Path(path).expanduser().resolve()

    def _getParam(self,line:str):
        _n,seting = line.split('=')
        return seting.rstrip('\n')
    
    def Write(self,anims:dict):
        animsb = anims['bezier']
        animsa = anims['animation']
        animsw = 'animations { \n' + 'enabled = yes, please :) \n'
        for animb in animsb:
            animsw = animsw + "bezier = "+animb+'\n'
        for anima in animsa:
            animsw = animsw + "animation = "+anima+'\n'
        animsw = animsw + '} \n'
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(animsw)
    def Read(self) -> list:
        try:
            animas = {}
            anims = []
            beziers = []
            with open(self.path, 'r', encoding='utf-8') as file:
                for line in file:
                    if 'bez' in line: 
                        beziers.append(self._getParam(line))
                    if 'animation ' in line:
                        anims.append(self._getParam(line))
                animas['bezier'] = beziers
                animas['animation'] = anims
                return animas   
        except Exception as e:
            self.Logger.Error(e,False)
            return []
        
n = NCompositorAppereance('~/.config/hypr/NCompositorAppereance.conf',False)
print(n.Read())