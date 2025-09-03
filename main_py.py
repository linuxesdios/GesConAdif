#!/usr/bin/env python3
import sys, os, time, logging
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

# PRECARGAR TODO PARA EXE - CRÍTICO PARA VELOCIDAD
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5 import uic
# PRECARGAR CONTROLADORES CRÍTICOS (simplified)
MODULES_LOADED = False

# =================== CLASE SPLASH SCREEN PERSONALIZADA ===================

class PantallaCarga(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(300, 150)
        pixmap.fill(QColor(250, 250, 250))
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        
    def mostrar_mensaje(self, mensaje):
        self.showMessage(mensaje, Qt.AlignmentFlag.AlignCenter, QColor(0, 0, 0))

def principal():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Generador de Actas ADIF")
    
    try:
        # Import when needed
        from controladores.controlador_grafica import ControladorGrafica
        
        main_window = ControladorGrafica(None)
        main_window.show()
        return app.exec_()
    except Exception as e:
        QMessageBox.critical(None, "Error", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(principal())