# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from Niradock.Modules.DockPanelWidgets import DockScrollClientArea, DockClientGroup
from Niradock.Modules.DBUS import SockServer
from Core.CoreHAL import HyprAL, EventBridge
from Core.CoreStyle import ClientDesktopFileManager
from NLUtils.BlocksUtils import Blocks
from NLUtils.Logger import NLLogger, ConColors
from NLUtils.JSONUtils import ConfigManager


class ClientDB:
    def __init__(self,production:bool,name:str):
        self.Logger = NLLogger(production,f'Client Database {name}')
        self.AGDB = {}
        self.IDtoCG = {}

    def SetNewClientGroup(self,groupName:str,ClientGroup:DockClientGroup):
        if groupName in self.AGDB:
            self.Logger.Warning(f"Client Group with name: {groupName} is exist")
        else:
            self.AGDB[groupName] = ClientGroup

    
    def UnsetAppGroup(self,groupName:str):
        if groupName in self.AGDB:
            del self.AGDB[groupName]   
        else:
            self.Logger.Warning(f"Client Group with name: {groupName} is not exist")

    def GetClientGroupFromGroupName(self,groupName:str) -> DockClientGroup:
        if groupName in self.AGDB:
            return self.AGDB[groupName]
        else:
            self.Logger.Warning(f"Client Group with name: {groupName} is not exist")

    def CheckGroup(self,groupName:str):
        if groupName in self.AGDB:
            return True
        else:
            return False
        
    def GetClientGroupFromID(self,ID) -> DockClientGroup:
        if ID in self.IDtoCG:
            return self.IDtoCG[ID]
        else:
            self.Logger.Warning(f"id:{ID} in Client Group is not exist")
        
    def UnsetClientGroupFromIDLink(self,ID):
        if ID in self.IDtoCG:
            del self.IDtoCG[ID]
        else:
            self.Logger.Warning(f"id:{ID} in Client Group is not exist")

    def SetClientGroupFromIDLink(self,ID,ClientGroup):
        if not ID in self.IDtoCG:
            self.IDtoCG[ID] = ClientGroup
        else:
            self.Logger.Warning(f"id:{ID} in Client Group is not exist")
            self.IDtoCG[ID] = ClientGroup



    


    
    
    



class ClientAgregator:
    def __init__(self,HAL:HyprAL,production:bool,ClientGroupArea:DockScrollClientArea,Theme = {"Clients":''}):
        self.production = production

        self.HAL = HAL

        self.eventBridge = EventBridge()
        self.eventBridge.eventSignal.connect(self.clientEventAgregator)

        self.Logger = NLLogger(False,"Client-Agregator")
        self.Logger.Info("started",ConColors.B,False)

        self.blacklist = []

      
        self.DECM = DEClientManager(HAL)
        self.GUICM = DockClientManager(HAL,self.production,ClientGroupArea,Theme)
        self.currentAlignment = Qt.AlignmentFlag.AlignLeft

        self.targetEvents = ["openwindow", "closewindow", "movewindowv2"]
        for eventType in self.targetEvents:
            self.HAL.HyprEvent.Bind(eventType, self.callbackHyprEvent)
        self.HAL.HyprEvent.start()


    def SetAligment(self,aligment):
        self.GUICM.setAlignment(aligment)

    def callbackHyprEvent(self, eventMessage:str):
        self.eventBridge.eventSignal.emit(eventMessage)

    def clientEventAgregator(self,eventMessage:str):
        self.Logger.Info('Current Event: '+eventMessage,ConColors.Y,False)
        clientEvent, clientData = eventMessage.split('>>')

        try:
            if clientData.count(',') > 0:
                splitedData = clientData.split(',')
                ID = splitedData[0]
            else:
                ID = clientData
                if ('0x'+ID) in self.DECM.ServiceClients:
                    self.DECM.ServiceEventProcess(clientEvent,clientData)
                    if not ID in self.blacklist:
                        self.blacklist.append(ID)
                    return
            if clientData.count(',') > 2:
                title = splitedData[3]
                if 'Nikoru-' in title:
                    self.DECM.ServiceEventProcess(clientEvent,clientData)
                    if not ID in self.blacklist:
                        self.blacklist.append(ID)
                    return
                        
                elif title == '':
                    if not ID in self.blacklist:
                        self.blacklist.append(ID)

                
            if ID in self.blacklist:
                return False
            else:
                self.GUICM.EventManager(clientEvent,clientData)
        except Exception as e:
            self.Logger.Error('Filter: '+str(e),False)
            return True

    
    


