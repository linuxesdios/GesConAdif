#!/usr/bin/env python3
"""
Versión optimizada de main_py.py específicamente para compilación EXE
OPTIMIZACIONES CRÍTICAS PARA PYINSTALLER:
- Pre-carga de módulos críticos al inicio
- Splash screen rápido para percepción de velocidad
- Threading mejorado para EXE
- Manejo optimizado de recursos incrustados
"""
import sys, os, time, logging
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# LOGGING OPTIMIZADO PARA EXE - RUTA INTELIGENTE
def configurar_logging():
    """Configura logging con ruta apropiada para EXE o desarrollo"""
    import sys
    
    if hasattr(sys, '_MEIPASS'):
        # Estamos en EXE - guardar en _internal
        log_path = os.path.join(os.path.dirname(sys.executable), '_internal', 'app.log')
        # Crear directorio _internal si no existe
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    else:
        # Desarrollo - guardar en raíz como siempre
        log_path = 'app.log'
    
    logging.basicConfig(
        level=logging.WARNING,  # Menos verbose para EXE
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )
    
    logging.info(f"Log configurado en: {log_path}")
    return log_path

# Configurar logging al inicio
log_path = configurar_logging()

# PRECARGAR CRÍTICO PARA EXE - EVITAR LAZY LOADING
import time
start_time = time.time()

from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QFont, QIcon

# PRE-IMPORTAR MÓDULOS CRÍTICOS PARA EXE
try:
    # Solo importar lo absolutamente crítico para el splash
    from modelos_py import Proyecto, DatosContrato, TipoContrato, Constantes
    from helpers_py import get_ui_file_path
    import datetime
    import json
    logging.info(f"Módulos críticos pre-cargados en {time.time() - start_time:.2f}s")
except Exception as e:
    logging.error(f"Error pre-cargando módulos: {e}")

# =================== SPLASH SCREEN OPTIMIZADO PARA EXE ===================

