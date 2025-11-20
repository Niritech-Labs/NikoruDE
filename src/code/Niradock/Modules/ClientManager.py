# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from Niradock.Modules.DockPanelWidgets import DockScrollClientArea, DockClient
from Niradock.Modules.DBUS import SockServer
from Utils.NLUtils import NLLogger, ConColors, ConfigManager
from Core.CoreHAL import HyprAL, EventBridge
from Core.CoreStyle import ClientDesktopFileManager


class DockClientManager():
    def __init__(self,HAL:HyprAL,production:bool,ClientArea:DockScrollClientArea,Theme = {"Clients":''}, configPath= "~/.config/Nikoru/Clients.confJs"):
        self.eventBridge = EventBridge()
        self.eventBridge.eventSignal.connect(self.UpdateManager)
        self.production = production

        self.Logger = NLLogger(False,"DockClient-Manager")
        self.Logger.Info("started",ConColors.B,False)
        self.ClientArea = ClientArea
        self.HAL = HAL
        self.currentAlignment = Qt.AlignmentFlag.AlignLeft

        self.CM = ConfigManager(configPath,self.production)
        self.SavedClients = self.CM.LoadConfig()
        if self.SavedClients == None or self.SavedClients == '':
            self.SavedClients = {}

        self.IC = {}
        self.ID = {}
        self.blacklist = []

        self.SServer = SockServer(self.HAL,self.Logger)
        self.SServer._SetupServer()

        self.Theme = Theme

        self.CAL = ClientAL(self.HAL,self.Theme,self.ClientArea,self.SavedClients,self.CM) 

        self.targetEvents = ["openwindow", "closewindow", "movewindowv2"]
        for eventType in self.targetEvents:
            self.HAL.hyprEvent.bind(eventType, self._CallbackHyprEvent)
        self.HAL.hyprEvent.start()

        self.InitClients()


    def setAlignment(self, alignment):
        self.currentAlignment = alignment
        self.ClientArea.setAlignment(alignment)

    def InitClients(self):
        for savedClient in self.SavedClients:
            client = self.CAL.LoadPinned(savedClient)
            self.IC[clientData["initialClass"]] = client
            self.ClientArea.clientsLayout.addWidget(client)
            self.ClientArea.setAlignment(self.currentAlignment)
        ClientsData = self.HAL.GetClients()
        for clientData in ClientsData:
            if "Nikoru@" in clientData["initialClass"]:
                self.SServer.ICS[clientData["initialClass"]] = clientData["address"]
            if clientData["initialClass"] in self.IC:
                self.CAL.Reinit(client=self.IC[clientData["initialClass"]],clid=clientData["address"],hidden=clientData["hidden"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]
            else:
                client = self.CAL.Add(IC=clientData["initialClass"],clid=clientData["address"],hidden=clientData["hidden"])
                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)
            self.Logger.Info('Init: Client opened: '+clientData["address"],ConColors.G,False)
            
    def CloseClient(self,id):
        self.Logger.Info('Event: Client closed: '+id,ConColors.G,False)
        self.CAL.Delete(self.ID[id])
        del self.ID[id]

    def OpenClient(self,ID):
        self.Logger.Info('Event: Client opened: '+ID,ConColors.G,False)
        clientData = self.HAL.GetClient(ID)
        # if client exists in Hyprland
        if not clientData == None:
            if clientData["initialClass"] in self.IC:
                #if client on a DockPanel
                self.CAL.Reinit(client=self.IC[clientData["initialClass"]],clid=clientData["address"],hidden=clientData["hidden"])
                self.ID[clientData["address"]] = self.IC[clientData["initialClass"]]
            else:
                #if client not on a DockPanel
                client = self.CAL.Add(IC=clientData["initialClass"],clid=clientData["address"],hidden=clientData["hidden"])
                self.IC[clientData["initialClass"]] = client
                self.ID[clientData["address"]] = client
                self.ClientArea.clientsLayout.addWidget(client)
                self.ClientArea.setAlignment(self.currentAlignment)

    def _CallbackHyprEvent(self, bEvent):
        self.eventBridge.eventSignal.emit(bEvent)

    def UpdateHiddenClient(self,ID,state:bool):
        self.Logger.Info('Event: Client set visible to: '+str(state),ConColors.G,False)
        client = self.ID[ID]
        client.visible[ID] = state

    def ClientFilter(self,byteData:str,byteEvent):
        try:
            if byteData.count(b',') > 0:
                splitedData = byteData.split(b',')
                bid = splitedData[0]
            else:
                bid = byteData
            if byteData.count(b',') > 2:
                btitle = splitedData[3]
                if b'@' in btitle:
                    sys,_name = btitle.split(b'@')
                    if sys == b'Nikoru':
                        title = btitle.decode('utf-8', errors='ignore')
                        if byteEvent == b'openwindow':
                            bid = bid.decode('utf-8', errors='ignore')
                            self.SServer.ICS[title] = "0x"+bid
                            self.Logger.Info('Opened menu window'+title,ConColors.Y,False)
                        if byteEvent == b'closewindow':
                            self.SServer.ICS[title] = None
                            self.Logger.Info('Closed menu window'+title,ConColors.Y,False)
                        if not bid in self.blacklist:
                            self.blacklist.append(bid)
                            return False
                elif btitle == b'':
                    if not bid in self.blacklist:
                        self.blacklist.append(bid)
                    return False
                
            elif bid in self.blacklist:
                return False
            else:
                return True
        except Exception as e:
            self.Logger.Error('Filter: '+str(e))
            return True

    def UpdateManager(self,bEvent: str):
        self.Logger.Info('Current Event: '+bEvent.decode('utf-8', errors='ignore'),ConColors.Y,False)
        bClientEvent, bData = bEvent.split(b'>>')
        if self.ClientFilter(byteData=bData,byteEvent=bClientEvent):
            if b',' in bData:
                bData = bData.split(b',')
                ID = bData[0]
            else:
                ID = bData
            if not ID in self.blacklist:
                ID = ID.decode('utf-8', errors='ignore')
                if bClientEvent == b'openwindow':
                    self.OpenClient('0x'+ID)
                if bClientEvent == b'closewindow':
                    self.CloseClient('0x'+ID)
                if bClientEvent == b'movewindowv2':
                    if bData[1] == b'99':
                        self.UpdateHiddenClient("0x"+ID,state=False)
                    else:
                        self.UpdateHiddenClient("0x"+ID,state=True)
        else:
            self.Logger.Info('Filtered event system service',ConColors.V,False)
           
