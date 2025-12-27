# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import json 
import subprocess 
from pathlib import Path 
import threading
import socket
from typing import Callable
import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import configparser
from PySide6.QtCore import Signal,QObject

from NLUtils.Logger import NLLogger,ConColors



class HyprSocketEvent:
    def __init__(self, socketPath:str):
        self.socketPath = socketPath
        self.sock = None
        self.connected = False
        self.running = False
        self.thread = None
        self.eventHandlers = {}
        
    def start(self):
        if self.connected:
            return
            
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(self.socketPath)
            self.connected = True
        except Exception as e:
            print(f"Connection error: {e}")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if not self.connected:
            return
            
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.1)
            
        try:
            self.sock.close()
        except:
            pass
            
        self.sock = None
        self.connected = False

    def Bind(self, eventType:str, callback:Callable[[str],None]):
        if eventType not in self.eventHandlers:
            self.eventHandlers[eventType] = []
            
        if callback not in self.eventHandlers[eventType]:
            self.eventHandlers[eventType].append(callback)

    def listen(self):
        """Поток чтения событий из сокета"""
        buffer = b""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                    
                buffer += data
                while b"\n" in buffer:
                    # Разделяем по символу новой строки
                    line, buffer = buffer.split(b"\n", 1)
                    self.eventProcessing(line.strip())
            except:
                if self.running:
                    break

    def eventProcessing(self, EVENT_MESSAGE:bytes):
        """Обработка сырого события в формате 'event>>data'"""
        try:
            if b">>" not in EVENT_MESSAGE:
                return
                
            eventMessage = EVENT_MESSAGE.decode('utf-8', errors='ignore')
            eventType, event_data = eventMessage.split(">>", 1)
            
            
            # Вызываем все обработчики для этого типа события
            if eventType in self.eventHandlers:
                for callback in self.eventHandlers[eventType]:
                    callback(eventType + ">>" + event_data)
        except:
            pass
   
class HyprSocketCtl:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.sock = None
        
        self.lock = threading.Lock()
        self.response_timeout = 2

    def Send(self, command:bytes, waitAnswer=True):
        with self.lock:
            
            tempSock = None
            
            try:
                tempSock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                tempSock.connect(self.socket_path)
                sock = tempSock
            except Exception as e:
                print(e)
                return None
            
                
            try:
                # Отправляем команду
                sock.sendall(command)
                
                if not waitAnswer:
                    return ""
                
                # Читаем ответ с таймаутом
                sock.settimeout(self.response_timeout)
                response = bytearray()
                
                while True:
                    try:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        response.extend(chunk)
                        if b'\x00' in chunk:
                            break
                    except socket.timeout:
                        break
                
                # Удаляем нулевой байт и возвращаем ответ
                return response.replace(b'\x00', b'').decode().strip()
                
            except Exception as e:
                print(e)
                return None
            finally:
                # Закрываем временный сокет
            
                try:
                    tempSock.close()
                except:
                    pass


class EventBridge(QObject):
    eventSignal = Signal(object)

class HyprAL:
    """
    Hyprland Abstraction Layer,
    Описание: Буквально абстракция Hyprland для Python,
    P.S: Этот код вдохновлён дракончиком Нирисом, что до сих пор вдохновляет автора на новые свершения!
    """
    def __init__(self, debug=False, CAL= None,SServer = None):
        #debug
        
        self.CAL=CAL
        self.SServer=SServer
        

        #paths
        
        XDGRD = os.environ.get("XDG_RUNTIME_DIR")
        SIG = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        SOCK = os.path.join(XDGRD,"hypr",SIG,".socket.sock")
        SOCK2 = os.path.join(XDGRD,"hypr",SIG,".socket2.sock")

        #init sockets
        self.HyprCtl = HyprSocketCtl(SOCK)
        self.HyprEvent = HyprSocketEvent(SOCK2)


        
    def HideClient(self,ID:str):
        command = bytes(f'dispatch movetoworkspacesilent 99,address:{ID}','utf-8')
        self.HyprCtl.Send(command)
    
    def MoveToWorkspace(self,workspace:int,ID:str):
        command = bytes(f'dispatch movetoworkspacesilent {workspace},address:{ID}','utf-8')
        self.HyprCtl.Send(command)
    
    def SetClientActive(self,ID:str):
        command = bytes(f'dispatch focuswindow address:{ID}','utf-8')
        self.HyprCtl.Send(command)
        
        

    def GetClients(self):
        return json.loads(self.HyprCtl.Send(b"j/clients",waitAnswer=True))
          
    
    def GetClient(self,ID:str)->dict:
        clients = self.GetClients()
        for client in clients:
            if client["address"] == ID:
                return client
        return None



    def RunProcess(self,command:list):    
        subprocess.Popen(
            command,
            start_new_session=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )



class WorkspacesHAL:
    def __init__(self):
        pass

