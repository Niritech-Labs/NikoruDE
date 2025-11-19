# Copyright (C) 2024-2025 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Core.NLUtils import ConfigManager

cm = ConfigManager("~/NiraLinux-project/NikoruDE/main/src/sOther/Themes/Daylight/Daylight.qss",True)
dock = {}
dock["main"] = """
                #DockRootWidget {
                    background: #dcdfe8;
                    border: 0px solid #505050;
                    border-radius: 4px;
                }

                    #DockClients {
                        background: #dcdfe8;
                        border: 0px solid #505050;
                        border-radius: 4px;
                    }
                    #DockClients:hover { 
                        background: #c9cdd4;
                    }
                    QMenu  {
                        color: #ffffff;
                        background: #404040;
                    }
                    QMenu:hover  {
                        color: #000000;
                    }
            #DockButtons {
                background: #dcdfe8;
                border: 0px solid #505050;
                border-radius: 4px;
                color: black;
                font-size: 12px;
            }
            #DockButtons:hover { 
                background: #c9cdd4;
            } 
            #DockBase {
                background: #dcdfe8;
            } 
        """
dock["IconPath"] = '/usr/share/NikoruDE/Other/Themes/Daylight/Nikoru/Dock'

cm.SaveConfig(dock)