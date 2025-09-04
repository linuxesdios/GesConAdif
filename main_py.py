#!/usr/bin/env python3
import sys, os, time, logging
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# LOGGING CON RUTA INTELIGENTE PARA EXE
def configurar_logging():
    """Configura logging con ruta apropiada para EXE o desarrollo"""
    if hasattr(sys, '_MEIPASS'):
        # Estamos en EXE - guardar en _internal
        log_path = os.path.join(os.path.dirname(sys.executable), '_internal', 'app.log')
        # Crear directorio _internal si no existe
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    else:
        # Desarrollo - guardar en raíz como siempre
        log_path = 'app.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )
    
    return log_path

# Configurar logging al inicio
log_path = configurar_logging()

# PRECARGAR TODO PARA EXE - CRÍTICO PARA VELOCIDAD
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5 import uic
# PRECARGAR CONTROLADORES CRÍTICOS (simplified)
MODULES_LOADED = False

# =================== CLASE SPLASH SCREEN PERSONALIZADA ===================

class PantallaCarga(QSplashScreen):
    def __init__(self):
        # Usar el mismo splash profesional que la versión optimizada
        pixmap = self._crear_splash_con_logo()
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Configurar icono del splash también
        self._configurar_icono_splash()
        
        # Configurar estilo profesional
        self.setStyleSheet("""
            QSplashScreen {
                border: 2px solid #0066CC;
                border-radius: 15px;
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
            import logging
            logging.debug(f"Error configurando icono splash: {e}")
    
    def _crear_splash_con_logo(self):
        """Crea el pixmap del splash con logo de ADIF"""
        try:
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
            import logging
            logging.warning(f"Error creando splash con logo: {e}")
            return self._crear_splash_profesional_sin_logo(500, 300)
    
    def _crear_splash_profesional_con_logo(self, width, height, logo):
        """Crea splash profesional con logo ADIF"""
        from PyQt5.QtGui import QPainter, QBrush, QLinearGradient, QFont
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
        return pixmap
    
    def _crear_splash_profesional_sin_logo(self, width, height):
        """Crea splash profesional sin logo (fallback)"""
        from PyQt5.QtGui import QPainter, QBrush, QLinearGradient, QFont
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
        from PyQt5.QtGui import QFont
        font = QFont("Segoe UI", 9)
        self.setFont(font)
        self.showMessage(
            mensaje, 
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, 
            QColor(0, 102, 204)  # Azul ADIF
        )
        QApplication.processEvents()

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
                    import logging
                    logging.info("Configuración de barra de tareas Windows aplicada")
                    
                except Exception as e:
                    import logging
                    logging.warning(f"Error configurando barra de tareas Windows: {e}")
            
            import logging
            logging.info(f"Icono configurado desde: {icono_path}")
            return icono_path
        else:
            import logging
            logging.warning(f"Icono no encontrado en: {icono_path}")
            return None
            
    except Exception as e:
        import logging
        logging.warning(f"Error configurando icono: {e}")
        return None

def principal():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Generador de Actas ADIF")
    
    # Configurar icono de la aplicación
    icono_path = configurar_icono_aplicacion(app)
    
    # SPLASH SCREEN PARA EXE - PERCEPCIÓN DE VELOCIDAD
    splash = PantallaCarga()
    splash.show()
    splash.mostrar_mensaje("Iniciando Generador de Actas ADIF...")
    app.processEvents()  # Forzar actualización UI
    
    try:
        # Detectar si estamos en EXE para optimizar mensajes
        es_exe = hasattr(sys, '_MEIPASS')
        
        if es_exe:
            # Mensajes optimizados para EXE
            splash.mostrar_mensaje("Cargando aplicación...")
            app.processEvents()
            time.sleep(0.3)  # Dar tiempo al usuario a ver el splash
            
            splash.mostrar_mensaje("Inicializando controladores...")
            app.processEvents()
        else:
            # Mensajes detallados para desarrollo
            splash.mostrar_mensaje("Importando módulos...")
            app.processEvents()
        
        # Import when needed
        from controladores.controlador_grafica import ControladorGrafica
        
        if es_exe:
            splash.mostrar_mensaje("Configurando interfaz...")
        else:
            splash.mostrar_mensaje("Inicializando aplicación...")
        app.processEvents()
        
        # Crear ventana principal
        main_window = ControladorGrafica(None)
        
        if es_exe:
            splash.mostrar_mensaje("¡Listo!")
            app.processEvents()
            time.sleep(0.2)  # Pausa breve para EXE
        else:
            splash.mostrar_mensaje("Preparando interfaz...")
            app.processEvents()
        
        # Mostrar ventana y ocultar splash
        main_window.show()
        
        # En EXE: transición más rápida
        delay = 300 if es_exe else 500
        QTimer.singleShot(delay, splash.hide)
        
        return app.exec_()
    except Exception as e:
        splash.hide()
        QMessageBox.critical(None, "Error", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(principal())