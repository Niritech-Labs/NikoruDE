# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from Config.ConfigModules import *
from Core.NLUtils import NLLogger, ConfigManager, ConColors
import dbus
import threading
import json
from PySide6.QtCore import QObject, Signal

class DBusEventBridge(QObject):
    fileOpenResult = Signal(list)
    fileSaveResult = Signal(str)

class DBusPortal:
    def __init__(self):
        self.eventBridge = DBusEventBridge()
        self.bus = dbus.SessionBus()
        self.portal = self.bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop.portal/desktop')
        self.fileChooser = dbus.Interface(self.portal, 'org.freedesktop.portal.FileChooser')
        self.currentOperation = None
        self.operationThread = None

    def openFileThread(self, title, filters):
        try:
            result = [None]
            event = threading.Event()

            def handleResponse(response, results):
                if response == 0:
                    uris = results.get('uris', [])
                    paths = [uri[7:] for uri in uris if uri.startswith('file://')]
                    result[0] = paths if paths else None
                else:
                    result[0] = None
                event.set()

            dbusFilters = []
            for name, patterns in filters:
                dbusFilters.append([name, [[pattern] for pattern in patterns]])

            options = {
                'filters': dbusFilters,
                'handle_token': 'nikoru_file_open'
            }

            requestPath = self.fileChooser.OpenFile('', title, options)
            requestInterface = dbus.Interface(
                self.bus.get_object('org.freedesktop.portal.Desktop', requestPath),
                'org.freedesktop.portal.Request'
            )
            requestInterface.connect_to_signal('Response', handleResponse)

            event.wait(timeout=30)
            self.eventBridge.fileOpenResult.emit(result[0])
            
        except Exception as e:
            self.eventBridge.fileOpenResult.emit(None)
        finally:
            self.currentOperation = None

    def saveFileThread(self, title, filters):
        try:
            result = [None]
            event = threading.Event()

            def handleResponse(response, results):
                if response == 0:
                    uris = results.get('uris', [])
                    if uris:
                        uri = uris[0]
                        if uri.startswith('file://'):
                            result[0] = uri[7:]
                event.set()

            dbusFilters = []
            for name, patterns in filters:
                dbusFilters.append([name, [[pattern] for pattern in patterns]])

            options = {
                'filters': dbusFilters,
                'handle_token': 'nikoru_file_save'
            }

            requestPath = self.fileChooser.SaveFile('', title, options)
            requestInterface = dbus.Interface(
                self.bus.get_object('org.freedesktop.portal.Desktop', requestPath),
                'org.freedesktop.portal.Request'
            )
            requestInterface.connect_to_signal('Response', handleResponse)

            event.wait(timeout=30)
            self.eventBridge.fileSaveResult.emit(result[0])
            
        except Exception as e:
            self.eventBridge.fileSaveResult.emit(None)
        finally:
            self.currentOperation = None

    def openFileAsync(self, title="Open File", filters=[("JSON Files", ["*.json"])]):
        if self.currentOperation is not None:
            return False
            
        self.currentOperation = "open"
        self.operationThread = threading.Thread(
            target=self.openFileThread, 
            args=(title, filters)
        )
        self.operationThread.daemon = True
        self.operationThread.start()
        return True

    def saveFileAsync(self, title="Save File", filters=[("JSON Files", ["*.json"])]):
        if self.currentOperation is not None:
            return False
            
        self.currentOperation = "save"
        self.operationThread = threading.Thread(
            target=self.saveFileThread, 
            args=(title, filters)
        )
        self.operationThread.daemon = True
        self.operationThread.start()
        return True

