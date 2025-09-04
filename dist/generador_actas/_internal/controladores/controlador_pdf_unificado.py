#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
controlador_pdf_unificado.py - Controlador PDF unificado y optimizado
- Combina funcionalidades de controlador_pdf.py y controlador_pdf_optimized.py
- Carga lazy de PyMuPDF para inicio rápido sin librerías pesadas
- Visualización de PDF con controles de navegación y zoom
- Integración completa con el sistema de contratos
"""

import logging
import os
import platform
import subprocess
import threading

logger = logging.getLogger(__name__)
from datetime import datetime
from typing import Optional

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QPushButton, QLabel,
    QSlider, QSpinBox, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout,
    QDialog
)

# ===== VARIABLES GLOBALES PARA LAZY LOADING =====
_fitz_module = None
_fitz_loading = False
_fitz_load_error = None

def _load_fitz_lazy():
    """Cargar PyMuPDF de forma lazy en segundo plano"""
    global _fitz_module, _fitz_loading, _fitz_load_error
    
    if _fitz_module is not None:
        return _fitz_module
    
    if _fitz_loading:
        return None
    
    _fitz_loading = True
    
    try:
        import fitz  # PyMuPDF
        _fitz_module = fitz
        _fitz_load_error = None

        return _fitz_module
    except ImportError as e:
        _fitz_load_error = f"PyMuPDF no disponible: {e}"
        _fitz_module = None
        logger.error(f"[PDF] ❌ {_fitz_load_error}")
        return None
    except Exception as e:
        _fitz_load_error = f"Error cargando PyMuPDF: {e}"
        _fitz_module = None
        logger.error(f"[PDF] ❌ {_fitz_load_error}")
        return None
    finally:
        _fitz_loading = False

def _load_fitz_async(callback=None):
    """Cargar PyMuPDF de forma asíncrona"""
    def load_thread():
        fitz = _load_fitz_lazy()
        if callback:
            callback(fitz is not None, _fitz_load_error)
    
    threading.Thread(target=load_thread, daemon=True).start()

class PDFScrollArea(QScrollArea):
    """QScrollArea personalizado para manejar rueda del ratón para cambio de páginas."""
    
    def __init__(self, pdf_controller, parent=None):
        super().__init__(parent)
        self.pdf_controller = pdf_controller
        
    def wheelEvent(self, event):
        # Si hay PDF cargado, cambiar páginas directamente con la rueda
        if self.pdf_controller and self.pdf_controller.has_pdf_loaded():
            if event.angleDelta().y() > 0:
                # Rueda hacia arriba - página anterior
                self.pdf_controller.prev_page()
            else:
                # Rueda hacia abajo - página siguiente
                self.pdf_controller.next_page()
            return
        
        # Si no hay PDF, comportamiento normal de scroll
        super().wheelEvent(event)

class _PDFControllerOptimized(QObject):
    """Controlador PDF optimizado con carga lazy de PyMuPDF"""
    
    pdf_changed = pyqtSignal(str)

    def __init__(self, main_window: QObject):
        super().__init__(main_window)
        self._mw = main_window
        self.pdf_document = None
        self.current_pdf_path: Optional[str] = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self._contract_name = ""
        self._pdf_pendiente = ""
        self.pdf_label_left = None
        self.pdf_label_right = None
        
        # Estado de carga de PyMuPDF
        self._fitz_ready = False
        self._fitz_loading = False
        
        # ===== INICIALIZACIÓN RÁPIDA SIN PYMUPDF =====
        self._init_ui_widgets()
        self._connect_basic_signals()
        self._show_loading_message()
        
        # Programar carga lazy de PyMuPDF para después
        QTimer.singleShot(2000, self._start_lazy_fitz_loading)
        


    def _init_ui_widgets(self):
        """Inicializar widgets de UI (rápido)"""
        try:
            # Widgets existentes en el .ui (pestaña PDF)
            self.btn_prev: QPushButton = self._mw.findChild(QPushButton, "btn_prev")
            self.page_info: QLabel = self._mw.findChild(QLabel, "page_info")
            self.page_spinbox: QSpinBox = self._mw.findChild(QSpinBox, "page_spinbox")
            self.zoom_slider: QSlider = self._mw.findChild(QSlider, "zoom_slider")
            self.zoom_label: QLabel = self._mw.findChild(QLabel, "zoom_label")
            self.btn_fit: QPushButton = self._mw.findChild(QPushButton, "btn_fit")
            self.btn_select_pdf: QPushButton = self._mw.findChild(QPushButton, "btn_select_pdf")
            self.btn_open_external: QPushButton = self._mw.findChild(QPushButton, "btn_open_external")
            self.btn_clear_pdf: QPushButton = self._mw.findChild(QPushButton, "btn_clear_pdf")
            self.scroll_area: QScrollArea = self._mw.findChild(QScrollArea, "scroll_area")
            self.pdf_label: QLabel = self._mw.findChild(QLabel, "pdf_label")
            
            # Reemplazar scroll_area con versión personalizada
            self._setup_custom_scroll_area()
            
        except Exception as e:
            logger.error(f"[PDF] ❌ Error inicializando widgets: {e}")

    
    def _connect_basic_signals(self):
        """Conectar señales básicas (sin PyMuPDF)"""
        try:
            # Botones básicos
            if self.btn_select_pdf:
                self.btn_select_pdf.clicked.connect(self.select_pdf_file)
            if self.btn_open_external:
                self.btn_open_external.clicked.connect(self.open_external)
            if self.btn_clear_pdf:
                self.btn_clear_pdf.clicked.connect(self.clear_pdf)
            
            # Configurar controles básicos
            if self.zoom_slider:
                self.zoom_slider.setMinimum(25)
                self.zoom_slider.setMaximum(300)
                self.zoom_slider.setValue(100)
                self.zoom_slider.valueChanged.connect(self.change_zoom)
            
            # Los controles de navegación se conectarán cuando PyMuPDF esté listo
            self._update_controls()
            
        except Exception as e:
            logger.error(f"[PDF] ❌ Error conectando señales: {e}")

    def _show_loading_message(self):
        """Mostrar mensaje de carga mientras se carga PyMuPDF"""
        if self.pdf_label:
            self.pdf_label.setText(
                "<div style='padding: 40px; text-align: center; color: #666;'>"
                "<div style='font-size: 36px; margin-bottom: 10px;'>⚡</div>"
                "<h3>Visor PDF (Cargando...)</h3>"
                "<p>Inicializando motor PDF en segundo plano...</p>"
                "<p style='font-size: 11px; color: #999;'>PyMuPDF se carga automáticamente</p>"
                "</div>"
            )
            self.pdf_label.setAlignment(Qt.AlignCenter)

    def _start_lazy_fitz_loading(self):
        """Iniciar carga lazy de PyMuPDF"""
        if self._fitz_loading or self._fitz_ready:
            return
        
        self._fitz_loading = True

        
        def on_fitz_loaded(success: bool, error: str):
            self._fitz_loading = False
            self._fitz_ready = success
            
            if success:
                self._on_fitz_ready()
            else:
                self._on_fitz_failed(error)
        
        _load_fitz_async(on_fitz_loaded)

    def _on_fitz_ready(self):
        """Callback cuando PyMuPDF está listo"""

        
        # Conectar controles de navegación ahora que PyMuPDF está listo
        if self.btn_prev:
            self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next: QPushButton = self._mw.findChild(QPushButton, "btn_next")
        if self.btn_next:
            self.btn_next.clicked.connect(self.next_page)
        if self.btn_fit:
            self.btn_fit.clicked.connect(self.fit_to_window)
        if self.page_spinbox:
            self.page_spinbox.valueChanged.connect(self.goto_page)
        
        # Actualizar mensaje
        self._show_ready_message()
        
        # Cargar PDF pendiente si existe
        if self._pdf_pendiente and os.path.exists(self._pdf_pendiente):
            self.load_pdf(self._pdf_pendiente)
            self._pdf_pendiente = ""

    def _on_fitz_failed(self, error: str):
        """Callback cuando falla la carga de PyMuPDF"""
        logger.error(f"[PDF] ❌ PyMuPDF no disponible: {error}")
        
        if self.pdf_label:
            self.pdf_label.setText(
                "<div style='padding: 40px; text-align: center; color: #d32f2f;'>"
                "<div style='font-size: 36px; margin-bottom: 10px;'>⚠️</div>"
                "<h3>Visor PDF - Funcionalidad Limitada</h3>"
                "<p>PyMuPDF no está disponible</p>"
                "<p style='font-size: 11px; color: #999;'>Solo funciones básicas disponibles</p>"
                "<p style='font-size: 10px; color: #666;'>Instale PyMuPDF para funcionalidad completa</p>"
                "</div>"
            )

    def _show_ready_message(self):
        """Mostrar mensaje cuando el visor está listo"""
        if self.pdf_label:
            self.pdf_label.setText(
                "<div style='padding: 40px; text-align: center; color: #666;'>"
                "<div style='font-size: 36px; margin-bottom: 10px;'>📄</div>"
                "<h3>Visor PDF</h3>"
                "<p>Seleccione un archivo PDF para visualizar</p>"
                "<p style='font-size: 11px; color: #27ae60;'>✅ PyMuPDF listo</p>"
                "</div>"
            )
            self.pdf_label.setAlignment(Qt.AlignCenter)

    # ===== API ESPERADA (compatible con original) =====
    
    def set_contract_name(self, name: str):
        """Establecer nombre de contrato"""
        old_name = self._contract_name
        self._contract_name = name or ""

        
        if old_name and old_name != self._contract_name:

            if self.pdf_document:
                self.pdf_document = None
                self.current_pdf_path = None
                self.total_pages = 0
                self.current_page = 0
                if self._fitz_ready:
                    self._show_ready_message()
                else:
                    self._show_loading_message()
                self._update_controls()
        
        if self._contract_name:
            self._load_pdf_from_contract()

    def on_tab_activated(self):
        """Callback cuando se activa la pestaña PDF"""

        
        # Si PyMuPDF no está listo pero no se está cargando, iniciarlo
        if not self._fitz_ready and not self._fitz_loading:
            self._start_lazy_fitz_loading()
        
        if self._pdf_pendiente and os.path.exists(self._pdf_pendiente):
            if self._fitz_ready:
                self.load_pdf(self._pdf_pendiente)
                self._pdf_pendiente = ""
        else:
            if self._contract_name:
                self._load_pdf_from_contract()

    def get_current_pdf_path(self) -> str:
        """Obtener ruta del PDF actual"""
        return self.current_pdf_path or ""

    def has_pdf_loaded(self) -> bool:
        """Verificar si hay PDF cargado"""
        return bool(self.pdf_document) and self.total_pages > 0

    # ===== FUNCIONES PDF (requieren PyMuPDF) =====
    
    def load_pdf(self, path: str) -> bool:
        """Cargar PDF - versión optimizada"""
        if not self._fitz_ready:
            if not _fitz_module:
                # PyMuPDF no está listo, guardar como pendiente
                self._pdf_pendiente = path
                if self.pdf_label:
                    self.pdf_label.setText(
                        "<div style='padding: 40px; text-align: center; color: #f39c12;'>"
                        "<div style='font-size: 36px; margin-bottom: 10px;'>⏳</div>"
                        "<h3>Cargando PDF...</h3>"
                        f"<p>Preparando: {os.path.basename(path)}</p>"
                        "<p style='font-size: 11px; color: #999;'>Esperando a PyMuPDF...</p>"
                        "</div>"
                    )
                return False
            else:
                # PyMuPDF disponible pero no inicializado
                fitz = _fitz_module
        else:
            fitz = _fitz_module

        if not fitz:
            QMessageBox.warning(
                self._mw, "PyMuPDF no disponible",
                f"No se puede abrir PDF. PyMuPDF no está disponible.\n\n"
                f"Error: {_fitz_load_error or 'Módulo no encontrado'}\n\n"
                f"Instale PyMuPDF para ver PDFs:\n"
                f"pip install PyMuPDF"
            )
            return False

        try:
            self.pdf_document = fitz.open(path)
            self.current_pdf_path = path
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            
            if self.page_spinbox:
                self.page_spinbox.setMinimum(1)
                self.page_spinbox.setMaximum(self.total_pages)
                self.page_spinbox.setValue(1)
            
            self.render_page()
            self._update_controls()
            self.pdf_changed.emit(path)
            
            if path != self._pdf_pendiente:
                self._save_pdf_to_json(path)
            

            return True
            
        except Exception as e:
            QMessageBox.warning(self._mw, "Error", f"Error cargando PDF:\n{e}")
            print(f"[PDF] ❌ Error cargando PDF: {e}")
            return False

    
    
    # ===== RESTO DE MÉTODOS (igual que el original) =====
    
    def select_pdf_file(self):
        """Seleccionar archivo PDF y copiarlo automáticamente a la carpeta 01-proyecto"""
        import shutil
        
        # Determinar directorio inicial
        initial_dir = ""
        if self._contract_name:
            project_folder = self.get_project_folder_path()
            if project_folder and os.path.exists(project_folder):
                initial_dir = project_folder
            else:
                initial_dir = os.getcwd()
        else:
            initial_dir = os.getcwd()
        
        # Seleccionar archivo PDF
        path, _ = QFileDialog.getOpenFileName(
            self._mw, "Seleccionar archivo PDF", initial_dir, 
            "Archivos PDF (*.pdf);;Todos los archivos (*)"
        )
        if not path:
            return
        if not os.path.exists(path):
            QMessageBox.warning(self._mw, "Error", "El archivo no existe")
            return
        
        # Si hay contrato seleccionado, copiar PDF a carpeta 01-proyecto
        if self._contract_name:
            target_folder = self.get_project_folder_path()
            if target_folder and os.path.exists(target_folder):
                try:
                    # Obtener nombre del archivo
                    filename = os.path.basename(path)
                    target_path = os.path.join(target_folder, filename)
                    
                    # Si el archivo no está ya en la carpeta del proyecto, copiarlo
                    if os.path.abspath(path) != os.path.abspath(target_path):
                        # Crear nombre único si ya existe
                        if os.path.exists(target_path):
                            name, ext = os.path.splitext(filename)
                            counter = 1
                            while os.path.exists(target_path):
                                new_filename = f"{name}_{counter}{ext}"
                                target_path = os.path.join(target_folder, new_filename)
                                counter += 1
                        
                        # Copiar archivo
                        shutil.copy2(path, target_path)

                        
                        # Usar la ruta del archivo copiado
                        path = target_path
                    else:
                        pass
                except Exception as e:
                    print(f"[PDF] ❌ Error copiando PDF a carpeta del proyecto: {e}")
                    # Continuar con la ruta original si falla la copia
            else:
                pass
        self.load_pdf(path)

    def _setup_custom_scroll_area(self):
        """Configurar scroll area para vista dual"""
        try:
            if self.scroll_area:
                parent = self.scroll_area.parent()
                geometry = self.scroll_area.geometry()
                
                custom_scroll = PDFScrollArea(self, parent)
                custom_scroll.setGeometry(geometry)
                custom_scroll.setWidgetResizable(True)
                custom_scroll.setObjectName("scroll_area")
                
                # Crear contenedor horizontal para dos páginas
                self.dual_container = QWidget()
                layout = QHBoxLayout(self.dual_container)
                layout.setSpacing(10)
                
                # Crear dos labels
                self.pdf_label_left = QLabel()
                self.pdf_label_right = QLabel()
                self.pdf_label_left.setAlignment(Qt.AlignCenter)
                self.pdf_label_right.setAlignment(Qt.AlignCenter)
                
                layout.addWidget(self.pdf_label_left)
                layout.addWidget(self.pdf_label_right)
                
                custom_scroll.setWidget(self.dual_container)
                
                # Mantener compatibilidad
                self.pdf_label = self.pdf_label_left
                
                self.scroll_area.hide()
                self.scroll_area = custom_scroll
                custom_scroll.show()
                
        except Exception as e:
            print(f"[PDF] ❌ Error configurando scroll area: {e}")

    def render_page(self):
        """Renderizar página(s) - con soporte dual"""
        if not self.has_pdf_loaded() or not self.pdf_label or not _fitz_module:
            return
        
        try:
            # Página izquierda (actual)
            page = self.pdf_document[self.current_page]
            mat = _fitz_module.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            qpix = QPixmap.fromImage(image)
            
            self.pdf_label_left.setPixmap(qpix)
            self.pdf_label_left.setScaledContents(False)
            self.pdf_label_left.resize(qpix.size())
            
            # Página derecha (si existe)
            if (self.current_page + 1) < self.total_pages:
                page_right = self.pdf_document[self.current_page + 1]
                pix_right = page_right.get_pixmap(matrix=mat)
                image_right = QImage(pix_right.samples, pix_right.width, pix_right.height, pix_right.stride, fmt)
                qpix_right = QPixmap.fromImage(image_right)
                
                self.pdf_label_right.setPixmap(qpix_right)
                self.pdf_label_right.setScaledContents(False)
                self.pdf_label_right.resize(qpix_right.size())
            else:
                self.pdf_label_right.clear()
                self.pdf_label_right.setText("Fin del documento")
                
        except Exception as e:
            print(f"[PDF] ❌ Error renderizando: {e}")

    def next_page(self):
        """Página siguiente - saltar 2 páginas"""
        if self.has_pdf_loaded() and (self.current_page + 2) < self.total_pages:
            self.current_page += 2
            self.render_page()
            self._update_controls()

    def prev_page(self):
        """Página anterior - retroceder 2 páginas"""
        if self.has_pdf_loaded() and self.current_page >= 2:
            self.current_page -= 2
            self.render_page()
            self._update_controls()

    def _update_controls(self):
        """Actualizar controles para vista dual"""
        has_pdf = self.has_pdf_loaded()
        if self.btn_prev:
            self.btn_prev.setEnabled(has_pdf and self.current_page >= 2)
        if hasattr(self, 'btn_next') and self.btn_next:
            self.btn_next.setEnabled(has_pdf and (self.current_page + 2) < self.total_pages)
        if self.page_spinbox:
            self.page_spinbox.setEnabled(has_pdf)
            if has_pdf:
                self.page_spinbox.blockSignals(True)
                self.page_spinbox.setValue(self.current_page + 1)
                self.page_spinbox.blockSignals(False)
        if self.page_info:
            if has_pdf and (self.current_page + 1) < self.total_pages:
                end_page = min(self.current_page + 2, self.total_pages)
                self.page_info.setText(f"Páginas {self.current_page + 1}-{end_page} de {self.total_pages}")
            elif has_pdf:
                self.page_info.setText(f"Página {self.current_page + 1} de {self.total_pages}")
            else:
                self.page_info.setText("Página 0 de 0")
        if self.zoom_label:
            self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")

    
    def goto_page(self, page_number: int):
        """Ir a página específica"""
        if self.has_pdf_loaded():
            target_page = page_number - 1
            if 0 <= target_page < self.total_pages:
                self.current_page = target_page
                self.render_page()
                self._update_controls()

    def change_zoom(self, value: int):
        """Cambiar zoom"""
        self.zoom_level = max(0.25, min(3.0, value / 100.0))
        self.render_page()
        self._update_controls()

    def fit_to_window(self):
        """Ajustar a ventana"""
        if not self.has_pdf_loaded() or not self.scroll_area or not _fitz_module:
            return
        try:
            page = self.pdf_document[self.current_page]
            pix = page.get_pixmap(matrix=_fitz_module.Matrix(1, 1))
            if not pix:
                return
                
            viewport_size = self.scroll_area.viewport().size()
            area_width = viewport_size.width() - 20
            area_height = viewport_size.height() - 20
            
            if pix.width and pix.height:
                zoom_width = area_width / pix.width
                zoom_height = area_height / pix.height
                
                self.zoom_level = max(0.25, min(3.0, min(zoom_width, zoom_height)))
                
                if self.zoom_slider:
                    self.zoom_slider.blockSignals(True)
                    self.zoom_slider.setValue(int(self.zoom_level * 100))
                    self.zoom_slider.blockSignals(False)
                self.render_page()
                self._update_controls()
        except Exception:
            pass

    def open_external(self):
        """Abrir en aplicación externa"""
        if not self.current_pdf_path:
            QMessageBox.information(self._mw, "Información", "No hay PDF cargado")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(self.current_pdf_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.current_pdf_path])
            else:
                subprocess.Popen(["xdg-open", self.current_pdf_path])
        except Exception as e:
            QMessageBox.warning(self._mw, "Error", f"No se pudo abrir externamente:\n{e}")

    def clear_pdf(self):
        """Limpiar PDF"""
        self.pdf_document = None
        self.current_pdf_path = None
        self.total_pages = 0
        self.current_page = 0
        self._pdf_pendiente = ""
        
        if self._fitz_ready:
            self._show_ready_message()
        else:
            self._show_loading_message()
            
        self._update_controls()
        
        if self._contract_name:
            self._save_pdf_to_json("")

    def _load_pdf_from_contract(self):
        """Cargar PDF desde contrato y configurar fecha de inicio automáticamente"""

        
        if not self._contract_name:

            return
            
        try:
            # Obtener datos del contrato desde JSON

            if not hasattr(self._mw, 'controlador_json') or not self._mw.controlador_json:
                print("[PDF] ❌ Controlador JSON no disponible")
                return
                

            datos_contrato = self._mw.controlador_json.leer_contrato_completo(self._contract_name)
            if not datos_contrato:
                print(f"[PDF] ❌ No se encontraron datos para el contrato: {self._contract_name}")
                return
            

            
            # Buscar PDF en los datos del contrato
            pdf_path = None
            
            # Buscar en diferentes campos donde puede estar guardado el PDF
            campos_pdf = ['pdf_path', 'ubicacion_proyecto', 'rutaPdf', 'proyecto_pdf']
            

            for campo in campos_pdf:
                if campo in datos_contrato and datos_contrato[campo]:
                    pdf_path = datos_contrato[campo]

                    break
                else:
                    valor = datos_contrato.get(campo, 'NO_EXISTE')

            
            if not pdf_path:
                print(f"[PDF] ❌ No hay PDF guardado para el contrato: {self._contract_name}")
                return
            
            # Verificar que el archivo existe - manejar rutas relativas

            
            # Si es una ruta relativa, convertir a absoluta
            if not os.path.isabs(pdf_path):
                pdf_path_absoluta = os.path.join(os.getcwd(), pdf_path)

                pdf_path = pdf_path_absoluta
            
            if not os.path.exists(pdf_path):
                print(f"[PDF] ❌ El archivo PDF no existe: {pdf_path}")
                return
            

            
            # Cargar el PDF
            if self.load_pdf(pdf_path):

                
                # 🆕 NUEVO: Configurar fecha de inicio automáticamente
                self._configurar_fecha_inicio_automatica(pdf_path)
                
            else:
                print(f"[PDF] ❌ Error cargando PDF desde contrato")
                
        except Exception as e:
            print(f"[PDF] ❌ Error cargando PDF desde contrato: {e}")
            import traceback
            traceback.print_exc()
    
    def _configurar_fecha_inicio_automatica(self, pdf_path: str):
        """Configurar fecha de inicio basada en la fecha de creación del PDF"""
        try:
            if not os.path.exists(pdf_path):
                return
                
            # Obtener fecha de creación del archivo PDF
            timestamp_creacion = os.path.getctime(pdf_path)
            fecha_creacion = datetime.fromtimestamp(timestamp_creacion)
            

            
            # Buscar campo de fecha de inicio en la interfaz
            campos_fecha = ['fechaContrato', 'fechaInicio', 'fecha_inicio', 'dateEdit']
            
            for nombre_campo in campos_fecha:
                try:
                    widget_fecha = getattr(self._mw, nombre_campo, None)
                    if widget_fecha and hasattr(widget_fecha, 'setDate'):
                        # Convertir datetime a QDate
                        from PyQt5.QtCore import QDate
                        q_date = QDate(fecha_creacion.year, fecha_creacion.month, fecha_creacion.day)
                        
                        # Establecer la fecha
                        widget_fecha.blockSignals(True)
                        widget_fecha.setDate(q_date)
                        widget_fecha.blockSignals(False)
                        

                        
                        # Guardar la fecha en JSON
                        self._guardar_fecha_en_json(nombre_campo, fecha_creacion.strftime('%Y-%m-%d'))
                        break
                        
                except Exception as widget_error:

                    continue
                    
        except Exception as e:
            print(f"[PDF] ❌ Error configurando fecha automática: {e}")
    
    def _guardar_fecha_en_json(self, nombre_campo: str, fecha_str: str):
        """Guardar fecha automática en JSON"""
        try:
            if not self._contract_name:
                return
                
            if hasattr(self._mw, 'controlador_json') and self._mw.controlador_json:
                datos_fecha = {nombre_campo: fecha_str}
                self._mw.controlador_json.guardar_contrato_completo(self._contract_name, datos_fecha)

                
        except Exception as e:
            print(f"[PDF] ❌ Error guardando fecha en JSON: {e}")

    def _save_pdf_to_json(self, pdf_path: str):
        """Guardar PDF en JSON y marcar fase de Creación Proyecto como generada"""
        if not self._contract_name:

            return
        
        try:


            
            # Guardar información del PDF en el JSON del contrato usando el controlador JSON
            if hasattr(self._mw, 'controlador_json') and self._mw.controlador_json:
                # Calcular ruta relativa desde el directorio de trabajo actual
                try:
                    pdf_path_relativa = os.path.relpath(pdf_path, os.getcwd())

                except Exception:
                    pdf_path_relativa = pdf_path

                
                # Guardar datos del PDF usando siempre la ruta relativa como principal
                pdf_data = {
                    'pdf_path': pdf_path_relativa,  # Usar ruta relativa como principal
                    'pdf_filename': os.path.basename(pdf_path),
                    'pdf_saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ubicacion_proyecto': pdf_path_relativa,  # Usar ruta relativa
                    'pdf_path_relativa': pdf_path_relativa,   # Mantener compatibilidad
                    'pdf_path_absoluta': pdf_path  # Guardar también la absoluta como respaldo
                }
                
                # Actualizar el contrato con los datos del PDF
                self._mw.controlador_json.guardar_contrato_completo(self._contract_name, pdf_data)

            
            # 🆕 MARCAR FASE DE CREACIÓN PROYECTO COMO GENERADA
            self._marcar_fase_creacion_proyecto()
            
            # 🆕 REGISTRAR FECHA EN fases_documentos.creacion.generado
            self._registrar_fecha_creacion_en_fases(pdf_path)
            
        except Exception as e:
            print(f"[PDF] ❌ Error guardando PDF en JSON: {e}")
    
    def _marcar_fase_creacion_proyecto(self):
        """Marcar la fase de Creación Proyecto como generada cuando se selecciona un PDF"""
        try:
            # Verificar que el controlador de fases esté disponible
            if not hasattr(self._mw, 'controlador_fases') or not self._mw.controlador_fases:

                return
            
            if not self._contract_name:

                return
            

            
            # Marcar la fase de creación como generada
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            self._mw.controlador_fases.marcar_documento_generado('creacion', self._contract_name)
            

            
            # Actualizar cronograma si está disponible
            if (hasattr(self._mw, 'integrador_resumen') and 
                self._mw.integrador_resumen and
                hasattr(self._mw.integrador_resumen, '_actualizar_cronograma_visual')):
                
                # Usar QTimer para actualizar después de un breve retraso
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(200, lambda: self._actualizar_cronograma_tras_pdf())
                
        except Exception as e:
            print(f"[PDF] ❌ Error marcando fase de creación: {e}")
    
    def _registrar_fecha_creacion_en_fases(self, pdf_path: str):
        """Registrar fecha de creación en fases_documentos.creacion.generado"""
        try:
            if not self._contract_name:

                return
                
            if not os.path.exists(pdf_path):

                return
                
            # Obtener fecha de creación del archivo PDF
            timestamp_creacion = os.path.getctime(pdf_path)
            fecha_creacion = datetime.fromtimestamp(timestamp_creacion)
            fecha_str = fecha_creacion.strftime('%Y-%m-%d')
            

            
            # Verificar que el controlador JSON esté disponible
            if not hasattr(self._mw, 'controlador_json') or not self._mw.controlador_json:
                print("[PDF] ❌ Controlador JSON no disponible para registrar fecha en fases")
                return
            
            # Leer datos actuales del contrato
            datos_contrato = self._mw.controlador_json.leer_contrato_completo(self._contract_name)
            if not datos_contrato:
                print(f"[PDF] ❌ No se encontraron datos del contrato para registrar fecha: {self._contract_name}")
                return
            
            # Asegurar que existe la estructura fases_documentos
            if 'fases_documentos' not in datos_contrato:
                datos_contrato['fases_documentos'] = {}

            
            if 'creacion' not in datos_contrato['fases_documentos']:
                datos_contrato['fases_documentos']['creacion'] = {
                    'generado': None,
                    'firmado': None
                }

            
            # Establecer la fecha de generado
            datos_contrato['fases_documentos']['creacion']['generado'] = fecha_str
            
            # Guardar cambios en JSON
            self._mw.controlador_json.guardar_contrato_completo(self._contract_name, datos_contrato)
            

            
        except Exception as e:
            print(f"[PDF] ❌ Error registrando fecha de creación en fases: {e}")
            import traceback
            traceback.print_exc()
    
    def _actualizar_cronograma_tras_pdf(self):
        """Actualizar cronograma después de marcar la fase de creación"""
        try:
            if (hasattr(self._mw, 'integrador_resumen') and 
                self._mw.integrador_resumen and
                self._contract_name):
                
                self._mw.integrador_resumen._actualizar_cronograma_visual(self._contract_name)

                
        except Exception as e:
            print(f"[PDF] ❌ Error actualizando cronograma tras PDF: {e}")
    def get_project_folder_path(self) -> str:
        """Obtener la ruta de la carpeta del proyecto actual"""
        if not self._contract_name:
            return ""
        
        current_dir = os.getcwd()
        for root, dirs, files in os.walk(current_dir):
            for dir_name in dirs:
                if self._contract_name.lower() in dir_name.lower():
                    proyecto_path = os.path.join(root, dir_name, "01-proyecto")
                    if os.path.exists(proyecto_path):
                        return proyecto_path
        return ""
def setup_pdf_viewer_simple(main_window: QObject, container_name: str = "contenedor_pdf") -> _PDFControllerOptimized:
    """API compatible con el controlador original"""
    controller = _PDFControllerOptimized(main_window)
    return controller

# ===== FUNCIONES DE CONVERSIÓN DOCX A PDF (MIGRADAS DESDE archivos_py.py) =====

class DialogoPDF(QDialog):
    def __init__(self, parent=None, nombre_documento="documento"):
        super().__init__(parent)
        self.nombre_documento = nombre_documento
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle("Conversión a PDF")
        self.setFixedSize(400, 180)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("¿Generar también PDF?")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Descripción
        descripcion = QLabel(f"Se generará el documento '{self.nombre_documento}'")
        descripcion.setAlignment(Qt.AlignCenter)
        descripcion.setFont(QFont("Arial", 10))
        layout.addWidget(descripcion)
        
        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(20)
        
        btn_si = QPushButton("✓ Sí, con PDF")
        btn_si.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_si.clicked.connect(self.accept)
        
        btn_no = QPushButton("✗ No, solo Word")
        btn_no.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_no.clicked.connect(self.reject)
        
        botones_layout.addWidget(btn_si)
        botones_layout.addWidget(btn_no)
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)

def convertir_docx_a_pdf_simple(docx_path: str) -> bool:
    """Conversión usando docx2pdf"""
    try:
        if not os.path.exists(docx_path):
            print(f"[PDF] ERROR: Archivo no existe: {docx_path}")
            return False
            
        from docx2pdf import convert
        pdf_path = docx_path.replace('.docx', '.pdf')
        
        print(f"[PDF] Generando PDF: {os.path.basename(pdf_path)}")
        
        # Crear popup con progress bar
        from PyQt5.QtWidgets import QProgressDialog, QApplication
        from PyQt5.QtCore import Qt, QTimer
        import time
        import sys
        
        progress = QProgressDialog("Generando PDF...", "Cancelar", 0, 100)
        progress.setWindowTitle("Generando PDF")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        
        # Solo agregar icono en versión compilada (EXE)
        if getattr(sys, 'frozen', False):  # Detectar PyInstaller
            try:
                from PyQt5.QtGui import QIcon
                icono_path = "_internal/images/icono.ico"
                if os.path.exists(icono_path):
                    progress.setWindowIcon(QIcon(icono_path))
                    print(f"[PDF] Icono aplicado en versión EXE: {icono_path}")
            except Exception as e:
                print(f"[PDF] Error cargando icono: {e}")
        
        progress.show()
        
        # Simular progreso mientras se genera el PDF
        for i in range(101):
            if progress.wasCanceled():
                break
            progress.setValue(i)
            QApplication.processEvents()
            
            # Generar PDF cuando llegue al 50%
            if i == 50:
                convert(docx_path, pdf_path)
            
            # Pequeña pausa para mostrar el progreso
            time.sleep(0.03)
        
        progress.close()
        
        exists = os.path.exists(pdf_path)
        if exists:
            print(f"[PDF] ✓ PDF generado correctamente: {pdf_path}")
        else:
            print(f"[PDF] ERROR: No se pudo generar el PDF")
            
        return exists
        
    except Exception as e:
        print(f"[PDF] ERROR: {e}")
        return False


def mostrar_dialogo_pdf(parent=None, nombre_documento="documento", docx_path=None) -> bool:
    """Función principal simplificada"""
    try:
        # Crear y mostrar diálogo
        dialogo = DialogoPDF(parent, nombre_documento)
        
        if dialogo.exec_() == QDialog.Accepted:
            if docx_path and os.path.exists(docx_path):
                # Conversión simple y directa
                if convertir_docx_a_pdf_simple(docx_path):
                    pdf_path = docx_path.replace('.docx', '.pdf')
                    QMessageBox.information(parent, "Éxito", 
                                          f"✅ PDF generado correctamente")
                    
                    # Abrir automáticamente el PDF
                    import subprocess
                    import os
                    try:
                        print(f"[PDF] Abriendo PDF automáticamente: {pdf_path}")
                        subprocess.run([pdf_path], shell=True, check=True)
                    except Exception as e:
                        print(f"[PDF] Error abriendo PDF: {e}")
                        # Si falla abrir el PDF, abrir la carpeta
                        carpeta = os.path.dirname(docx_path)
                        subprocess.run(f'explorer "{carpeta}"', shell=True)
                    
                else:
                    QMessageBox.warning(parent, "Error", 
                                      "❌ No se pudo convertir a PDF")
            return True
        return False
        
    except Exception:
        return False


if __name__ == "__main__":
    # Test del controlador optimizado
    from PyQt5.QtWidgets import QApplication, QMainWindow
    import sys
    
    app = QApplication(sys.argv)
    
    # Simular main window
    main_window = QMainWindow()
    
    # Crear controlador optimizado
    pdf_controller = _PDFControllerOptimized(main_window)
    


    
    # Simular activación de pestaña después de 3 segundos
    QTimer.singleShot(3000, pdf_controller.on_tab_activated)
    
    app.exec_()