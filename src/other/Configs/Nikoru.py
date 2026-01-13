# Copyright (C) 2024-2026 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from NLUtils.BaseParserRealizations import HyprlangParser
from NLUtils.Parser import NLParser
from NLUtils.BlocksUtils import Blocks,Block

class PluginInfo:
    Autor = 'Lakur Fessi Nel'
    PluginName = 'Base Nikoru DE Settings'
    Description = 'Foooo'

class SBRThemes:
    def __init__(self,SettingsRoot:Blocks):
        self.SR = SettingsRoot

    def ReadSetting(self):
        pass

    def WriteSetting(self):
        pass

    def InitSetting(self):
        TB = Block('Theme')
        TB.AddParam(['current-theme','Daylight'])
        self.SR.AddBlock(TB)

    def RemoveSetting(self):
        BlockList = self.SR.FindBlock('Theme')
        if BlockList:
            for block in BlockList:
                block.name = None
        self.SR.DeleteMarkedObjects()