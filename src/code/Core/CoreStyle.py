import os
import subprocess 
import configparser
import shutil
from Utils.NLUtils import NLLogger,ConfigManager,ConColors
C_NIKORU_THEME_NAME = 'NikoruBase'
C_ICON_SIZES = ['32x32','16x16','64x64','48x48','128x128','scallable']
C_PRODUCTION = False
class ClientDesktopFileManager:
	def __init__(self):
		pass
		
	def GetClientDesktopInfo(self,initialClass:str,resolution:str):
		clientDesktopFile = ClientDesktopFileParser(f'/usr/share/applications/{initialClass}.desktop')
		if not '/' in clientDesktopFile.clientIcon:
			iconPath = self.Find(clientDesktopFile.clientIcon,resolution)
		elif not clientDesktopFile.clientIcon == None: 
			iconPath = clientDesktopFile.clientIcon
		else: 
			iconPath = self.Find(clientDesktopFile.clientIcon,resolution)

		return (iconPath, clientDesktopFile.clientExec,clientDesktopFile.clientTitle)
	
	def Find(self, name, scale):
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/scalable/{name}.svg"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/scalable/{name}.svg"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}/{name}.png"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}/{name}.png"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.png"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.png"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.svg"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.svg"
		
		return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/scalable/notFound.svg"
	
	
	@staticmethod
	def GetTheme():
		CM = ConfigManager()
		return CM.LoadConfig()['Theme']
		
class ClientDesktopFileParser:
	def __init__(self,path:str):
		self.clientExec = None
		self.clientTitle = None
		self.clientIcon = None
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
			self.clientExec = section.get('Exec','')
			self.clientTitle = section.get('Name','')
			self.clientIcon = section.get('Icon','')
		

class UpdateChache:
	def __init__(self):
		self.LOG = NLLogger(C_PRODUCTION,'DNF Update Nikoru icon chahe addon')
		self.LOG.Info('Started',ConColors.G,False)
		self.CM = ConfigManager(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/icons.chache")
		

	def loadChache(self):
		chache = self.CM.LoadConfig()
		return chache['list']
	
	def saveChache(self,chache):
		chache['list'] = chache
		self.CM.SaveConfig(chache)

	def getThemes(self) -> list:
		themes = []
		with os.scandir('/usr/share/icons') as AllIconThemes:
			for file in AllIconThemes:
				if (not file.name == C_NIKORU_THEME_NAME) and file.is_dir():
					themes.append(file.name)
		return themes
	
	def Update(self):
		newChache,customIcons = self.load()
		oldChache = self.loadChache()

		if not self.filesChanged(newChache+customIcons,oldChache):
			return
		for iconName in newChache:
			hicolor, other = self.legacyFind(iconName,C_ICON_SIZES,self.getThemes())
			if 'scallable' in hicolor:
				self.CreateStandartSymlink(hicolor['scallable'],'scallable')
			elif 'scallable' in other:
				self.CreateStandartSymlink(other['scallable'],'scallable')
			hicolor['scallable'] = None
			other['scallable'] = None
			for type in hicolor:
				self.CreateStandartSymlink(other[type],type)
				other[type] = None
			for type in other:
				self.CreateStandartSymlink(other[type],type)
		for iconPath in customIcons:
			self.CreateOtherSymlink(iconPath)

		self.CM.SaveConfig(self.saveChache(newChache+customIcons))
	
	def removeSymlinks(self,path):
		for scale in C_ICON_SIZES:
			path = f'/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}'
			shutil.rmtree(path)
			os.makedirs(path,mode=0o755)

		
	def filesChanged(list1:list,list2:list) -> bool:
		return not set(list1) == set(list2)

	def CreateOtherSymlink(self, path):
		os.symlink(path,f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{os.path.basename(path)}")
		
	def CreateStandartSymlink(self,path,scale):
		os.symlink(path,f"/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}/{os.path.basename(path)}")

	def load(self):
		iconNameList = []
		customPaths = []
		with os.scandir('/usr/share/applications') as AllDesktopfiles:
			for file in AllDesktopfiles:
				Desktopfile = ClientDesktopFileParser(file.path)
				if '/' in Desktopfile.clientIcon:
					customPaths.append(Desktopfile.clientIcon)
				else:
					iconNameList.append(Desktopfile.clientIcon)


		return iconNameList,customPaths
	
	def legacyFind(self,name, scales:list,themes:list):
		iconsOther = {}
		iconsHicolor = {}
		for theme in themes:
			if os.path.exists(f"/usr/share/icons/{theme}/scallable/{name}.svg"):
				iconsOther['scallable'] = f"/usr/share/icons/{theme}/scalable/{name}.svg"
			for scale in scales:
				if os.path.exists(f"/usr/share/icons/{theme}/{scale}/{name}.png"):
					iconsOther[scale] = f"/usr/share/icons/{theme}/{scale}/{name}.png"
		if os.path.exists(f"/usr/share/icons/hicolor/scallable/{name}.svg"):
				iconsHicolor['scallable'] = f"/usr/share/icons/hicolor/scallable/{name}.svg"
		for scale in scales:
			if os.path.exists(f"/usr/share/icons/hicolor/{scale}/{name}.png"):
				iconsHicolor[scale] = f"/usr/share/icons/hicolor/{scale}/{name}.png"
		
		return iconsHicolor, iconsOther
			
			
class NikoruThemeManager:
	def __init__(self,themeSettingsBlock: dict,production: bool):
		self.LOG = NLLogger(production,"ThemeManager")
		self.themeSettingsBlock = themeSettingsBlock
		self.CM = ConfigManager('',production)
		if not self.themeSettingsBlock['user'] == '':
			self.themeName = self.themeSettingsBlock['user']
		else:
			self.themeName = self.themeSettingsBlock['system']
		self.loadTheme(self.themeName)

	def loadTheme(self,themeName):
		try:
			if not self.themeSettingsBlock['user'] == None:
				self.AllPaths = self.CM.OpenRestricted(f"/usr/share/NikoruDE/Other/Themes/{themeName}/{themeName}.ntc")
			else:
				self.AllPaths = self.CM.OpenRestricted(f"~/.local/share/nikoru/themes/{themeName}/{themeName}.ntc")
		except Exception as e:
			self.LOG.Error (e, True)

	def GTK_QT_Reload(self):
		subprocess.run([self.AllPaths["GTK"]],waitAnswer = True)
		subprocess.run([self.AllPaths["QT"]],waitAnswer = True)

	def GetTheme(self) -> dict:
		self.loadTheme(self.themeName)
		theme = self.CM.OpenRestricted(self.AllPaths["DE"])
		if not theme == None:
			return theme
		else:
			###################################################### <- TO UPDATE
			self.LOG.Error("Failed to load theme, Exiting.", True)
			######################################################
