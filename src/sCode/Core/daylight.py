from NLUtils import ConfigManager

cm = ConfigManager("~/Desktop/NiraLinux-project/NikoruDE/main/src/sOther/Themes/Daylight/Daylight.qss")
dock = {}
dock["ClientArea"] = """
                QWidget {
                    background: #dcdfe8;
                    border: 0px solid #505050;
                    border-radius: 4px;
                }
            """
dock["Clients"] = """
                    QPushButton {
                        background: #dcdfe8;
                        border: 0px solid #505050;
                        border-radius: 4px;
                    }
                    QPushButton:hover { 
                        background: #c9cdd4;
                    }
                    QMenu  {
                        color: #ffffff;
                        background: #404040;
                    }
                    QMenu:hover  {
                        color: #000000;
                    }
                           """
dock["Overview"] = """
            QPushButton {
                background: #dcdfe8;
                border: 0px solid #505050;
                border-radius: 4px;
                color: black;
                font-size: 12px;
            }
            QPushButton:hover { 
                background: #c9cdd4;
            } 
            QMainWindow {
                background: #dcdfe8;
            } 
        """
dock["IconPath"] = '/usr/share/NikoruDE/Other/Themes/Daylight/Nikoru/Dock'

system = {}
system['DockPanel'] = dock
cm.SaveConfig(system)