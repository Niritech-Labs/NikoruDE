# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import json 
import subprocess 
from pathlib import Path 
import threading
import socket
import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import configparser
from PySide6.QtCore import Signal,QObject

from Utils.NLUtils import NLLogger,ConColors



class HyprSocketEvent:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.sock = None
        self.connected = False
        self.running = False
        self.thread = None
        self.handlers = {}
        
    def start(self):
        if self.connected:
            return
            
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(self.socket_path)
            self.connected = True
        except Exception as e:
            print(f"Connection error: {e}")
            return
        
        # Нет автоматической подписки - сокет сразу начинает получать события
        self.running = True
        self.thread = threading.Thread(target=self._listen)
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

    def bind(self, event_type, callback):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
            
        if callback not in self.handlers[event_type]:
            self.handlers[event_type].append(callback)

    def _listen(self):
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
                    self._process_event(line.strip())
            except:
                if self.running:
                    break

    def _process_event(self, raw_data):
        """Обработка сырого события в формате 'event>>data'"""
        try:
            # Разделяем данные по '>>' (два символа '>')
            if b">>" not in raw_data:
                return
                
            event_type, event_data = raw_data.split(b">>", 1)
            event_type_str = event_type.decode('utf-8', errors='ignore')
            
            # Вызываем все обработчики для этого типа события
            if event_type_str in self.handlers:
                for callback in self.handlers[event_type_str]:
                    callback(event_type + b">>" + event_data)
        except:
            pass
   
class HyprSocketCtl:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.sock = None
        
        self.lock = threading.Lock()
        self.response_timeout = 2

    def send(self, command, waitAnswer=True):
        with self.lock:
            #соединение создаем временное
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
        
        self.CAL= CAL
        self.SServer = SServer
        

        #paths
        
        XDG = os.environ.get("XDG_RUNTIME_DIR")
        SIG = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        SOCK = os.path.join(XDG,"hypr",SIG,".socket.sock")
        SOCK2 = os.path.join(XDG,"hypr",SIG,".socket2.sock")

        #init sockets
        self.hyprctl = HyprSocketCtl(SOCK)
        self.hyprEvent = HyprSocketEvent(SOCK2)


        

        
        
        

    def GetClients(self):
        return json.loads(self.hyprctl.send(b"j/clients",waitAnswer=True))
          
    def _getClientPath(self,pid):
        try: return os.readlink(f'/proc/{pid}/exe')
        except Exception as e: print('\033[33mGet path error:\033[0m',e); return None

    def getClientInfo(self,initialClass:str):
        appPath = f'/usr/share/applications/{initialClass.lower()}.desktop'
        pathI = "/usr/share/icons/hicolor"
        name, icon = self._getAppData(appPath)
        svg = os.path.join(pathI,f"scalable/apps/{icon}.svg")
        png = os.path.join(pathI,f"32x32/apps/{icon}.png")
        if os.path.exists(svg):
            return svg,name,icon
        elif os.path.exists(png):
            return png,name,icon
        return "",name,icon

    def _getName(self,Iclass:str):
        if '.' in Iclass:
            return Iclass.split('.')[-1]
        if '_' in Iclass:
            return Iclass.split('_')[-1]
    
        return Iclass
    
    def GetClient(self,id):
        clients = self.GetClients()
        for client in clients:
            if client["address"] == id:
                return client
        return None

    def _getAppData(self,AppPath):
        """Парсит .desktop файл и возвращает имя и иконку"""
        if not Path(AppPath).exists():
            return '',''

        config = configparser.ConfigParser()
        # Сохраняем регистр ключей
        config.optionxform = lambda option: option  

        try:
            config.read(AppPath, encoding='utf-8')
        except Exception:
            return '',''

        if 'Desktop Entry' not in config:
            return '',''

        entry = config['Desktop Entry']

        # Извлекаем имя с учетом локализации
        currentLang = os.getenv('LANG', 'en_US.UTF-8').split('_')[0]
        lcName = f'Name[{currentLang}]'
    
        title = entry.get(lcName) or entry.get('Name', '')

        # Извлекаем имя иконки (без пути)
        icon = entry.get('Icon', '').strip()

        return title,icon


    def RunProcess(self,cmd):    
        # Popen запускает процесс в фоне
        subprocess.Popen(
            cmd,
            start_new_session=True,  # Не зависит от родительского процесса
            stdout=subprocess.DEVNULL,  # Перенаправляем вывод в никуда
            stderr=subprocess.DEVNULL
        )



class WorkspacesHAL:
    def __init__(self):
        pass

