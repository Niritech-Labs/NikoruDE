# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Settings.Config.ConfigModules import *

C_PRODUCTION = True

class GUI_SettingPlugins():
    def __init__(self,settings: dict):
        self.settings = settings
        self.blockName = 'settings-plugins'
        if not self.blockName in self.settings:
            self.settings[self.blockName] = []
        self.settingBlock = self.settings[self.blockName]
        self.Tab = QWidget()
        self.Name = 'Plugins'
        self.Requires = None

        self.panelSetup()

    def panelSetup(self):
        mainLayout = QVBoxLayout(self.Tab)

        addingWidget = QWidget()
        mainLayout.addWidget(addingWidget)

        addingWidgetLayout = QHBoxLayout(addingWidget)
        addButton = QPushButton('Add Plugin File')
        addingWidgetLayout.addWidget(addButton)

        for plugin in self.settingBlock:
            pluginWidget = QWidget()
            pluginLayout = QHBoxLayout(pluginWidget)
            pluginName = QLabel(plugin)
            deleteButton = QPushButton('X')
            pluginLayout.addWidget(pluginName)
            pluginLayout.addWidget(deleteButton)
            mainLayout.addWidget(pluginWidget)

class GUI_SettingMonitor():
    def __init__(self,settings: dict):
        self.settings = settings
        self.blockName = 'NMonitors'
        self.settingBlock = self.settings[self.blockName]
        self.Tab = QWidget()
        self.Name = 'Monitors'
        self.Requires = 'BASE_Settings'
    
    def Write(self):
        self.settings[self.blockName] = self.settingBlock

class GUI_SettingThemes():
    def __init__(self,settings: dict):
        self.settings = settings
        self.blockName = 'system-style'
        self.settingBlock = self.settings[self.blockName]
        self.Tab = QWidget()
        self.Name = 'Themes'
        self.Requires = 'BASE_Settings'
    
    def Write(self):
        self.settings[self.blockName] = self.settingBlock

#######################################################################################################################################

class BASE_Settings():
    def __init__(self,settings: dict):
        self.production = C_PRODUCTION
        self.settings = settings
        self.Name = 'Nikoru base'

        ############################# HYPRLAND ################################################################
        self.NSessionEnviroments = NSessionEnviroments('~/.config/hypr/NSessionEnviroments.conf',self.production)
        self.NMonitors = NMonitors('~/.config/hypr/NMonitors.conf',self.production)
        self.NInputDevices = NInputDevices('~/.config/hypr/NInputDevices.conf',self.production)
        self.NSClientRules = NSClientRules('~/.config/hypr/NSClientRules.conf',self.production)
        self.NKeyBindings = NKeyBindings('~/.config/hypr/NKeyBindings.conf',self.production)
        self.NSessionAutostart = NSessionAutostart('~/.config/hypr/NSessionAutostart.conf',self.production)
        self.NCompositorAppereance = NCompositorAppereance('~/.config/hypr/NCompositorAppereance.conf',self.production)
        self.NSessionAnimations = NSessionAnimations('~/.config/hypr/NSessionAnimations.conf',self.production)
        ############################# MAKO ####################################################################
    
    def Write(self):
        ############################# HYPRLAND ################################################################
        self.NSessionEnviroments.Write(self.settings["NSessionEnviroments"])
        self.NMonitors.Write(self.settings["NMonitors"])
        self.NInputDevices.Write(self.settings["NInputDevices"])
        self.NSClientRules.Write(self.settings["NSClientRules"])
        self.NKeyBindings.Write(self.settings["NKeyBindings"])
        self.NSessionAutostart.Write(self.settings["NSessionAutostart"])
        self.NCompositorAppereance.Write(self.settings["NCompositorAppereance"])
        self.NSessionAnimations.Write(self.settings["NSessionAnimations"])
        ############################# MAKO ####################################################################

    def Read(self):
        ############################# HYPRLAND ################################################################
        self.settings["NSessionEnviroments"] = self.NSessionEnviroments.Read()
        self.settings["NMonitors"] = self.NMonitors.Read()
        self.settings["NInputDevices"] = self.NInputDevices.Read()
        self.settings["NSClientRules"] = self.NSClientRules.Read()
        self.settings["NKeyBindings"] = self.NKeyBindings.Read()
        self.settings["NSessionAutostart"] = self.NSessionAutostart.Read()
        self.settings["NCompositorAppereance"] = self.NCompositorAppereance.Read()
        self.settings["NSessionAnimations"] = self.NSessionAnimations.Read()
        ############################# MAKO ####################################################################
    