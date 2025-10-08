import os
import subprocess 
import configparser
from Core.NLUtils import NLLogger,ConfigManager
class AppDesktopManager:
	def __init__(self,resolution: str,theme: str):
		self.resolution = resolution
		self.CM = ConfigManager("/usr/share/icons/NikoruThemeStd/icons.chache")
		self.chache = self.CM.LoadConfig()
		self.currentTheme = theme
		
	def ReadDotDesktop(self,name):
		desktop = Desktop(f'/usr/share/applications/{name}.desktop')
		if not '/' in desktop.Dicon:
			icoPath = self.Find(desktop.Dicon,self.resolution)
		elif not desktop.Dicon == None: icoPath = desktop.Dicon
		else: icoPath = self.Find(desktop.Dicon,self.resolution)
		return (icoPath, desktop.Dexec,desktop.Dtitle)
	
	def Find(self, name, scale):
		if os.path.exists(f"/usr/share/icons/NikoruThemeStd/scalable/{name}.svg"):
			return f"/usr/share/icons/NikoruThemeStd/scalable/{name}.svg"
		if os.path.exists(f"/usr/share/icons/NikoruThemeStd/{scale}/{name}.png"):
			return f"/usr/share/icons/NikoruThemeStd/{scale}/{name}.png"
		if os.path.exists(f"/usr/share/icons/NikoruThemeStd/other/{name}.png"):
			return f"/usr/share/icons/NikoruThemeStd/other/{name}.png"
		if os.path.exists(f"/usr/share/icons/NikoruThemeStd/other/{name}.svg"):
			return f"/usr/share/icons/NikoruThemeStd/other/{name}.svg"
		return f"/usr/share/icons/NikoruThemeStd/scalable/notFound.svg"
	@staticmethod
	def LFind(name, scales,theme):
		icons = {}
		if os.path.exists(f"/usr/share/icons/{theme}/scallable/{name}.svg"):
			icons['scallable'] = f"/usr/share/icons/{theme}/scalable/{name}.svg"
		elif os.path.exists(f"/usr/share/icons/hicolor/scallable/{name}.svg"):
			icons['scallable'] = f"/usr/share/icons/hicolor/scallable/{name}.svg"

		for scale in scales:
			if os.path.exists(f"/usr/share/icons/{theme}/{scale}/{name}.png"):
				icons[scale] = f"/usr/share/icons/{theme}/{scale}/{name}.png"
			elif os.path.exists(f"/usr/share/icons/hicolor/{scale}/{name}.png"):
				icons[scale] = f"/usr/share/icons/hicolor/{scale}/{name}.png"
		if icons == {}: return None
		else: return icons
	@staticmethod
	def GetTheme():
		CM = ConfigManager()
		return CM.LoadConfig()['Theme']
		
class Desktop:
	def __init__(self,path:str):
		self.Dexec = None
		self.Dtitle = None
		self.Dicon = None
		self.file = path
		self.GetFields()

	def GetFields(self):
		parser = configparser.ConfigParser()
		parser.optionxform = str
		try:
			parser.read(self.file,encoding='utf-8')
		except Exception as e:
			NLLogger.Error(e, False)
		
		if not "Desktop Entry" in parser:
			NLLogger.Error("Desktop Entry not in desktop file", False)
		else:
			section = parser['Desktop Entry'] 
			self.Dexec = section.get('Exec','')
			self.Dtitle = section.get('Name','')
			self.Dicon = section.get('Icon','')
		

class UpdateChache:
	def __init__(self):
		self.CM = ConfigManager("/usr/share/icons/NikoruThemeStd/icons.chache")
		self.chache = {}
		self.theme = AppDesktopManager.GetTheme()
		self.Update()

	def Update(self):
		self.icons = self.Load()
		for icon in self.icons:
			if "/" in icon: 
				self.CreateLnOther(icon)
			else: 
				self.CreateLn(AppDesktopManager.LFind(icon,"c",self.theme))
		self.CM.SaveConfig(self.chache)
				  

	def CreateLnOther(self, path):
		os.symlink(path,f"/usr/share/icons/NikoruThemeStd/other/{os.path.basename(path)}")
		
	def CreateLn(self, icons):
		if not icons == None:
			for scale in icons:
				path = icons[scale]
				os.symlink(path,f"/usr/share/icons/NikoruThemeStd/{scale}/{os.path.basename(path)}")
	def Load(self):
		list = []
		with os.scandir('/usr/share/applications') as Afiles:
			for file in Afiles:
				Dfile = Desktop(file.path)
				list.append(Dfile.Dicon)
				if '/' in Dfile.Dicon: self.chache[file.name] = os.path.basename(Dfile.Dicon)
				else: self.chache[file.name] = Dfile.Dicon
		return list
			
			
class NikoruThemeManager:
	def __init__(self,configTheme: dict,production: bool):
		self.Logger = NLLogger(production,"ThemeManager")
		self.themeCfg = configTheme
		self.CM = ConfigManager('',production)
		if not self.themeCfg['user'] == '':
			self.Theme = self.themeCfg['user']
		else:
			self.Theme = self.themeCfg['system']
		self.LoadTheme(self.Theme)

	def LoadTheme(self,theme):
		try:
			print(self.themeCfg['user'])
			if not self.themeCfg['user'] == None:
				self.AllPaths = self.CM.OpenRestricted(f"/usr/share/NikoruDE/Other/Themes/{theme}/{theme}.ntc")
			else:
				self.AllPaths = self.CM.OpenRestricted(f"~/.local/share/nikoru/themes/{theme}/{theme}.ntc")
		except Exception as e:
			self.Logger.Error (e, True)

	def GTK_QT_Reload(self):
		subprocess.run([self.AllPaths["GTK"]],waitAnswer = True)
		subprocess.run([self.AllPaths["QT"]],waitAnswer = True)

	def ThemeLoad(self) -> dict:
		if not self.themeCfg['user'] == '':
			self.Theme = self.themeCfg['user']
		else:
			self.Theme = self.themeCfg['system']
		self.LoadTheme(self.Theme)
		theme = self.CM.OpenRestricted(self.AllPaths["SYS"])
		if not theme == None:
			return theme
		else:
			self.Logger.Error("Failed to load theme, Exiting.", True)
