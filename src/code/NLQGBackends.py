# Copyright (C) 2024-2026 Niritech Labs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
from shiboken6 import getCppPointer
from NLUtils.Logger import NLLogger, ConColors
from PySide6.QtWidgets import QMainWindow
from NLUtils.QUBackend.LSI import NLLayerShellIntegration
import os
os.environ["QT_WAYLAND_SHELL_INTEGRATION"] = "layer-shell"
    

class WlrLayerShellBackend(QMainWindow):
    class Constants:
        AnchorNone = 0
        AnchorTop = 1
        AnchorBottom = 2
        AnchorLeft = 4
        AnchorRight = 8
    
        LayerBackground = 0
        LayerBottom = 1
        LayerTop = 2
        LayerOverlay = 3

        KeyboardInteractivityNone = 0
        KeyboardInteractivityExclusive = 1
        KeyboardInteractivityOnDemand = 2

    def __init__(self,production:bool,Anchor:int = Constants.AnchorBottom,Layer:int = Constants.LayerTop,KI:int = Constants.KeyboardInteractivityOnDemand,ExclusiveZone = None):
        super().__init__()
        self.Logger = NLLogger(production,'NL layer-shell-qt backend')
        self.Logger.Info('Started',ConColors.G,False)
        self.anchor = Anchor
        self.layer = Layer
        self.KI = KI
        self.EZ = ExclusiveZone
        
        try:
            from NLUtils.QUBackend.LSI import NLLayerShellIntegration
        except ImportError:
            self.Logger.Error('Backend is not installed',True)
        except Exception as E:
            self.Logger.Error(str(E),False)

    def Show(self):
        self.show()
        self.backendInit()

    def backendInit(self):
        QMWPtr = getCppPointer(self)[0]
        self.LSI = NLLayerShellIntegration(QMWPtr)
        self.LSI.SetAnchors(self.anchor)
        self.LSI.SetLayer(self.layer)
        self.LSI.SetKeyboardInteractivity(self.KI)
        if self.EZ:
            self.LSI.SetExclusiveZone(self.EZ)