class SettingsBackend:
    def __init__(self, FullFunc: bool, production: bool):
        self.AllSettings = {}
        self.ReadedConfig = {}
        self.GUI = None
        self.production = False

        self.NSessionEnviroments = None
        self.NMonitors = None
        self.NInputDevices = None
        self.NSClientRules = None
        self.NKeyBindings = None
        self.NSessionAutostart = None
        self.NCompositorAppereance = None
        self.NSessionAnimations = None
        self.Logger = NLLogger(production, "SettingsBackend")
        self.CM = ConfigManager('~/.config/Nikoru/System.confjs')
        #self.portal = DBusPortal()
        self.dbusBusy = False
        
        #self.portal.eventBridge.fileSaveResult.connect(self.onExportResult)
        #self.portal.eventBridge.fileOpenResult.connect(self.onImportResult)
        
        if FullFunc:
            self.InitAll()
    
    def InitAll(self):
        self.GUI = SettingsRealization()
        self.InitTranslators()
        
    def ReadConfig(self):
        self.ReadedConfig["NSessionEnviroments"] = self.NSessionEnviroments.Read()
        self.ReadedConfig["NMonitors"] = self.NMonitors.Read()
        self.ReadedConfig["NInputDevices"] = self.NInputDevices.Read()
        self.ReadedConfig["NSClientRules"] = self.NSClientRules.Read()
        self.ReadedConfig["NKeyBindings"] = self.NKeyBindings.Read()
        self.ReadedConfig["NSessionAutostart"] = self.NSessionAutostart.Read()
        self.ReadedConfig["NCompositorAppereance"] = self.NCompositorAppereance.Read()
        self.ReadedConfig["NSessionAnimations"] = self.NSessionAnimations.Read()
        
    def WriteConfig(self):
        self.NSessionEnviroments.Write(self.AllSettings["NSessionEnviroments"])
        self.NMonitors.Write(self.AllSettings["NMonitors"])
        self.NInputDevices.Write(self.AllSettings["NInputDevices"])
        self.NSClientRules.Write(self.AllSettings["NSClientRules"])
        self.NKeyBindings.Write(self.AllSettings["NKeyBindings"])
        self.NSessionAutostart.Write(self.AllSettings["NSessionAutostart"])
        self.NCompositorAppereance.Write(self.AllSettings["NCompositorAppereance"])
        self.NSessionAnimations.Write(self.AllSettings["NSessionAnimations"])
        self.CM.SaveConfig(self.AllSettings)
        
    def InitTranslators(self):
        self.NSessionEnviroments = NSessionEnviroments('~/.config/hypr/NSessionEnviroments.conf',self.production)
        self.NMonitors = NMonitors('~/.config/hypr/NMonitors.conf',self.production)
        self.NInputDevices = NInputDevices('~/.config/hypr/NInputDevices.conf',self.production)
        self.NSClientRules = NSClientRules('~/.config/hypr/NSClientRules.conf',self.production)
        self.NKeyBindings = NKeyBindings('~/.config/hypr/NKeyBindings.conf',self.production)
        self.NSessionAutostart = NSessionAutostart('~/.config/hypr/NSessionAutostart.conf',self.production)
        self.NCompositorAppereance = NCompositorAppereance('~/.config/hypr/NCompositorAppereance.conf',self.production)
        self.NSessionAnimations = NSessionAnimations('~/.config/hypr/NSessionAnimations.conf',self.production)
        
    def LoadConfig(self): 
        self.AllSettings = self.CM.LoadConfig()

    def SupportImport(self, path: str):
        self.dbusBusy = False
        
""" def ExportConfig(self):
        if self.dbusBusy:
            return
            
        self.dbusBusy = True
        success = self.portal.saveFileAsync(
            title="Export Config", 
            filters=[('Config Files', ['*.confJs'])]
        )
        
        if not success:
            self.dbusBusy = False
            self.Logger.log("Another operation in progress", level=ConColors.WARNING)
        
 def ImportConfig(self):
        if self.dbusBusy:
            return
            
        self.dbusBusy = True
        success = self.portal.openFileAsync(
            title="Import Config", 
            filters=[('JSON Files', ['*.json'])]
        )
        
        if not success:
            self.dbusBusy = False
            self.Logger.log("Another operation in progress", level=ConColors.WARNING)

    def SupportExport(self, path: str):
        try:
            if not path.endswith('.json'):
                path += '.json'
            
            
        except Exception as e:
            self.Logger.log(f"Export failed: {str(e)}", level=ConColors.ERROR)
        
    def SupportImport(self, path: str):

        
        """

class SettingsRealization:
    def __init__(self):
        pass


back = SettingsBackend(True,False)
back.ReadConfig()
back.AllSettings = back.ReadedConfig
back.WriteConfig()
