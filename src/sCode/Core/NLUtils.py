import json
from pathlib import Path

class ConfigManager():
    def __init__(self,path,debug = False):
        self.debug = debug
        self.configPath = Path(path).expanduser().resolve()

    def LoadConfig(self):
        try:
            with open(self.configPath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            if(self.debug): print("can't load saved apps,creatig new config")
            defconf = {}
            self.SaveConfig(defconf)
            return defconf

    def SaveConfig(self,configD):
        if not self.configPath.exists(): self.configPath.parent.mkdir(parents=True,exist_ok=True)
        with open(self.configPath, 'w', encoding='utf-8') as file:
            json.dump(configD, file, ensure_ascii=False, indent=4)