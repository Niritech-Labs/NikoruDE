# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
class InternetAL:
    def __init__(self):
        pass

    def GetInternetDevices(self) -> dict:
        pass

    def ConnectToDevice(self,device,password:str) -> bool:
        pass

    def ReconnectToDevice(self,device) -> bool:
        pass

    def ConfigureDevice(self,device) -> bool:
        pass

    def SwitchRadioDevices(self,device,state):
        pass

    def DisconnectFromDevice(self,device):
        pass

    def SetNMProfile(self,path):
        pass