class ClientAL:
    def __init__(self,HAL:HyprAL,Theme:dict,CA:DockScrollClientArea,savedClients:dict,ConfigManager:ConfigManager):
        self.client = None
        self.HAL = HAL
        self.CM = ConfigManager
        self.SvCl = savedClients
        self.Theme = Theme
        self.ClientArea = CA
        self.CDFM = ClientDesktopFileManager()

    def Reinit(self,client:DockClient,clid:str,hidden:str):
        client.ids.append(clid)
        if hidden == 'false':
            client.visible[clid] = False
        else:
            client.visible[clid] = True
        client.runned[clid] = True

    def Add(self,IC:str,clid:str,hidden:str):
        iconPath,clientExec,title = self.CDFM.GetClientDesktopInfo(IC,'32x32')
        
        icon = QIcon(iconPath) 
        client = DockClient(self.HAL,title,icon,IC,iconPath=iconPath,pinned=False,Theme=self.Theme,toExec=clientExec)
        client.ids.append(clid)
        if hidden == 'false':
            client.visible[clid] = False
        else:
            client.visible[clid] = True
        client.runned[clid] = True
        return client
    
    def LoadPinned(self,LoadedClient:dict):
        IC = LoadedClient['IC']
        title = LoadedClient['title']
        iconPath = LoadedClient['icon-path']
        clientExec = LoadedClient['exec']
        
        icon = QIcon(iconPath) 
        client = DockClient(self.HAL,title,icon,IC,iconPath=iconPath,pinned=False,Theme=self.Theme,toExec=clientExec)
        return client
    
    def SavePinned(self,client:DockClient):
        SavedClient = {}
        iconPath = client.iconPath
        SavedClient['IC'] = client.IC
        SavedClient['title'] = client.title
        SavedClient['exec'] = client.toExec
        SavedClient['icon-path'] = iconPath
        self.SvCl[client.IC] = SavedClient
        self.CM.SaveConfig(self.SvCl)

    
    def Delete(self,client:DockClient):
        if len(client.ids) > 1:
            client.ids.remove(id)
            del client.visible[id]
            del client.runned[id] 
        elif len(client.ids) == 1:
            if not client.pin:
                self.ClientArea.clientsLayout.removeWidget(client)
                client.delete()
                self.ClientArea.reloadAlignment()
                del self.IC[client.IC]
            else:
                client.ids = []
                client.visible = {}
                client.runned = {}
        


       
     