import os, sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess 
import configparser
import shutil
from NLUtils.Logger import NLLogger,ConColors
from NLUtils.JSONUtils import ConfigManager


C_NIKORU_THEME_NAME = 'NikoruBase'
C_ICON_SIZES = ['32x32','16x16','64x64','48x48','128x128','scalable','pixmap']
C_PRODUCTION = False
class ClientDesktopFileManager:
	def __init__(self):
		self.LOG = NLLogger(C_PRODUCTION,"CDFM")
		self.LOG.Info('Started',ConColors.G,False)
		
	def GetClientDesktopInfo(self,initialClass:str,resolution:str):
		clientDesktopFile = ClientDesktopFileParser(f'/usr/share/applications/{initialClass.lower()}.desktop',self.LOG)
		if not '/' in clientDesktopFile.clientIcon:
			iconPath = self.find(clientDesktopFile.clientIcon,resolution)
		elif not clientDesktopFile.clientIcon == None: 
			iconPath = f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{os.path.basename(clientDesktopFile.clientIcon)}"
		else: 
			iconPath = self.find(clientDesktopFile.clientIcon,resolution)

		return (iconPath, clientDesktopFile.clientExec,clientDesktopFile.clientTitle)
	
	def find(self, name, scale):
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/scalable/{name}.svg"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/scalable/{name}.svg"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}/{name}.png"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}/{name}.png"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.png"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.png"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.svg"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.svg"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.png"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{name}.png"
		
		if os.path.exists(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/pixmap/{name}.png"):
			return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/pixmap/{name}.png"
		
		return f"/usr/share/icons/{C_NIKORU_THEME_NAME}/standard/notFound.svg"
	
	
	@staticmethod
	def GetTheme():
		CM = ConfigManager()
		return CM.LoadConfig()['Theme']
		
class ClientDesktopFileParser:
	def __init__(self,path:str,Logger:NLLogger):
		self.clientExec = None
		self.clientTitle = None
		self.clientIcon = None
		self.file = path
		self.LOG = Logger
		self.getFields()

	def getFields(self):
		parser = configparser.ConfigParser(interpolation=None)
		parser.optionxform = str
		try:
			parser.read(self.file,encoding='utf-8')
		except Exception as e:
			self.LOG.Error(e, False)
		
		if not "Desktop Entry" in parser:
			self.LOG.Error("Desktop Entry not in desktop file", False)
		else:
			section = parser['Desktop Entry'] 
			self.clientExec = section.get('Exec','')
			self.clientTitle = section.get('Name','')
			self.clientIcon = section.get('Icon','')
			
		

class UpdateCache:
	def __init__(self):
		self.LOG = NLLogger(C_PRODUCTION,'DNF Update Nikoru icon chahe addon')
		self.LOG.Info('Started',ConColors.G,False)
		self.CM = ConfigManager(f"/usr/share/icons/{C_NIKORU_THEME_NAME}/icons.chache",False)
		

	def loadChache(self):
		cache = self.CM.LoadConfig()
		try:
			return cache['list']
		except KeyError:
			self.saveChache([])
			return []

	
	def saveChache(self,toCache):
		cache = {}
		cache['list'] = toCache
		self.CM.SaveConfig(cache)

	def getThemes(self) -> list:
		themes = []
		with os.scandir('/usr/share/icons') as AllIconThemes:
			for file in AllIconThemes:
				if (not file.name == C_NIKORU_THEME_NAME) and file.is_dir() and (not file.name == 'hicolor'):
					themes.append(file.name)
		return themes
	
	def Update(self):
		newCache,customIcons = self.load()
		oldCache = self.loadChache()
		

		if not self.filesChanged(newCache+customIcons,oldCache):
			return
		self.removeSymlinks()
		
		for iconName in newCache:
			hicolor, other = self.legacyFind(iconName,C_ICON_SIZES,self.getThemes())
			if 'scalable' in hicolor:
				self.createStandartSymlink(hicolor['scalable'],'scalable')
			elif 'scalable' in other:
				self.createStandartSymlink(other['scalable'],'scalable')
			if 'scalable' in hicolor: 
				del hicolor['scalable']
			if 'pixmap' in other:
				del other['pixmap'] 
			if 'scalable' in other: 
				del other['scalable'] 
			for iconType in hicolor:
				self.createStandartSymlink(hicolor[iconType],iconType)
				if iconType in other:
					del other[iconType] 
			for iconType in other:
				self.createStandartSymlink(other[iconType],iconType)
		for iconPath in customIcons:
			self.createOtherSymlink(iconPath)

		self.saveChache(newCache+customIcons)

	
	def removeSymlinks(self):
		try:
			for scale in C_ICON_SIZES:
				path = f'/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}'
				shutil.rmtree(path)
				os.makedirs(path,mode=0o755)
		except FileNotFoundError:
			os.makedirs(path,mode=0o755)
		except Exception as E:
			self.LOG.Error("Remove Symlinks: "+str(E),False)
		
	def filesChanged(self, list1:list,list2:list) -> bool:
		return not set(list1) == set(list2)

	def createOtherSymlink(self, path):
		try:
			os.symlink(path,f"/usr/share/icons/{C_NIKORU_THEME_NAME}/other/{os.path.basename(path)}")
		except Exception as E:
			self.LOG.Error("Create other Symlinks: "+str(E),False)
		
	def createStandartSymlink(self,path,scale):
		try:
			os.symlink(path,f"/usr/share/icons/{C_NIKORU_THEME_NAME}/{scale}/{os.path.basename(path)}")
		except FileExistsError:
			pass
		except Exception as E:
			self.LOG.Error("Create standard Symlinks: "+str(E),False)

	def load(self):
		iconNameList = []
		customPaths = []
		try:
			with os.scandir('/usr/share/applications') as AllDesktopfiles:
				for file in AllDesktopfiles:
					if (not os.path.isdir(file)) and '.desktop' in os.path.basename(file):
						Desktopfile = ClientDesktopFileParser(file.path,self.LOG)
						if '/' in Desktopfile.clientIcon:
							customPaths.append(Desktopfile.clientIcon)
						else:
							iconNameList.append(Desktopfile.clientIcon)
		except Exception as E:
			self.LOG.Error('Desktop Load: '+str(E),False)


		return iconNameList,customPaths
	
	def legacyFind(self,name, scales:list,themes:list):
		iconsOther = {}
		iconsHicolor = {}
		for theme in themes:
			if os.path.exists(f"/usr/share/icons/{theme}/scalable/apps/{name}.svg"):
				iconsOther['scalable'] = f"/usr/share/icons/{theme}/scalable/apps/{name}.svg"
			for scale in scales:
				if os.path.exists(f"/usr/share/icons/{theme}/{scale}/apps/{name}.png"):
					iconsOther[scale] = f"/usr/share/icons/{theme}/{scale}/apps/{name}.png"

		if os.path.exists(f"/usr/share/pixmaps/{name}.png"):
			iconsHicolor['pixmap'] = f"/usr/share/pixmaps/{name}.png"

		if os.path.exists(f"/usr/share/icons/hicolor/scalable/apps/{name}.svg"):
			iconsHicolor['scalable'] = f"/usr/share/icons/hicolor/scalable/apps/{name}.svg"

		

		for scale in scales:
			if os.path.exists(f"/usr/share/icons/hicolor/{scale}/apps/{name}.png"):
				iconsHicolor[scale] = f"/usr/share/icons/hicolor/{scale}/apps/{name}.png"
		
		return iconsHicolor, iconsOther
			
			
class NikoruThemeManager:
	def __init__(self,themeSettingsBlock: dict,production: bool):
		self.LOG = NLLogger(production,"ThemeManager")
		self.CM = ConfigManager('',production)

		self.themeSettingsBlock = themeSettingsBlock

		self.systemThemeName = self.themeSettingsBlock['system']
		if not self.themeSettingsBlock['user'] == '':
			self.currentThemeName = self.themeSettingsBlock['user']
		else:
			self.currentThemeName = self.themeSettingsBlock['system']
		self.loadTheme(self.currentThemeName)

	def loadTheme(self,themeName):
		try:
			if not self.themeSettingsBlock['user'] == None:
				return self.CM.OpenRestricted(f"/usr/share/Nikoru/Other/Themes/{themeName}/{themeName}.ntc")
			else:
				return self.CM.OpenRestricted(f"~/.local/share/nikoru/themes/{themeName}/{themeName}.ntc")
		except Exception as e:
			self.LOG.Error(e, True)
			return None

	def GTK_QT_Reload(self):
		subprocess.run([self.allPathsInNTC["GTK"]],waitAnswer = True)
		subprocess.run([self.allPathsInNTC["QT"]],waitAnswer = True)

	def GetTheme(self) -> dict:
		try:
			allPathsInNTC = self.loadTheme(self.currentThemeName)
			theme = self.CM.OpenRestricted(allPathsInNTC["DE"])
			self.LOG.Info(f'Loaded theme {self.currentThemeName}',ConColors.G,False)
		except Exception:
			self.LOG.Warning(f"Failed to load theme: {self.currentThemeName}, try to load another theme.")
			try:
				allPathsInNTC = self.loadTheme(self.systemThemeName)
				theme = self.CM.OpenRestricted(allPathsInNTC["DE"])
				self.LOG.Info(f'Loaded theme {self.systemThemeName}',ConColors.G,False)
			except Exception:
				theme = None

		if not theme == None:
			return theme
		else:
			self.LOG.Error("Failed to load themes, Exiting.", True)
			
if __name__ == "__main__":
	UC = UpdateCache()
	UC.Update()