class PantallaCargaEXE(QSplashScreen):
    def __init__(self):
        # Intentar cargar el logo de ADIF
        pixmap = self._crear_splash_con_logo()
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Configurar icono del splash también
        self._configurar_icono_splash()
        
        # Configurar estilo profesional
        self.setStyleSheet("""
            QSplashScreen {
                border: 2px solid #0066CC;
                border-radius: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f0f0, stop: 1 #ffffff);
            }
        """)
    
    def _configurar_icono_splash(self):
        """Configura el icono del splash screen"""
        try:
            # Detectar ruta del icono según contexto
            if hasattr(sys, '_MEIPASS'):
                icono_path = os.path.join(sys._MEIPASS, 'images', 'icono.ico')
            else:
                icono_path = 'images/icono.ico'
            
            if os.path.exists(icono_path):
                self.setWindowIcon(QIcon(icono_path))
                
        except Exception as e:
            logging.debug(f"Error configurando icono splash: {e}")
    
    def _crear_splash_con_logo(self):
        """Crea el pixmap del splash con logo de ADIF"""
        try:
            import sys
            from PyQt5.QtGui import QPainter, QBrush, QLinearGradient
            from PyQt5.QtCore import QRect
            
            # Detectar ruta del logo según contexto
            if hasattr(sys, '_MEIPASS'):
                logo_path = os.path.join(sys._MEIPASS, 'images', 'adif.png')
            else:
                logo_path = 'images/adif.png'
            
            # Crear pixmap base
            width, height = 500, 300
            pixmap = QPixmap(width, height)
            
            # Verificar si existe el logo
            if os.path.exists(logo_path):
                # Cargar logo de ADIF
                logo = QPixmap(logo_path)
                if not logo.isNull():
                    # Crear splash con logo
                    return self._crear_splash_profesional_con_logo(width, height, logo)
            
            # Fallback: crear splash sin logo pero profesional
            return self._crear_splash_profesional_sin_logo(width, height)
            
        except Exception as e:
            logging.warning(f"Error creando splash con logo: {e}")
            return self._crear_splash_profesional_sin_logo(500, 300)
    
    def _crear_splash_profesional_con_logo(self, width, height, logo):
        """Crea splash profesional con logo ADIF"""
        from PyQt5.QtGui import QPainter, QBrush, QLinearGradient, QPen
        from PyQt5.QtCore import QRect
        
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(255, 255, 255))  # Fondo blanco
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo degradado elegante
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(240, 248, 255))  # Azul muy claro
        gradient.setColorAt(1, QColor(255, 255, 255))  # Blanco
        painter.fillRect(pixmap.rect(), QBrush(gradient))
        
        # Dibujar logo centrado en la parte superior
        logo_size = min(width // 2, height // 3)  # Tamaño proporcional
        logo_scaled = logo.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        logo_x = (width - logo_scaled.width()) // 2
        logo_y = height // 4 - logo_scaled.height() // 2
        painter.drawPixmap(logo_x, logo_y, logo_scaled)
        
        # Título principal
        painter.setPen(QColor(0, 102, 204))  # Azul ADIF
        font_title = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(font_title)
        
        title_rect = QRect(0, logo_y + logo_scaled.height() + 20, width, 30)
        painter.drawText(title_rect, Qt.AlignCenter, "Generador de Actas ADIF")
        
        # Subtítulo
        painter.setPen(QColor(100, 100, 100))
        font_subtitle = QFont("Segoe UI", 10)
        painter.setFont(font_subtitle)
        
        subtitle_rect = QRect(0, title_rect.y() + 35, width, 20)
        painter.drawText(subtitle_rect, Qt.AlignCenter, "Sistema de Gestión de Contratos")
        
        painter.end()
        logging.info("Splash screen con logo ADIF creado exitosamente")
        return pixmap
    
    def _crear_splash_profesional_sin_logo(self, width, height):
        """Crea splash profesional sin logo (fallback)"""
        from PyQt5.QtGui import QPainter, QBrush, QLinearGradient
        from PyQt5.QtCore import QRect
        
        pixmap = QPixmap(width, height)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo degradado
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(0, 102, 204))    # Azul ADIF
        gradient.setColorAt(1, QColor(0, 51, 102))     # Azul más oscuro
        painter.fillRect(pixmap.rect(), QBrush(gradient))
        
        # Título grande
        painter.setPen(QColor(255, 255, 255))
        font_title = QFont("Segoe UI", 18, QFont.Bold)
        painter.setFont(font_title)
        
        title_rect = QRect(0, height//2 - 40, width, 40)
        painter.drawText(title_rect, Qt.AlignCenter, "ADIF")
        
        # Subtítulo
        font_subtitle = QFont("Segoe UI", 12)
        painter.setFont(font_subtitle)
        subtitle_rect = QRect(0, height//2 + 10, width, 30)
        painter.drawText(subtitle_rect, Qt.AlignCenter, "Generador de Actas")
        
        painter.end()
        return pixmap
        
    def mostrar_mensaje(self, mensaje):
        # Mensaje en la parte inferior con estilo
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        self.showMessage(
            mensaje, 
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, 
            QColor(0, 102, 204)  # Azul ADIF
        )
        QApplication.processEvents()

# =================== CARGADOR ASÍNCRONO PARA EXE ===================

class CargadorControladores(QThread):
    """Carga controladores en segundo plano para EXE"""
    progreso = pyqtSignal(str)
    finalizado = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            self.progreso.emit("Cargando controlador principal...")
            time.sleep(0.1)  # Dar tiempo al splash
            
            from controladores.controlador_grafica import ControladorGrafica
            
            self.progreso.emit("Inicializando interfaz...")
            time.sleep(0.1)
            
            # Crear controlador en thread principal
            QTimer.singleShot(0, lambda: self.crear_controlador(ControladorGrafica))
            
        except Exception as e:
            self.error.emit(str(e))
    
    def crear_controlador(self, ControladorGrafica):
        try:
            main_window = ControladorGrafica(None)
            self.finalizado.emit(main_window)
        except Exception as e:
            self.error.emit(str(e))

# =================== CONFIGURACIÓN DE ICONO ===================

def configurar_icono_aplicacion(app):
    """Configura el icono de la aplicación para ventana y barra de tareas"""
    try:
        # Detectar ruta del icono según contexto (EXE vs desarrollo)
        if hasattr(sys, '_MEIPASS'):
            # Estamos en EXE - buscar en _internal
            icono_path = os.path.join(sys._MEIPASS, 'images', 'icono.ico')
        else:
            # Desarrollo - buscar en directorio actual
            icono_path = 'images/icono.ico'
        
        if os.path.exists(icono_path):
            icon = QIcon(icono_path)
            
            # Configurar icono para la aplicación (afecta a todas las ventanas)
            app.setWindowIcon(icon)
            
            # CONFIGURACIÓN ESPECÍFICA PARA BARRA DE TAREAS DE WINDOWS
            import platform
            if platform.system() == "Windows":
                try:
                    # Configurar AppUserModelID para Windows (barra de tareas)
                    import ctypes
                    from ctypes import wintypes
                    
                    # Establecer AppUserModelID único para la aplicación
                    app_id = "ADIF.GeneradorActas.Desktop.1.0"
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                    
                    # Forzar actualización del icono en la barra de tareas
                    logging.info("Configuración de barra de tareas Windows aplicada")
                    
                except Exception as e:
                    logging.warning(f"Error configurando barra de tareas Windows: {e}")
            
            logging.info(f"Icono configurado desde: {icono_path}")
            return icono_path
        else:
            logging.warning(f"Icono no encontrado en: {icono_path}")
            return None
            
    except Exception as e:
        logging.warning(f"Error configurando icono: {e}")
        return None

# =================== FUNCIÓN PRINCIPAL OPTIMIZADA PARA EXE ===================

def principal_exe():
    """Función principal optimizada específicamente para EXE"""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Generador de Actas ADIF")
    app.setApplicationVersion("1.0 EXE")
    
    # Configurar icono de la aplicación
    icono_path = configurar_icono_aplicacion(app)
    
    # Variables de control
    main_window = None
    splash = None
    cargador = None
    
    try:
        # 1. SPLASH INMEDIATO - CRÍTICO PARA PERCEPCIÓN EXE
        splash = PantallaCargaEXE()
        splash.show()
        splash.mostrar_mensaje("Iniciando...")
        
        # 2. PRE-VERIFICACIONES RÁPIDAS
        splash.mostrar_mensaje("Verificando entorno...")
        
        # Verificar archivos críticos para EXE
        archivos_criticos = [
            "_internal/BaseDatos.json" if hasattr(sys, '_MEIPASS') else "basedatos/BaseDatos.json",
            "_internal/ui" if hasattr(sys, '_MEIPASS') else "ui"
        ]
        
        for archivo in archivos_criticos:
            if hasattr(sys, '_MEIPASS'):
                ruta_completa = os.path.join(sys._MEIPASS, archivo.replace('_internal/', ''))
            else:
                ruta_completa = archivo
            
            if not os.path.exists(ruta_completa):
                splash.mostrar_mensaje(f"⚠️ Falta: {archivo}")
                time.sleep(1)
        
        # 3. CARGA ASÍNCRONA ESPECÍFICA PARA EXE
        splash.mostrar_mensaje("Cargando aplicación...")
        
        def on_progreso(mensaje):
            if splash:
                splash.mostrar_mensaje(mensaje)
        
        def on_finalizado(ventana):
            nonlocal main_window
            main_window = ventana
            if splash:
                splash.hide()
            if main_window:
                main_window.show()
        
        def on_error(error):
            if splash:
                splash.hide()
            QMessageBox.critical(None, "Error EXE", f"Error cargando aplicación:\n{error}")
            app.quit()
        
        # IMPORTAR DIRECTAMENTE PARA EXE (no threading que puede fallar)
        try:
            splash.mostrar_mensaje("Cargando controladores...")
            from controladores.controlador_grafica import ControladorGrafica
            
            splash.mostrar_mensaje("Inicializando interfaz...")
            main_window = ControladorGrafica(None)
            
            splash.mostrar_mensaje("Finalizando...")
            time.sleep(0.2)  # Breve pausa para mostrar mensaje
            
            splash.hide()
            main_window.show()
            
            logging.info(f"Aplicación EXE iniciada en {time.time() - start_time:.2f}s")
            
        except Exception as e:
            splash.hide()
            QMessageBox.critical(None, "Error EXE", f"Error inicializando:\n{e}")
            return 1
        
        return app.exec_()
        
    except Exception as e:
        if splash:
            splash.hide()
        QMessageBox.critical(None, "Error Crítico EXE", str(e))
        return 1
    
    finally:
        # Limpieza
        if cargador and cargador.isRunning():
            cargador.terminate()
            cargador.wait(1000)

# =================== FUNCIÓN PRINCIPAL ESTÁNDAR ===================

def principal():
    """Función principal estándar (no-EXE)"""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Generador de Actas ADIF")
    
    # Configurar icono de la aplicación
    icono_path = configurar_icono_aplicacion(app)
    
    try:
        # Splash más simple para desarrollo
        splash = PantallaCargaEXE()
        splash.show()
        splash.mostrar_mensaje("Iniciando modo desarrollo...")
        
        from controladores.controlador_grafica import ControladorGrafica
        
        main_window = ControladorGrafica(None)
        splash.hide()
        main_window.show()
        
        return app.exec_()
    except Exception as e:
        QMessageBox.critical(None, "Error", str(e))
        return 1

# =================== PUNTO DE ENTRADA ===================

if __name__ == "__main__":
    # Detectar si estamos en EXE compilado
    if hasattr(sys, '_MEIPASS'):
        # Estamos en EXE - usar versión optimizada
        sys.exit(principal_exe())
    else:
        # Desarrollo - usar versión estándar
        sys.exit(principal())