class DockClientManager():
    def __init__(self,HAL:HyprAL,production:bool,ClientGroupArea:DockScrollClientArea,Theme:dict):
        self.production = production

        self.CGDB = ClientDB(production,'Standard')

        self.Logger = NLLogger(False,"DockClient-Manager")
        self.Logger.Info("started",ConColors.B,False)
        
        self.ClientGroupArea = ClientGroupArea
        self.HAL = HAL
        self.currentAlignment = Qt.AlignmentFlag.AlignLeft

       
        self.savedClientGroups = {}

        self.Theme = Theme

        self.CAL = ClientAL(self.HAL,self.Theme,self.ClientGroupArea,self.savedClientGroups,self.CGDB) 

        self.initClients()


    def setAlignment(self, alignment):
        self.currentAlignment = alignment
        self.ClientGroupArea.setAlignment(alignment)

   
    def EventManager(self,clientEvent:str,data:str):
        if ',' in data:
            data = data.split(',')
            ID = data[0]
        else:
            ID = data

        
        if clientEvent == 'openwindow':
            self.OpenClient('0x'+ID)
        if clientEvent == 'closewindow':
            self.CloseClient('0x'+ID)
        if clientEvent == 'movewindowv2':
            if data[1] == '99':
                self.UpdateHiddenClient("0x"+ID,state=False)
            else:
                self.UpdateHiddenClient("0x"+ID,state=True)


    def initClients(self):
        for savedClientGroupParams in self.savedClientGroups:
            DockClientGroup = self.CAL.LoadPinnedGroup(savedClientGroupParams)

            self.CGDB.SetNewClientGroup(DockClientGroup.ClientData.FindParam("IC")[1],DockClientGroup)

            self.ClientGroupArea.AddClientGroup(DockClientGroup)
            self.ClientGroupArea.setAlignment(self.currentAlignment)

        ClientsData = self.HAL.GetClients()
        for clientDataFromHyprland in ClientsData:
            self.initClient(clientDataFromHyprland)
            self.Logger.Info(f'Init: Client opened: {clientDataFromHyprland["address"]}',ConColors.G,False)

    def initClient(self, clientDataFromHyprland):
        clientGroupName = clientDataFromHyprland["initialClass"]
        ID = clientDataFromHyprland["address"]

        if self.CGDB.CheckGroup(clientGroupName):
            DockClientGroup = self.CGDB.GetClientGroupFromGroupName(clientGroupName)
            self.CGDB.SetClientGroupFromIDLink(ID,DockClientGroup)

            self.CAL.Reinit(DockClientGroup,ID,clientDataFromHyprland["hidden"])
        else:
            DockClientGroup = self.CAL.Add(clientGroupName,ID,hidden=clientDataFromHyprland["hidden"])
            self.CGDB.SetClientGroupFromIDLink(ID,DockClientGroup)
            self.CGDB.SetNewClientGroup(clientGroupName,DockClientGroup)

            IDDB = DockClientGroup.GetIDDB()
            IDDB.append(ID)
               
            self.ClientGroupArea.AddClientGroup(DockClientGroup)
            self.ClientGroupArea.setAlignment(self.currentAlignment)
    
    def CloseClient(self,ID):
        self.Logger.Info('Event: Client closed: '+ID,ConColors.G,False)
        DockClientGroup = self.CGDB.GetClientGroupFromID(ID)
        self.CGDB.UnsetClientGroupFromIDLink(ID)
        self.CAL.Delete(DockClientGroup,ID)
        

    def OpenClient(self,ID):
        self.Logger.Info('Event: Client opened: '+ID,ConColors.G,False)
        clientDataFromHyprland = self.HAL.GetClient(ID)
        self.initClient(clientDataFromHyprland)


    def UpdateHiddenClient(self,ID,state:bool):
        self.Logger.Info('Event: Client set visible to: '+str(state),ConColors.G,False)
        ClientGroup:DockClientGroup = self.CGDB.GetClientGroupFromID(ID)
        ClientGroup.visibleData[ID] = state

           
class ClientAL:
    def __init__(self,HAL:HyprAL,Theme:dict,CA:DockScrollClientArea,savedClients:dict,ClientGroupDatabase:ClientDB):
        self.client = None
        self.HAL = HAL
        self.CM = ConfigManager
        self.SvCl = savedClients
        self.Theme = Theme
        self.ClientArea = CA
        self.CDFM = ClientDesktopFileManager()
        self.CGDB = ClientGroupDatabase

    def Reinit(self,ClientGroup:DockClientGroup,ID:str,hidden:str):
        IDDB = ClientGroup.GetIDDB()
        IDDB.append(ID)
        if hidden == 'false':
            ClientGroup.visibleData[ID] = False
        else:
            ClientGroup.visibleData[ID] = True
        ClientGroup.runned[ID] = True

    def Add(self,ClientGroupName:str,ID:str,hidden:str):
        iconPath,clientExec,title = self.CDFM.GetClientDesktopInfo(ClientGroupName,'32x32')
        
        icon = QIcon(iconPath) 
        ClientData = Blocks(ClientGroupName)
        ClientData.AddParam(['to-exec',clientExec])
        ClientData.AddParam(['title',title])
        ClientData.AddParam(['icon',icon])
        ClientData.AddParam(['IC',ClientGroupName])
        ClientData.AddParam(['icon-path',iconPath])
        
        ClientGroup = DockClientGroup(self.HAL,self.Theme,ClientData)

        IDDB = ClientGroup.GetIDDB()
        IDDB.append(ID)

        ClientGroup.UnpinClientGroup()

        if hidden == 'false':
            ClientGroup.visibleData[ID] = False
        else:
            ClientGroup.visibleData[ID] = True
        ClientGroup.runned[ID] = True
        return ClientGroup
    
    #Fixed
    def LoadPinnedGroup(self,LoadedClient:dict):
        IC = LoadedClient['IC']
        title = LoadedClient['title']
        iconPath = LoadedClient['icon-path']
        icon = QIcon(iconPath) 
        clientExec = LoadedClient['to-exec']


        ClientData = Blocks(IC)
        ClientData.AddParam(['to-exec',clientExec])
        ClientData.AddParam(['title',title])
        ClientData.AddParam(['icon',icon])
        ClientData.AddParam(['IC',IC])
        ClientData.AddParam(['icon-path',iconPath])
        
        ClientGroup = DockClientGroup(self.HAL,self.Theme,ClientData)
        ClientGroup.PinClientGroup()
        return ClientGroup
    
    def SavePinned(self,client:DockClientGroup):
        pass
        

    
    def Delete(self,ClientGroup:DockClientGroup,ID:str):
        IDDB = ClientGroup.GetIDDB()
        IDDB.remove(ID)
        if len(IDDB) > 1:
            IDDB.remove(ID)
            del ClientGroup.visibleData[ID]
            del ClientGroup.runned[ID] 
        elif len(IDDB) == 1:
            if not ClientGroup.pinState:
                self.ClientArea.ClientGroupsLayout.removeWidget(ClientGroup)
                self.ClientArea.reloadAlignment()
                self.CGDB.UnsetAppGroup(ClientGroup.ClientData.name)
                ClientGroup.Delete()
            else:
                IDDB = []
                ClientGroup.visibleData = {}
                ClientGroup.runned = {}
        
class DEClientManager:
    def __init__(self, HAL:HyprAL):
        self.Logger = NLLogger(False,"DE-ClientManager")
        self.Logger.Info("started",ConColors.B,False)
        self.HAL = HAL

        self.ServiceClients = {}
        self.SockServer = SockServer(self.HAL,self.Logger,self.ServiceClients)
        self.SockServer.SetupServer()

    def AddToIC(self,ID:str,IC:str):
        self.SockServer.ICS[IC] = ID

    def ServiceEventProcess(self,clientEvent:str,clientData:str):
        splitedData = clientData.split(',')

        title = splitedData[3]
        servicePointer,panelPointer = title.split('-')
        ID = splitedData[0]
        if clientEvent == 'openwindow':
            self.ServiceClients[title] = "0x"+ID
            self.Logger.Info('Opened Nikoru Panel '+title,ConColors.Y,False)
        if clientEvent == 'closewindow':
            del self.ServiceClients[title]
            self.Logger.Info('Closed Nikoru Panel '+title,ConColors.Y,False)

       
     