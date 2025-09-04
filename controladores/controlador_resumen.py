#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
CONTROLADOR DE RESUMEN UNIFICADO PARA ADIF

Este módulo unifica toda la funcionalidad de resumen en un solo controlador:
- TrackerDocumentos: Rastrea y gestiona documentos generados  
- WidgetResumenIntegrado: Widget completo de resumen con UI integrada
- IntegradorResumen: Sistema de integración automática con la aplicación principal

Anteriormente distribuido en: integrador_resumen.py, tracker_documentos.py, widget_resumen.py
"""
import os
import json
import datetime
import re
import glob
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                            QGroupBox, QPushButton, QProgressBar, QScrollArea, QFrame, 
                            QGridLayout, QSplitter, QTabWidget, QMessageBox, QGraphicsView, 
                            QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsLineItem,
                            QDateEdit, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush


# =================== ENUMS Y DATACLASSES ===================


class EstadoDocumento(Enum):
    GENERANDO = "generando"
    GENERADO = "generado"
    ERROR = "error"
    MODIFICADO = "modificado"
    ENVIADO = "enviado"
    FIRMADO = "firmado"

class TipoDocumento(Enum):
    INVITACION = "invitacion"
    ADJUDICACION = "adjudicacion"
    ACTA_INICIO = "acta_inicio"
    ACTA_REPLANTEO = "acta_replanteo"
    ACTA_RECEPCION = "acta_recepcion"
    ACTA_FINALIZACION = "acta_finalizacion"
    LIQUIDACION = "liquidacion"
    CONTRATO = "contrato"
    OTRO = "otro"

@dataclass
class DocumentoGenerado:
    id: str
    tipo: TipoDocumento
    nombre: str
    ruta_archivo: str
    fecha_generacion: datetime.datetime
    estado: EstadoDocumento
    tamano_kb: float
    observaciones: str = ""
    plantilla_usada: str = ""



# =================== TRACKER DE DOCUMENTOS ===================

class TrackerDocumentos:
    """Gestor del historial de documentos generados"""
    
    def __init__(self, ruta_base: str = None):
        if ruta_base:
            self.ruta_base = ruta_base
            self.archivo_historial = os.path.join(self.ruta_base, "historial_documentos.json")
        else:
            # Usar el sistema de rutas centralizado
            from .controlador_routes import rutas
            self.ruta_base = rutas.get_base_path()
            self.archivo_historial = rutas.get_ruta_historial_documentos()
        self.documentos: Dict[str, List[DocumentoGenerado]] = {}
        self.cargar_historial()
    
    def cargar_historial(self):
        try:
            if os.path.exists(self.archivo_historial):
                with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.documentos = {}
                for contrato, docs_data in data.items():
                    self.documentos[contrato] = []
                    for doc_data in docs_data:
                        try:
                            doc = DocumentoGenerado(
                                id=doc_data['id'],
                                tipo=TipoDocumento(doc_data['tipo']),
                                nombre=doc_data['nombre'],
                                ruta_archivo=doc_data['ruta_archivo'],
                                fecha_generacion=datetime.datetime.fromisoformat(doc_data['fecha_generacion']),
                                estado=EstadoDocumento(doc_data['estado']),
                                tamano_kb=doc_data['tamano_kb'],
                                observaciones=doc_data.get('observaciones', ''),
                                plantilla_usada=doc_data.get('plantilla_usada', '')
                            )
                            self.documentos[contrato].append(doc)
                        except (KeyError, ValueError) as e:
                            logger.error(f"Error cargando documento: {e}")
                            continue
            else:
                self.documentos = {}
        except Exception as e:
            logger.error(f"Error cargando historial: {e}")
            self.documentos = {}
    
    def guardar_historial(self):
        try:
            os.makedirs(os.path.dirname(self.archivo_historial), exist_ok=True)
            
            data = {}
            for contrato, docs in self.documentos.items():
                data[contrato] = []
                for doc in docs:
                    doc_dict = {
                        'id': doc.id,
                        'tipo': doc.tipo.value if hasattr(doc.tipo, 'value') else str(doc.tipo),
                        'nombre': doc.nombre,
                        'ruta_archivo': doc.ruta_archivo,
                        'fecha_generacion': doc.fecha_generacion.isoformat(),
                        'estado': doc.estado.value if hasattr(doc.estado, 'value') else str(doc.estado),
                        'tamano_kb': doc.tamano_kb,
                        'observaciones': doc.observaciones,
                        'plantilla_usada': doc.plantilla_usada
                    }
                    data[contrato].append(doc_dict)
            
            with open(self.archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")
            return False
    
    def registrar_documento_iniciado(self, contrato: str, tipo, nombre: str, plantilla: str = "") -> str:
        import uuid
        documento_id = str(uuid.uuid4())[:8]
        
        # Convertir tipo a enum si es necesario
        if isinstance(tipo, str):
            try:
                # Intentar mapear strings comunes a TipoDocumento
                mapeo_tipos = {
                    'invitacion': TipoDocumento.INVITACION,
                    'adjudicacion': TipoDocumento.ADJUDICACION,
                    'acta_inicio': TipoDocumento.ACTA_INICIO,
                    'acta_replanteo': TipoDocumento.ACTA_REPLANTEO,
                    'acta_recepcion': TipoDocumento.ACTA_RECEPCION,
                    'acta_finalizacion': TipoDocumento.ACTA_FINALIZACION,
                    'liquidacion': TipoDocumento.LIQUIDACION,
                    'contrato': TipoDocumento.CONTRATO
                }
                tipo_enum = mapeo_tipos.get(tipo.lower(), TipoDocumento.OTRO)
            except:
                tipo_enum = TipoDocumento.OTRO
        else:
            tipo_enum = tipo
        
        documento = DocumentoGenerado(
            id=documento_id,
            tipo=tipo_enum,
            nombre=nombre,
            ruta_archivo="",
            fecha_generacion=datetime.datetime.now(),
            estado=EstadoDocumento.GENERANDO,
            tamano_kb=0.0,
            plantilla_usada=plantilla
        )
        
        if contrato not in self.documentos:
            self.documentos[contrato] = []
        
        self.documentos[contrato].append(documento)
        self.guardar_historial()
        return documento_id
    
    def registrar_documento_completado(self, contrato: str, documento_id: str, ruta_archivo: str, observaciones: str = ""):
        documento = self._buscar_documento(contrato, documento_id)
        if documento:
            documento.ruta_archivo = ruta_archivo
            documento.estado = EstadoDocumento.GENERADO
            documento.tamano_kb = self._obtener_tamano_archivo(ruta_archivo)
            documento.observaciones = observaciones
            self.guardar_historial()
    
    def registrar_documento_error(self, contrato: str, documento_id: str, error: str):
        documento = self._buscar_documento(contrato, documento_id)
        if documento:
            documento.estado = EstadoDocumento.ERROR
            documento.observaciones = f"Error: {error}"
            self.guardar_historial()
    
    def obtener_documentos_contrato(self, contrato: str) -> List[DocumentoGenerado]:
        return self.documentos.get(contrato, [])
    
    def obtener_resumen_contrato(self, contrato: str) -> Dict[str, Any]:
        documentos = self.obtener_documentos_contrato(contrato)
        
        if not documentos:
            return {
                'total_documentos': 0,
                'por_tipo': {},
                'por_estado': {},
                'ultimo_generado': None,
                'tamano_total_kb': 0.0,
                'documentos_generados_hoy': 0,
                'documentos_con_error': 0
            }
        
        por_tipo = {}
        for doc in documentos:
            tipo = doc.tipo.value
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        
        por_estado = {}
        for doc in documentos:
            estado = doc.estado.value
            por_estado[estado] = por_estado.get(estado, 0) + 1
        
        ultimo_generado = max(documentos, key=lambda d: d.fecha_generacion)
        tamano_total = sum(doc.tamano_kb for doc in documentos if os.path.exists(doc.ruta_archivo))
        
        hoy = datetime.date.today()
        docs_hoy = len([d for d in documentos if d.fecha_generacion.date() == hoy and d.estado == EstadoDocumento.GENERADO])
        docs_error = len([d for d in documentos if d.estado == EstadoDocumento.ERROR])
        
        return {
            'total_documentos': len(documentos),
            'por_tipo': por_tipo,
            'por_estado': por_estado,
            'ultimo_generado': {
                'tipo': ultimo_generado.tipo.value,
                'nombre': ultimo_generado.nombre,
                'fecha': ultimo_generado.fecha_generacion.strftime('%Y-%m-%d %H:%M'),
                'estado': ultimo_generado.estado.value
            },
            'tamano_total_kb': tamano_total,
            'documentos_generados_hoy': docs_hoy,
            'documentos_con_error': docs_error
        }
    
    def generar_reporte_html(self, contrato: str) -> str:
        documentos = self.obtener_documentos_contrato(contrato)
        
        if not documentos:
            return "<p style='color: #666; text-align: center; padding: 20px;'>📄 No hay documentos generados para este contrato.</p>"
        
        html = f"<div class='historial-documentos'>"
        html += f"<h3 style='color: #1976D2; margin-bottom: 15px;'>📄 Historial de Documentos - {contrato}</h3>"
        
        # Agrupar por fecha
        por_fecha = {}
        for doc in sorted(documentos, key=lambda d: d.fecha_generacion, reverse=True):
            fecha = doc.fecha_generacion.strftime('%Y-%m-%d')
            if fecha not in por_fecha:
                por_fecha[fecha] = []
            por_fecha[fecha].append(doc)
        
        iconos = {
            TipoDocumento.INVITACION: "📧",
            TipoDocumento.ADJUDICACION: "🏆", 
            TipoDocumento.ACTA_INICIO: "🚀",
            TipoDocumento.ACTA_REPLANTEO: "📐",
            TipoDocumento.ACTA_RECEPCION: "✅",
            TipoDocumento.ACTA_FINALIZACION: "🏁",
            TipoDocumento.LIQUIDACION: "💰",
            TipoDocumento.CONTRATO: "📋",
            TipoDocumento.OTRO: "📄"
        }
        
        colores = {
            EstadoDocumento.GENERADO: "#4CAF50",
            EstadoDocumento.ERROR: "#F44336", 
            EstadoDocumento.GENERANDO: "#FF9800",
            EstadoDocumento.MODIFICADO: "#9C27B0",
            EstadoDocumento.ENVIADO: "#2196F3",
            EstadoDocumento.FIRMADO: "#4CAF50"
        }
        
        for fecha, docs_fecha in por_fecha.items():
            html += f"<h4 style='color: #555; border-bottom: 1px solid #ddd; padding-bottom: 5px;'>📅 {fecha}</h4>"
            html += "<ul style='list-style: none; padding-left: 0;'>"
            
            for doc in docs_fecha:
                icono = iconos.get(doc.tipo, "📄")
                color = colores.get(doc.estado, "#666")
                hora = doc.fecha_generacion.strftime('%H:%M')
                
                html += f"<li style='margin: 8px 0; padding: 8px; background: #f9f9f9; border-radius: 5px;'>"
                html += f"<div style='display: flex; align-items: center; justify-content: space-between;'>"
                html += f"<div>{icono} <strong>{doc.nombre}</strong></div>"
                html += f"<div style='font-size: 12px; color: #666;'>{hora}</div>"
                html += f"</div>"
                
                html += f"<div style='margin-top: 4px; font-size: 11px;'>"
                html += f"<span style='color: {color}; font-weight: bold;'>● {doc.estado.value.upper()}</span>"
                
                if os.path.exists(doc.ruta_archivo):
                    html += f" • {doc.tamano_kb:.1f} KB"
                else:
                    html += f" • <span style='color: #F44336;'>Archivo no encontrado</span>"
                
                if doc.plantilla_usada:
                    html += f" • {doc.plantilla_usada}"
                
                html += f"</div>"
                
                if doc.observaciones:
                    html += f"<div style='margin-top: 4px; font-size: 10px; color: #666; font-style: italic;'>{doc.observaciones}</div>"
                
                html += "</li>"
            
            html += "</ul>"
        
        html += "</div>"
        return html
    
    def _buscar_documento(self, contrato: str, documento_id: str) -> Optional[DocumentoGenerado]:
        documentos = self.obtener_documentos_contrato(contrato)
        for doc in documentos:
            if doc.id == documento_id:
                return doc
        return None
    
    def _obtener_tamano_archivo(self, ruta_archivo: str) -> float:
        try:
            if os.path.exists(ruta_archivo):
                return os.path.getsize(ruta_archivo) / 1024
            return 0.0
        except OSError:
            return 0.0


# =================== WIDGET DE RESUMEN INTEGRADO ===================



# =================== INTEGRADOR PRINCIPAL ===================

class IntegradorResumen:
    """Integrador principal para agregar el resumen a la aplicación"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.widget_resumen = None
        self.tab_index = None
    
    def _obtener_nombre_carpeta_actual(self, nombre_contrato: str) -> str:
        """Obtener el nombre real de la carpeta desde el JSON (considerando cambios de expediente)"""
        try:
            # Obtener datos del contrato desde el JSON
            if hasattr(self.main_window, 'controlador_json') and self.main_window.controlador_json:
                contrato_data = self.main_window.controlador_json.leer_contrato_completo(nombre_contrato)
                if contrato_data and 'nombreCarpeta' in contrato_data:
                    nombre_carpeta = contrato_data['nombreCarpeta']
                    logger.info(f"[IntegradorResumen] 📁 Nombre de carpeta desde JSON: {nombre_carpeta}")
                    return nombre_carpeta
            
            # Fallback: usar nombre del contrato si no hay nombreCarpeta en JSON
            logger.warning(f"[IntegradorResumen] Usando nombre de contrato como fallback: {nombre_contrato}")
            return nombre_contrato
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error obteniendo nombre carpeta: {e}")
            return nombre_contrato  # Fallback seguro
    
    def integrar_en_aplicacion(self) -> bool:
        """Integrar el widget de resumen en la aplicación principal"""
        try:

            
            # Solo conectar señales, no agregar tabs
            self._conectar_senales()
            

            return True
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error integrando: {e}")
            return False
    
    def _encontrar_tab_widget(self):
        """Encontrar el QTabWidget principal"""
        # Buscar por atributos comunes
        for attr_name in ['tabWidget', 'tab_widget', 'main_tabs', 'tabs']:
            if hasattr(self.main_window, attr_name):
                tab_widget = getattr(self.main_window, attr_name)
                if isinstance(tab_widget, QTabWidget):
                    return tab_widget
        
        # Buscar recursivamente
        tab_widgets = self.main_window.findChildren(QTabWidget)
        return tab_widgets[0] if tab_widgets else None
    
    def _conectar_senales(self):
        """Conectar señales automáticamente"""
        try:
            # Conectar botones del tab Resumen
            self._conectar_botones_ui()
            

            
        except Exception as e:
            logger.warning(f"[IntegradorResumen] Error conectando señales: {e}")
    
    def _conectar_botones_ui(self):
        """Conectar botones específicos del tab Resumen y agregar cronograma"""
        try:

            
            # Buscar botones por nombre
            btn_generar = self.main_window.findChild(QPushButton, 'btn_generar_fichero_resumen')
            btn_actualizar = self.main_window.findChild(QPushButton, 'btn_actualizar_resumen')
            

            
            # Búsqueda alternativa si no se encuentran
            if not btn_generar:
                if hasattr(self.main_window, 'btn_generar_fichero_resumen'):
                    btn_generar = self.main_window.btn_generar_fichero_resumen

                    
            if not btn_actualizar:
                if hasattr(self.main_window, 'btn_actualizar_resumen'):
                    btn_actualizar = self.main_window.btn_actualizar_resumen

                    
            
            
            # Agregar cronograma visual al tab Resumen
            self._agregar_cronograma_visual()
            
            if btn_generar:
                # Desconectar cualquier conexión previa
                try:
                    btn_generar.clicked.disconnect()
                except:
                    pass
                # Conectar la función
                btn_generar.clicked.connect(self._on_generar_fichero_resumen)

            else:
                logger.info("[IntegradorResumen] ❌ No se encontró btn_generar_fichero_resumen")
            
            if btn_actualizar:
                # Desconectar cualquier conexión previa
                try:
                    btn_actualizar.clicked.disconnect()
                except:
                    pass
                # Conectar la función
                btn_actualizar.clicked.connect(self._on_actualizar_resumen)

            else:
                logger.info("[IntegradorResumen] ❌ No se encontró btn_actualizar_resumen")
            
            # Guardar referencia al área de texto
                
        except Exception as e:
            logger.warning(f"[IntegradorResumen] Error conectando botones UI: {e}")
    
    def reconectar_botones_si_es_necesario(self):
        """Método público para reconectar botones si es necesario"""

        try:
            self._conectar_botones_ui()
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error reconectando botones: {e}")
    
    def test_botones_resumen(self):
        """Método de prueba para verificar que los botones funcionan"""
        # Test botón actualizar
        try:
            self._on_actualizar_resumen()
        except Exception as e:
            logger.error(f"[IntegradorResumen] Test botón actualizar: ERROR - {e}")
        
        # Test botón generar  
        try:
            self._on_generar_fichero_resumen()
        except Exception as e:
            logger.error(f"[IntegradorResumen] Test botón generar: ERROR - {e}")
    
    def test_tabla_seguimiento(self):
        """Método específico para probar la tabla de seguimiento"""
        try:
            # Buscar la tabla
            tabla_seguimiento = self.main_window.findChild(QTableWidget, 'Tabla_seguimiento')
            
            if tabla_seguimiento:
                # Probar configuración básica
                tabla_seguimiento.setRowCount(3)
                tabla_seguimiento.setColumnCount(3)
                tabla_seguimiento.setHorizontalHeaderLabels(['Test1', 'Test2', 'Test3'])
                
                # Añadir datos de prueba
                for fila in range(3):
                    for col in range(3):
                        item = QTableWidgetItem(f"Test-{fila}-{col}")
                        tabla_seguimiento.setItem(fila, col, item)
                
                # Forzar actualización
                tabla_seguimiento.resizeColumnsToContents()
                tabla_seguimiento.update()
            else:
                all_tables = self.main_window.findChildren(QTableWidget)
                logger.error(f"[IntegradorResumen] Tabla NO encontrada. Disponibles: {[t.objectName() for t in all_tables]}")
                
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error en test tabla: {e}")
            import traceback
            logger.exception("Error completo:")
    
    def _on_anchor_clicked(self, url):
        """Manejar clics en enlaces (especialmente para PDFs)"""
        try:
            from PyQt5.QtCore import QUrl
            import os
            import subprocess
            import platform
            
            url_str = url.toString()
            logger.info(f"[IntegradorResumen] 🔗 Enlace clickeado: {url_str}")
            
            # Extraer ruta del archivo si es un enlace file://
            if url_str.startswith('file:///'):
                file_path = url_str[8:]  # Remover 'file:///'
                # Convertir separadores de ruta para Windows
                if platform.system() == "Windows":
                    file_path = file_path.replace('/', os.sep)
                
                logger.debug(f"[IntegradorResumen] Abriendo archivo: {file_path}")
                
                if os.path.exists(file_path):
                    # Abrir archivo con aplicación por defecto del sistema
                    try:
                        if platform.system() == "Windows":
                            os.startfile(file_path)
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.Popen(["open", file_path])
                        else:  # Linux
                            subprocess.Popen(["xdg-open", file_path])
                        
                        logger.info(f"[IntegradorResumen] Archivo abierto exitosamente: {os.path.basename(file_path)}")
                    except Exception as e:
                        logger.error(f"[IntegradorResumen] Error abriendo archivo: {e}")
                        # Mostrar mensaje de error al usuario
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(
                            self.main_window, 
                            "Error", 
                            f"No se pudo abrir el archivo:\n{e}"
                        )
                else:
                    logger.error(f"[IntegradorResumen] Archivo no encontrado: {file_path}")
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self.main_window, 
                        "Archivo no encontrado", 
                        f"El archivo no existe:\n{file_path}"
                    )
            else:
                # Para otros tipos de enlaces, usar comportamiento por defecto
                logger.info(f"[IntegradorResumen] 🌐 Enlace externo: {url_str}")
                
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error manejando enlace: {e}")
    
    def _agregar_cronograma_visual(self):
        """Configurar el cronograma visual que ya existe en el UI"""
        try:
            # Buscar el QGraphicsView que está definido en actas.ui
            cronograma_view = self.main_window.findChild(QGraphicsView, "cronograma_fases_timeline")
            
            if not cronograma_view:
                logger.info("[IntegradorResumen] ⚠️ No se encontró el QGraphicsView cronograma_fases_timeline en el UI")
                return
            
            # Configurar propiedades adicionales del QGraphicsView
            cronograma_view.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
            cronograma_view.setDragMode(QGraphicsView.NoDrag)
            

                
        except Exception as e:
            logger.warning(f"[IntegradorResumen] Error configurando cronograma visual: {e}")
    
    def _actualizar_cronograma_visual(self, nombre_contrato: str):
        """Actualizar el cronograma visual existente en el UI"""
        try:
            # Buscar el QGraphicsView que está definido en actas.ui
            cronograma_view = self.main_window.findChild(QGraphicsView, "cronograma_fases_timeline")
            
            if not cronograma_view:
                logger.info("[IntegradorResumen] ⚠️ No se encontró el QGraphicsView cronograma_fases_timeline en el UI")
                return
            
            # Limpiar la escena actual
            if cronograma_view.scene():
                cronograma_view.scene().clear()
            else:
                # Crear nueva escena si no existe
                scene = QGraphicsScene()
                cronograma_view.setScene(scene)
            
            # Dibujar el timeline actualizado
            scene = cronograma_view.scene()
            
            # Usar datos de firmas (mismos que la tabla de seguimiento)
            if hasattr(self, '_datos_firmas_cache') and hasattr(self, '_firmantes_unicos_cache'):
                datos_firmas = self._datos_firmas_cache
                firmantes_unicos = self._firmantes_unicos_cache
                
                if datos_firmas:
                    self._dibujar_timeline_firmas(scene, datos_firmas, firmantes_unicos)
                else:
                    # Mostrar mensaje si no hay firmas
                    texto = scene.addText("No hay datos de firmas disponibles", QFont("Arial", 12))
                    texto.setPos(20, 20)
            else:
                # Mostrar mensaje de error
                texto = scene.addText("Datos de seguimiento no disponibles\nPulsa 'Actualizar' para cargar los datos", QFont("Arial", 12))
                texto.setPos(20, 20)
                
        except Exception as e:
            logger.warning(f"[IntegradorResumen] Error actualizando cronograma visual: {e}")
    
    def _dibujar_timeline_firmas(self, scene: QGraphicsScene, datos_firmas: dict, firmantes_unicos: list):
        """Dibujar timeline usando datos de firmas (igual que la tabla de seguimiento)"""
        try:
            from PyQt5.QtCore import QRectF
            from PyQt5.QtGui import QBrush, QPen
            
            # Configuración visual
            ANCHO_BARRA = 800
            ALTO_FASE = 60
            MARGEN_SUPERIOR = 50
            MARGEN_IZQUIERDO = 20
            
            # Fases a mostrar (mismo orden que la tabla)
            fases_mostrar = ['CREACION', 'INICIO', 'CARTASINVITACION', 'ADJUDICACION', 'CARTASADJUDICACION', 'CONTRATO', 
                           'REPLANTEO', 'ACTUACION', 'RECEPCION', 'FINALIZACION']
            
            # Colores por estado
            COLOR_COMPLETADO = QBrush(QColor(144, 238, 144))  # Verde claro
            COLOR_DOCUMENTO = QBrush(QColor(255, 255, 200))   # Amarillo
            COLOR_SIN_DATOS = QBrush(QColor(255, 200, 200))   # Rojo claro
            
            y_pos = MARGEN_SUPERIOR
            
            for i, fase in enumerate(fases_mostrar):
                # Determinar estado de la fase
                tiene_documento = False
                tiene_firmas = False
                
                if fase in datos_firmas:
                    info_fase = datos_firmas[fase]
                    tiene_documento = bool(info_fase.get('fecha_creacion'))
                    tiene_firmas = bool(info_fase.get('firmas'))
                
                # Elegir color según estado
                if tiene_firmas:
                    color = COLOR_COMPLETADO
                    estado = "✅ Firmado"
                elif tiene_documento:
                    color = COLOR_DOCUMENTO
                    estado = "📄 Documento"
                else:
                    color = COLOR_SIN_DATOS
                    estado = "⏸️ Pendiente"
                
                # Dibujar barra de fase
                rect = QRectF(MARGEN_IZQUIERDO, y_pos, ANCHO_BARRA, ALTO_FASE - 10)
                barra = scene.addRect(rect, QPen(QColor(0, 0, 0)), color)
                
                # Título de la fase
                titulo = scene.addText(f"{fase} - {estado}", QFont("Arial", 12, QFont.Bold))
                titulo.setPos(MARGEN_IZQUIERDO + 10, y_pos + 5)
                
                # Información adicional
                if fase in datos_firmas:
                    info_fase = datos_firmas[fase]
                    detalles = []
                    
                    # Fecha de creación de documento
                    if info_fase.get('fecha_creacion'):
                        detalles.append(f"📅 Doc: {info_fase['fecha_creacion']}")
                    
                    # Última fecha de firma
                    if info_fase.get('firmas'):
                        fechas_firmas = [f['fecha'] for f in info_fase['firmas'] if 'fecha' in f]
                        if fechas_firmas:
                            fecha_ultima = max(fechas_firmas)
                            detalles.append(f"✍️ Última firma: {fecha_ultima}")
                        
                        # Número de firmantes
                        num_firmantes = len(info_fase['firmas'])
                        detalles.append(f"👥 {num_firmantes} firmante(s)")
                    
                    if detalles:
                        detalle_texto = " | ".join(detalles)
                        detalle_item = scene.addText(detalle_texto, QFont("Arial", 9))
                        detalle_item.setPos(MARGEN_IZQUIERDO + 10, y_pos + 25)
                
                y_pos += ALTO_FASE
            
            # Agregar leyenda
            y_leyenda = y_pos + 20
            leyenda_titulo = scene.addText("📋 Leyenda:", QFont("Arial", 10, QFont.Bold))
            leyenda_titulo.setPos(MARGEN_IZQUIERDO, y_leyenda)
            
            leyenda_items = [
                "✅ Firmado: Fase con documentos y firmas",
                "📄 Documento: Documento generado pero sin firmas",
                "⏸️ Pendiente: No hay documento ni firmas"
            ]
            
            for i, item in enumerate(leyenda_items):
                item_texto = scene.addText(item, QFont("Arial", 9))
                item_texto.setPos(MARGEN_IZQUIERDO, y_leyenda + 20 + (i * 15))
            

            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error dibujando timeline de firmas: {e}")
    
    def _on_generar_fichero_resumen(self):
        """Generar documento Word con resumen del contrato"""
        logger.info("[IntegradorResumen] 📄 ===== GENERANDO DOCUMENTO WORD =====")
        
        try:
            # 1. Verificar contrato seleccionado
            logger.info("[IntegradorResumen] 🔍 Verificando contrato seleccionado...")
            nombre_contrato = ""
            
            if hasattr(self.main_window, 'comboBox'):
                nombre_contrato = self.main_window.comboBox.currentText()
                logger.info(f"[IntegradorResumen] 📋 Contrato: '{nombre_contrato}'")
            else:
                logger.info("[IntegradorResumen] ❌ ComboBox no encontrado")
                self._mostrar_mensaje_error("Error: No se encontró el selector de contratos")
                return
            
            if not nombre_contrato or nombre_contrato == "Seleccionar contrato...":
                logger.info("[IntegradorResumen] ⚠️ No hay contrato válido")
                self._mostrar_mensaje_error("No hay contrato seleccionado.\n\nPor favor, selecciona un contrato en el ComboBox principal.")
                return
            
            # 2. Sincronizar fechas antes de generar (si está disponible)
            logger.info("[IntegradorResumen] 🔄 Sincronizando datos...")
            if hasattr(self.main_window, 'controlador_fases'):
                try:
                    self.main_window.controlador_fases.reparar_sincronizacion_fases(nombre_contrato)
                    self.main_window.controlador_fases.sincronizar_todas_fechas_a_json(nombre_contrato)
                    logger.info("[IntegradorResumen] ✅ Fechas sincronizadas")
                except Exception as e:
                    logger.warning(f"[IntegradorResumen] Error sincronizando fechas: {e}")
            
            # 3. Obtener datos del contrato
            logger.info("[IntegradorResumen] 📊 Obteniendo datos del contrato...")
            datos_contrato = self._obtener_datos_contrato_completos(nombre_contrato)
            
            if not datos_contrato:
                logger.info("[IntegradorResumen] ❌ No se pudieron obtener datos")
                self._mostrar_mensaje_error("No se pudieron obtener los datos del contrato.\n\nVerifica que el contrato esté guardado correctamente.")
                return
            
            logger.info(f"[IntegradorResumen] Datos obtenidos: {len(datos_contrato)} campos")
            
            # 4. Actualizar estado del botón
            self._actualizar_estado_boton_generar("📝 Generando documento...")
            
            # 5. Generar fichero Word
            logger.info("[IntegradorResumen] 📝 Generando documento Word...")
            ruta_archivo = self.generar_fichero_resumen(nombre_contrato, datos_contrato)
            
            if ruta_archivo:
                logger.info(f"[IntegradorResumen] Documento generado: {ruta_archivo}")
                
                # 6. Mostrar resultado exitoso
                self._mostrar_mensaje_exito(f"✅ Documento Word generado exitosamente!\n\nArchivo: {ruta_archivo}\n\nEl documento se abrirá automáticamente.")
                
                # 7. Abrir archivo automáticamente
                try:
                    import os
                    import subprocess
                    import platform
                    
                    if platform.system() == "Windows":
                        os.startfile(ruta_archivo)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.Popen(["open", ruta_archivo])
                    else:  # Linux
                        subprocess.Popen(["xdg-open", ruta_archivo])
                    
                    logger.info("[IntegradorResumen] 📂 Archivo abierto automáticamente")
                except Exception as e:
                    logger.warning(f"[IntegradorResumen] Error abriendo archivo: {e}")
                
            else:
                logger.info("[IntegradorResumen] ❌ Error: No se generó archivo")
                self._mostrar_mensaje_error("Error generando documento.\n\nNo se pudo crear el archivo Word.")
            
            # 8. Restaurar estado del botón
            self._actualizar_estado_boton_generar("📄 Generar Resumen Word")
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] ERROR GENERANDO DOCUMENTO: {e}")
            import traceback
            logger.exception("Error completo:")
            
            # Restaurar botón y mostrar error
            self._actualizar_estado_boton_generar("📄 Generar Resumen Word")
            self._mostrar_mensaje_error(f"Error generando documento Word:\n\n{e}")
            
        logger.info("[IntegradorResumen] 📄 Proceso de generación completado")
    
    def _on_actualizar_resumen(self):
        """Actualizar resumen del contrato seleccionado"""
        try:
            # 1. Verificar contrato seleccionado
            nombre_contrato = ""
            
            if hasattr(self.main_window, 'comboBox'):
                nombre_contrato = self.main_window.comboBox.currentText()
            else:
                return
            
            if not nombre_contrato or nombre_contrato == "Seleccionar contrato...":
                return
            
            # 3. Sincronizar fechas (si está disponible)
            if hasattr(self.main_window, 'controlador_fases'):
                try:
                    self.main_window.controlador_fases.reparar_sincronizacion_fases(nombre_contrato)
                    self.main_window.controlador_fases.sincronizar_todas_fechas_a_json(nombre_contrato)
                except Exception as e:
                    logger.warning(f"[IntegradorResumen] Error sincronizando fechas: {e}")
            
            # 4. Obtener datos del contrato
            datos_contrato = self._obtener_datos_contrato_completos(nombre_contrato)
            
            if not datos_contrato:
                return
            
            # 5. Test completo de escaneo de PDFs y firmas
            try:
                self.test_escaneo_pdf_completo(nombre_contrato)
                
                # Después del test, ejecutar escaneo normal
                self._escanear_y_actualizar_tabla_firmas(nombre_contrato)
            except Exception as e:
                logger.warning(f"[IntegradorResumen] Error escaneando firmas: {e}")
                import traceback
                logger.exception("Error completo:")
            
            # 6. Generar resumen HTML con fases
            html_resumen = self._generar_resumen_con_fases(nombre_contrato, datos_contrato)
            
            if not html_resumen:
                # Fallback: generar resumen básico
                html_basico = self._generar_resumen_basico(nombre_contrato, datos_contrato)
            
            # 7. Actualizar cronograma visual si existe
            try:
                self._actualizar_cronograma_visual(nombre_contrato)
            except Exception as e:
                logger.warning(f"[IntegradorResumen] Error actualizando cronograma: {e}")
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] ERROR ACTUALIZANDO RESUMEN: {e}")
            import traceback
            logger.exception("Error completo:")
            
    
    def _generar_resumen_basico(self, nombre_contrato: str, datos_contrato: dict) -> str:
        """Generar resumen básico como fallback"""
        try:
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #1976D2; text-align: center; margin-bottom: 20px;">📊 RESUMEN - {nombre_contrato}</h2>
                
                <div style="background: #E3F2FD; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #1976D2; margin-top: 0;">📋 Datos Principales</h3>
                    
                    <p><strong>📝 Tipo:</strong> {datos_contrato.get('tipoContrato', 'No especificado')}</p>
                    <p><strong>💰 Importe Total:</strong> {datos_contrato.get('importeTotal', 'No especificado')}</p>
                    <p><strong>🏆 Empresa Adjudicataria:</strong> {datos_contrato.get('empresaAdjudicataria', 'No especificado')}</p>
                    <p><strong>📅 Fecha Creación:</strong> {datos_contrato.get('fechaCreacion', 'No especificado')}</p>
                </div>
                
                <div style="background: #FFF3E0; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #F57C00; margin-top: 0;">ℹ️ Estado</h3>
                    <p style="color: #2196F3;">Resumen básico generado correctamente</p>
                    <p style="color: #666; font-size: 12px;">Para más detalles, use el botón "Generar Resumen Word"</p>
                </div>
            </div>
            """
            return html
        except Exception as e:
            return f"<p style='color: #F44336; text-align: center;'>Error generando resumen básico: {e}</p>"
    
    def _debug_fases_completo(self, nombre_contrato: str):
        """Debug completo: mostrar todos los DateEdit y datos del JSON"""
        try:
            logger.debug("=" * 80)
            logger.debug("🔧 DEBUG COMPLETO DE FASES")
            logger.debug("=" * 80)
            logger.info("📋 Contrato: {nombre_contrato}")
            logger.debug("")
            
            # 1. VERIFICAR SI HAY CONTROLADOR DE FASES
            if not hasattr(self.main_window, 'controlador_fases'):
                logger.error("❌ No hay controlador de fases disponible")
                return
                
            controlador_fases = self.main_window.controlador_fases
            
            # 2. LEER DATOS DEL JSON
            logger.info("📄 DATOS DEL JSON:")
            logger.debug("-" * 40)
            datos_contrato = controlador_fases._obtener_datos_contrato(nombre_contrato)
            
            if datos_contrato and "fases_documentos" in datos_contrato:
                fases_json = datos_contrato["fases_documentos"]
                for fase, datos in fases_json.items():
                    generado = datos.get("generado") or "null"
                    firmado = datos.get("firmado") or "null"
                    logger.info(f"  {fase:15} → generado: {str(generado):12} | firmado: {str(firmado)}")
            else:
                logger.info("  ⚠️ No se encontró 'fases_documentos' en el JSON")
            
            logger.debug("")
            
            # 3. LEER VALORES DE TODOS LOS DATEEDIT
            logger.info("🎛️ VALORES DE LOS DATEEDIT:")
            logger.debug("-" * 40)
            
            from PyQt5.QtWidgets import QDateEdit
            
            for fase, config in controlador_fases.fases_config.items():
                # DateEdit de generado (readonly)
                gen_field = config["generado_field"]
                gen_widget = self.main_window.findChild(QDateEdit, gen_field)
                gen_valor = gen_widget.date().toString("yyyy-MM-dd") if gen_widget else "NOT_FOUND"
                
                # DateEdit de firmado (editable)
                fir_field = config["firmado_field"]
                fir_widget = self.main_window.findChild(QDateEdit, fir_field)
                fir_valor = fir_widget.date().toString("yyyy-MM-dd") if fir_widget else "NOT_FOUND"
                
                logger.info(f"  {fase.value:15} → UI Gen: {gen_valor:12} | UI Fir: {fir_valor}")
            
            logger.debug("")
            logger.info("✅ Debug completo finalizado")
            logger.debug("=" * 80)
            
        except Exception as e:
            logger.error("❌ Error en debug de fases: {e}")
            import traceback
            logger.exception("Error completo:")
    
    
    def _generar_resumen_con_fases(self, nombre_contrato: str, datos_contrato: dict) -> str:
        """Generar HTML para la visualización del resumen incluyendo las fases"""
        try:
            tracker = TrackerDocumentos()
            
            # Análisis básico
            resumen_docs = tracker.obtener_resumen_contrato(nombre_contrato)
            
            # Obtener progreso de fases si está disponible
            progreso_fases = {}
            historial_fases = []
            if self.main_window and hasattr(self.main_window, 'controlador_fases'):
                progreso_fases = self.main_window.controlador_fases.obtener_resumen_progreso(nombre_contrato)
                historial_fases = self.main_window.controlador_fases.obtener_historial_actividad(nombre_contrato, 5)
            
            html = f"""
            <div style="font-family: Arial, sans-serif;">
                <h2 style="color: #1976D2; text-align: center; margin-bottom: 20px;">📊 RESUMEN - {nombre_contrato}</h2>
            """
            
            # Sección de progreso de fases (NUEVA)
            if progreso_fases:
                html += f"""
                <div style="background: #E8F5E8; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #4CAF50;">
                    <h3 style="color: #2E7D32; margin-top: 0;">🚀 PROGRESO DEL PROYECTO</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #1976D2;">
                                {progreso_fases.get('generados', 0)}/{progreso_fases.get('total', 9)}
                            </div>
                            <div style="font-size: 12px; color: #666;">📄 Documentos Generados</div>
                            <div style="background: #E3F2FD; height: 8px; border-radius: 4px; margin: 5px 0;">
                                <div style="background: #1976D2; height: 8px; border-radius: 4px; width: {progreso_fases.get('porcentaje_generados', 0)}%;"></div>
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #4CAF50;">
                                {progreso_fases.get('firmados', 0)}/{progreso_fases.get('total', 9)}
                            </div>
                            <div style="font-size: 12px; color: #666;">✍️ Documentos Firmados</div>
                            <div style="background: #E8F5E8; height: 8px; border-radius: 4px; margin: 5px 0;">
                                <div style="background: #4CAF50; height: 8px; border-radius: 4px; width: {progreso_fases.get('porcentaje_firmados', 0)}%;"></div>
                            </div>
                        </div>
                    </div>
                """
                
                if progreso_fases.get('proxima_fase'):
                    html += f"""
                    <div style="background: #FFF3E0; padding: 10px; border-radius: 5px; border-left: 3px solid #FF9800;">
                        <strong>📋 Próxima fase:</strong> {progreso_fases['proxima_fase']}
                    </div>
                    """
                
                html += "</div>"
            
            # Datos principales del contrato
            html += f"""
            <div style="background: #E3F2FD; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #1976D2; margin-top: 0;">📋 Datos Principales</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            """
            
            # Datos principales
            campos = [
                ('tipoContrato', 'Tipo', '📝'),
                ('importeTotal', 'Importe Total', '💰'),
                ('empresaAdjudicataria', 'Adjudicataria', '🏆'),
                ('fechaCreacion', 'Fecha Creación', '📅')
            ]
            
            for campo, etiqueta, icono in campos:
                valor = datos_contrato.get(campo, 'No especificado')
                if campo == 'importeTotal' and isinstance(valor, (int, float)):
                    valor = f"{valor:,.2f} €"
                html += f"<div><strong>{icono} {etiqueta}:</strong> {valor}</div>"
            
            # 🆕 NUEVO: Añadir información del archivo PDF del proyecto
            pdf_path = None
            campos_pdf = ['pdf_path', 'ubicacion_proyecto', 'rutaPdf', 'proyecto_pdf']
            
            for campo in campos_pdf:
                if campo in datos_contrato and datos_contrato[campo]:
                    pdf_path = datos_contrato[campo]
                    break
            
            if pdf_path:
                import os
                if os.path.exists(pdf_path):
                    pdf_filename = os.path.basename(pdf_path)
                    # Crear enlace clickeable para abrir el PDF (usando atributo data-pdf-path)
                    html += f"""
                    <div>
                        <strong>📄 Archivo Proyecto:</strong> 
                        <a href="file:///{pdf_path.replace(os.sep, '/')}" 
                           style="color: #1976D2; text-decoration: underline;" 
                           title="Clic para abrir {pdf_filename}">
                            {pdf_filename}
                        </a>
                    </div>
                    """
                else:
                    html += f"<div><strong>📄 Archivo Proyecto:</strong> <span style='color: #F44336;'>Archivo no encontrado</span></div>"
            else:
                html += f"<div><strong>📄 Archivo Proyecto:</strong> <span style='color: #666;'>No seleccionado</span></div>"
            
            html += "</div></div>"
            
            # Historial de actividad de fases (NUEVO)
            if historial_fases:
                html += """
                <div style="background: #FAFAFA; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="color: #1976D2; margin-top: 0;">📋 Actividad Reciente</h3>
                """
                
                for actividad in historial_fases[:5]:  # Solo las 5 más recientes
                    html += f"""
                    <div style="background: white; padding: 8px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #2196F3;">
                        <div style="font-size: 11px; color: #666; float: right;">{actividad['fecha']}</div>
                        <div>{actividad['descripcion']}</div>
                    </div>
                    """
                
                html += "</div>"
            
            # Métricas de documentos legacy
            html += f"""
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
            """
            
            # Métricas
            metricas = [
                ('📄', 'Total Docs', resumen_docs.get('total_documentos', 0)),
                ('📅', 'Hoy', resumen_docs.get('documentos_generados_hoy', 0)),
                ('💾', 'Tamaño', f"{resumen_docs.get('tamano_total_kb', 0):.1f} KB"),
                ('❌', 'Errores', resumen_docs.get('documentos_con_error', 0))
            ]
            
            for icono, label, valor in metricas:
                html += f"""
                    <div style="background: white; padding: 15px; text-align: center; border-radius: 8px; border: 1px solid #ddd;">
                        <div style="font-size: 1.5em;">{icono}</div>
                        <div style="font-weight: bold; color: #1976D2; font-size: 1.3em;">{valor}</div>
                        <div style="color: #666; font-size: 0.9em;">{label}</div>
                    </div>
                """
            
            html += "</div>"
            
            html += "</div>"
            
            return html
            
        except Exception as e:
            logger.info(f"[IntegradorResumen] Error generando resumen con fases: {e}")
    
    
    def _dibujar_timeline_fases(self, scene: QGraphicsScene, datos_fases: dict):
        """Dibujar el timeline de fases en la escena gráfica"""
        try:
            y_start = 20
            x_start = 50
            fase_height = 80
            line_x = x_start + 15
            
            # Título del cronograma
            titulo = scene.addText("📅 Cronograma de Fases del Proyecto", QFont("Arial", 14, QFont.Bold))
            titulo.setPos(x_start, 0)
            
            # Línea principal del timeline
            total_height = len(datos_fases) * fase_height
            main_line = scene.addLine(line_x, y_start + 40, line_x, y_start + total_height, 
                                    QPen(QColor("#BDBDBD"), 4))
            
            y_pos = y_start + 50
            
            for fase_key, fase_data in datos_fases.items():
                # Determinar estado de la fase
                generado = fase_data.get('generado')
                firmado = fase_data.get('firmado')
                nombre_fase = fase_data.get('nombre', fase_key)
                
                # Estados y colores
                if firmado:
                    color_circulo = QColor("#4CAF50")  # Verde
                    color_fondo = QColor("#E8F5E8")
                    icono_text = "✓"
                elif generado:
                    color_circulo = QColor("#FF9800")  # Naranja
                    color_fondo = QColor("#FFF3E0")
                    icono_text = "●"
                else:
                    color_circulo = QColor("#E0E0E0")  # Gris
                    color_fondo = QColor("#FAFAFA")
                    icono_text = "○"
                    
                    # Verificar si es la próxima fase
                    if not generado:
                        color_circulo = QColor("#2196F3")  # Azul para próxima fase
                        color_fondo = QColor("#E3F2FD")
                        icono_text = "▶"
                
                # Círculo del timeline
                circle = scene.addEllipse(line_x - 12, y_pos - 12, 24, 24, 
                                        QPen(QColor("white"), 3), QBrush(color_circulo))
                
                # Ícono en el círculo
                icono = scene.addText(icono_text, QFont("Arial", 10, QFont.Bold))
                icono.setDefaultTextColor(QColor("white"))
                icono.setPos(line_x - 6, y_pos - 10)
                
                # Caja de información de la fase
                rect_width = 400
                rect_height = 60
                info_rect = scene.addRect(line_x + 40, y_pos - 25, rect_width, rect_height,
                                        QPen(color_circulo, 2), QBrush(color_fondo))
                
                # Texto del nombre de la fase
                nombre_text = scene.addText(nombre_fase, QFont("Arial", 12, QFont.Bold))
                nombre_text.setPos(line_x + 50, y_pos - 20)
                
                # Información de fechas
                fecha_info = ""
                if generado:
                    fecha_info += f"Generado: {generado}"
                if firmado:
                    if fecha_info:
                        fecha_info += " | "
                    fecha_info += f"Firmado: {firmado}"
                if not fecha_info:
                    fecha_info = "Pendiente"
                
                fecha_text = scene.addText(fecha_info, QFont("Arial", 9))
                fecha_text.setDefaultTextColor(QColor("#666666"))
                fecha_text.setPos(line_x + 50, y_pos + 5)
                
                y_pos += fase_height
                
            # Ajustar el tamaño de la escena
            scene.setSceneRect(0, 0, x_start + 500, y_pos + 20)
            
        except Exception as e:
            logger.info(f"[IntegradorResumen] Error dibujando timeline: {e}")
    
    def _generar_cronograma_fases(self, nombre_contrato: str) -> str:
        """Generar cronograma visual de las fases del proyecto - versión HTML de respaldo"""
        try:
            html = """
            <div style="background: #F5F5F5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #1976D2; margin-top: 0;">📅 Cronograma de Fases del Proyecto (HTML)</h3>
            """
            
            # Obtener datos de fases
            if hasattr(self.main_window, 'controlador_fases'):
                datos_fases = self.main_window.controlador_fases.obtener_datos_fases_para_resumen(nombre_contrato)
                
                if datos_fases:
                    # Crear timeline visual
                    html += '<div style="position: relative; margin: 20px 0;">'
                    
                    # Línea principal del timeline
                    html += '''
                    <div style="
                        position: absolute; 
                        left: 30px; 
                        top: 10px; 
                        width: 4px; 
                        height: calc(100% - 20px); 
                        background: linear-gradient(to bottom, #E0E0E0, #BDBDBD); 
                        border-radius: 2px;
                        z-index: 1;">
                    </div>
                    '''
                    
                    fase_count = 0
                    total_fases = len(datos_fases)
                    
                    for fase_key, fase_data in datos_fases.items():
                        fase_count += 1
                        
                        # Determinar estado de la fase
                        generado = fase_data.get('generado')
                        firmado = fase_data.get('firmado')
                        nombre_fase = fase_data.get('nombre', fase_key)
                        
                        # Estados y colores
                        if firmado:
                            estado = "completada"
                            color_circulo = "#4CAF50"  # Verde
                            color_fondo = "#E8F5E8"
                            icono = "●"
                        elif generado:
                            estado = "generada"
                            color_circulo = "#FF9800"  # Naranja
                            color_fondo = "#FFF3E0"
                            icono = "●"
                        else:
                            estado = "pendiente"
                            color_circulo = "#E0E0E0"  # Gris
                            color_fondo = "#FAFAFA"
                            icono = "○"
                        
                        # Determinar si es la siguiente fase a realizar
                        es_proxima = not generado and estado == "pendiente"
                        if es_proxima:
                            color_circulo = "#2196F3"  # Azul para próxima fase
                            color_fondo = "#E3F2FD"
                            icono = "●"
                        
                        # Generar item del timeline
                        html += f'''
                        <div style="position: relative; margin-bottom: 25px; padding-left: 70px; min-height: 50px;">
                            <!-- Círculo del timeline -->
                            <div style="
                                position: absolute; 
                                left: 18px; 
                                top: 8px; 
                                width: 28px; 
                                height: 28px; 
                                background: {color_circulo}; 
                                border-radius: 50%; 
                                display: flex; 
                                align-items: center; 
                                justify-content: center; 
                                color: white; 
                                font-size: 16px; 
                                font-weight: bold;
                                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                                z-index: 2;
                                border: 3px solid white;">
                                {icono}
                            </div>
                            
                            <!-- Contenido de la fase -->
                            <div style="
                                background: {color_fondo}; 
                                padding: 12px 15px; 
                                border-radius: 8px; 
                                border-left: 4px solid {color_circulo};
                                box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <h4 style="margin: 0; color: #333; font-size: 14px;">
                                        {nombre_fase}
                                    </h4>
                                    <span style="
                                        background: {color_circulo}; 
                                        color: white; 
                                        padding: 2px 8px; 
                                        border-radius: 12px; 
                                        font-size: 11px; 
                                        text-transform: uppercase; 
                                        font-weight: bold;">
                                        {estado.replace('_', ' ')}
                                    </span>
                                </div>
                                
                                <div style="font-size: 12px; color: #666;">
                        '''
                        
                        # Información de fechas
                        if generado:
                            html += f'Generado: {generado}<br>'
                        if firmado:
                            html += f'Firmado: {firmado}<br>'
                        
                        # Documentos relacionados
                        docs_relacionados = fase_data.get('documentos_relacionados', [])
                        if docs_relacionados:
                            docs_str = ', '.join(docs_relacionados)
                            html += f'Documentos: {docs_str}'
                        
                        if not generado and not firmado:
                            if es_proxima:
                                html += '<strong>Proxima fase a realizar</strong>'
                            else:
                                html += '<strong>Pendiente</strong>'
                        
                        html += '''
                                </div>
                            </div>
                        </div>
                        '''
                    
                    html += '</div>'  # Cerrar timeline
                    
                    # Resumen de progreso
                    fases_generadas = sum(1 for fase_data in datos_fases.values() if fase_data.get('generado'))
                    fases_firmadas = sum(1 for fase_data in datos_fases.values() if fase_data.get('firmado'))
                    progreso_generado = (fases_generadas / total_fases) * 100 if total_fases > 0 else 0
                    progreso_firmado = (fases_firmadas / total_fases) * 100 if total_fases > 0 else 0
                    
                    html += f'''
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <h4 style="color: #1976D2; margin-top: 0;">Progreso General</h4>
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-size: 13px; color: #666;">Documentos Generados</span>
                                <span style="font-size: 13px; font-weight: bold;">{fases_generadas}/{total_fases} ({progreso_generado:.0f}%)</span>
                            </div>
                            <div style="background: #E0E0E0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #FF9800; height: 100%; width: {progreso_generado}%; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-size: 13px; color: #666;">Documentos Firmados</span>
                                <span style="font-size: 13px; font-weight: bold;">{fases_firmadas}/{total_fases} ({progreso_firmado:.0f}%)</span>
                            </div>
                            <div style="background: #E0E0E0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #4CAF50; height: 100%; width: {progreso_firmado}%; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                    </div>
                    '''
                    
                else:
                    html += "<div style='color: #666; text-align: center; font-style: italic; padding: 20px;'>No hay datos de fases disponibles</div>"
            else:
                html += "<div style='color: #666; text-align: center; font-style: italic; padding: 20px;'>Controlador de fases no disponible</div>"
                
            html += "</div>"
            return html
            
        except Exception as e:
            logger.info(f"[IntegradorResumen] Error generando cronograma: {e}")
            return f"""
            <div style="background: #FFEBEE; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #D32F2F; margin-top: 0;">Error en Cronograma</h3>
                <p style="color: #666;">No se pudo generar el cronograma de fases: {str(e)}</p>
            </div>
            """
            # Fallback al resumen anterior
            return self._generar_resumen_visualizacion(nombre_contrato, datos_contrato)
    
    
    def _actualizar_estado_boton_generar(self, texto: str):
        """Actualizar texto del botón generar"""
        btn_generar = self.main_window.findChild(QPushButton, 'btn_generar_fichero_resumen')
        if btn_generar:
            btn_generar.setText(texto)
    
    def _mostrar_mensaje_exito(self, mensaje: str):
        """Mostrar mensaje de éxito"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self.main_window, "✅ Éxito", mensaje)
        except:
            logger.info(f"[IntegradorResumen] {mensaje}")
    
    def _mostrar_mensaje_error(self, mensaje: str):
        """Mostrar mensaje de error"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self.main_window, "❌ Error", mensaje)
        except:
            logger.error(f"[IntegradorResumen] {mensaje}")
    
    def _obtener_datos_contrato_completos(self, nombre_contrato: str) -> dict:
        """Obtener datos completos del contrato desde la estructura JSON real"""
        try:
            # Primero intentar con el método estándar
            datos_estandar = {}
            if hasattr(self.main_window, 'contract_manager'):
                try:
                    datos_estandar = self.main_window.contract_manager.get_current_contract_data() or {}
                except:
                    pass
            
            # Si tenemos datos estándar y están completos, usarlos
            if datos_estandar and datos_estandar.get('nombreObra'):
                return self._mapear_datos_a_formato_estandar(datos_estandar)
            
            # Sino, intentar cargar desde BaseDatos.json directamente
            import json
            base_datos_path = os.path.join(os.getcwd(), "BaseDatos.json")
            
            if os.path.exists(base_datos_path):
                with open(base_datos_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Buscar el contrato en el array de obras
                obras = data.get('obras', [])
                contrato_encontrado = None
                
                for obra in obras:
                    if obra.get('nombreObra') == nombre_contrato or obra.get('comboBox') == nombre_contrato:
                        contrato_encontrado = obra
                        break
                
                if contrato_encontrado:
                    # Mapear a formato estándar para el detector
                    return self._mapear_datos_a_formato_estandar(contrato_encontrado)
            
            return {}
            
        except Exception as e:
            logger.info(f"[IntegradorResumen] Error obteniendo datos del contrato: {e}")
            return {}
    
    def _mapear_datos_a_formato_estandar(self, datos_originales: dict) -> dict:
        """Mapear datos desde la estructura real a formato estándar"""
        try:
            # Mapeo de campos desde tu estructura a los esperados por el detector
            mapeo_campos = {
                # Campos básicos
                'nombreObra': datos_originales.get('nombreObra', ''),
                'tipoContrato': datos_originales.get('tipoActuacion', ''),  # Mapear tipoActuacion a tipoContrato
                'numeroExpediente': datos_originales.get('numeroExpediente', ''),
                'objetoContrato': datos_originales.get('objeto', ''),  # Mapear objeto a objetoContrato
                'fechaCreacion': datos_originales.get('fechaCreacion', ''),
                
                # Importes - mapear desde tu estructura
                'importeLicitacion': self._convertir_a_numero(datos_originales.get('basePresupuesto', 0)),
                'importeIVA': self._convertir_a_numero(datos_originales.get('ivaPresupuestoBase', 0)),
                'importeTotal': self._convertir_a_numero(datos_originales.get('totalPresupuestoBase', 0)),
                
                # Empresa adjudicataria
                'empresaAdjudicataria': datos_originales.get('empresaAdjudicada', ''),
                
                # Fechas importantes
                'fechaAdjudicacion': datos_originales.get('fechaAdjudicacion', ''),
                'fechaInicio': datos_originales.get('fechaProyecto', ''),  # Mapear fechaProyecto a fechaInicio
                'fechaRecepcion': datos_originales.get('fechaRecepcion', ''),
                
                # Información adicional
                'plazoEjecucion': datos_originales.get('plazoEjecucion', ''),
                'organoContratacion': datos_originales.get('organoContratacion2', ''),
                'justificacion': datos_originales.get('justificacion', ''),
                'objeto': datos_originales.get('objeto', ''),
            }
            
            # Agregar empresas si están disponibles
            if 'empresas' in datos_originales and isinstance(datos_originales['empresas'], list):
                mapeo_campos['empresas'] = datos_originales['empresas']
            
            # Agregar todos los datos originales por si acaso
            mapeo_campos.update(datos_originales)
            
            return mapeo_campos
            
        except Exception as e:
            logger.info(f"[IntegradorResumen] Error mapeando datos: {e}")
            return datos_originales
    
    def _convertir_a_numero(self, valor) -> float:
        """Convertir valor a número float"""
        try:
            if isinstance(valor, (int, float)):
                return float(valor)
            if isinstance(valor, str):
                # Detectar formato: si hay punto Y coma, es formato español
                if '.' in valor and ',' in valor:
                    # Formato español: 12.500,75 -> punto = miles, coma = decimales
                    valor_limpio = valor.replace('.', '').replace(',', '.')
                    return float(valor_limpio)
                elif ',' in valor and valor.count(',') == 1:
                    # Solo coma: podría ser decimal español (12500,75)
                    valor_limpio = valor.replace(',', '.')
                    return float(valor_limpio)
                else:
                    # Formato estándar: 12500.75 (punto = decimal)
                    return float(valor)
            return 0.0
        except:
            return 0.0
    
    def notificar_documento_generado(self, tipo_str: str, nombre: str, ruta: str = ""):
        """Notificar que se generó un documento (desde controlador_documentos)"""
        # Widget eliminado, solo mantener funcionalidad básica
        pass
    
    def generar_fichero_resumen(self, nombre_contrato: str, datos_contrato: dict) -> str:
        """Generar fichero completo de resumen del contrato en formato Word - Delegado a ControladorDocumentos"""
        try:
            # Delegar la generación de documentos Word al controlador especializado
            if hasattr(self.main_window, 'controlador_documentos'):
                return self.main_window.controlador_documentos.generar_fichero_resumen(nombre_contrato, datos_contrato)
            else:
                raise Exception("Controlador de documentos no disponible")
        except Exception as e:
            error_msg = f"Error generando fichero: {e}"
            logger.error(f"[IntegradorResumen] {error_msg}")
            raise Exception(error_msg)
    
    # =================== FUNCIONES DE ESCANEO DE FIRMAS PDF ===================
    
    def _escanear_y_actualizar_tabla_firmas(self, nombre_contrato: str):
        """Escanear firmas digitales en PDFs y actualizar la tabla de seguimiento"""
        try:
            logger.debug(f"[IntegradorResumen] Iniciando escaneo de firmas para: {nombre_contrato}")
            
            # 1. Obtener ruta base de obras
            if hasattr(self.main_window, 'controlador_routes'):
                logger.info(f"[IntegradorResumen] Usando controlador_routes para obtener ruta obras")
                obras_path = self.main_window.controlador_routes.get_ruta_carpeta_obras()
                logger.info(f"[IntegradorResumen] 📂 Ruta obras: {obras_path}")
            else:
                logger.warning(f"[IntegradorResumen] Fallback: controlador_routes no disponible")
                # Fallback usando ruta relativa
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                obras_path = os.path.join(current_dir, "obras")
                logger.info(f"[IntegradorResumen] 📂 Ruta obras (fallback): {obras_path}")
            
            # 2. Obtener ruta de la carpeta 02-documentacion-finales
            carpeta_documentos = self._obtener_carpeta_documentacion_finales(nombre_contrato)
            if not carpeta_documentos or not os.path.exists(carpeta_documentos):
                logger.warning(f"[IntegradorResumen] No se encontró carpeta 02-documentacion-finales para {nombre_contrato}")
                return
            
            logger.info(f"[IntegradorResumen] 📂 Escaneando carpeta: {carpeta_documentos}")
            
            # 3. Mapear archivos PDF a fases
            mapeo_fases = self._crear_mapeo_archivos_pdf_fases()
            
            # 4. Escanear archivos PDF y extraer firmas
            datos_firmas = {}
            todas_firmas = []  # Para ordenamiento cronológico
            
            # Buscar archivos PDF en 02-documentacion-finales
            archivos_pdf_encontrados = [f for f in os.listdir(carpeta_documentos) if f.lower().endswith('.pdf')]
            logger.debug(f"[IntegradorResumen] Archivos PDF encontrados en 02-documentacion-finales: {archivos_pdf_encontrados}")
            
            # Buscar documento de CREACION en 01-proyecto (excepción especial)
            nombre_carpeta_real = self._obtener_nombre_carpeta_actual(nombre_contrato)
            carpeta_proyecto = os.path.join(obras_path, nombre_carpeta_real, "01-proyecto")
            if os.path.exists(carpeta_proyecto):
                archivos_proyecto = [f for f in os.listdir(carpeta_proyecto) if f.lower().endswith('.pdf') and 'proyecto' in f.lower()]
                if archivos_proyecto:
                    logger.debug(f"[IntegradorResumen] Archivos proyecto encontrados en 01-proyecto: {archivos_proyecto}")
                    # Añadir a la lista con ruta especial para procesamiento posterior
                    for archivo in archivos_proyecto:
                        archivos_pdf_encontrados.append(f"01-proyecto/{archivo}")
            
            for archivo_pdf in archivos_pdf_encontrados:
                logger.debug(f"[IntegradorResumen] Analizando archivo: {archivo_pdf}")
                
                # Manejar rutas especiales para documentos de 01-proyecto
                if archivo_pdf.startswith("01-proyecto/"):
                    nombre_archivo_real = archivo_pdf.replace("01-proyecto/", "")
                    ruta_pdf = os.path.join(obras_path, nombre_carpeta_real, archivo_pdf)
                    fase = 'CREACION'  # Los documentos de proyecto se mapean a fase CREACION
                else:
                    nombre_archivo_real = archivo_pdf
                    ruta_pdf = os.path.join(carpeta_documentos, archivo_pdf)
                    fase = self._determinar_fase_por_archivo(archivo_pdf, mapeo_fases)
                
                logger.info(f"[IntegradorResumen] 📋 Archivo {archivo_pdf} -> Fase determinada: {fase}")
                
                if fase:
                    logger.debug(f"[IntegradorResumen] Procesando {archivo_pdf} -> Fase: {fase}")
                    
                    # Extraer firmas usando la función existente
                    firmas = self._extraer_firmas_pdf(ruta_pdf)
                    logger.debug(f"[IntegradorResumen] Firmas extraídas de {archivo_pdf}: {len(firmas) if firmas else 0}")
                    
                    if firmas:
                        logger.info(f"[IntegradorResumen] 📝 Firmas encontradas: {firmas}")
                        datos_firmas[fase] = {
                            'archivo': nombre_archivo_real,
                            'fecha_creacion': self._obtener_fecha_creacion_archivo(ruta_pdf),
                            'firmas': firmas
                        }
                        
                        # Recopilar todas las firmas para ordenamiento cronológico
                        todas_firmas.extend(firmas)
                        
                        logger.info(f"[IntegradorResumen] Encontradas {len(firmas)} firmas en {archivo_pdf}")
                    else:
                        # Agregar fase sin firmas pero con documento
                        datos_firmas[fase] = {
                            'archivo': nombre_archivo_real,
                            'fecha_creacion': self._obtener_fecha_creacion_archivo(ruta_pdf),
                            'firmas': []  # Lista vacía para documentos sin firmas
                        }
                        logger.debug(f"[IntegradorResumen] Documento sin firmas agregado: {archivo_pdf} -> Fase: {fase}")
                else:
                    logger.warning(f"[IntegradorResumen] No se pudo determinar fase para {archivo_pdf}")
            
            # Ordenar firmantes cronológicamente por fecha de primera firma
            firmantes_con_fechas = {}
            for firma in todas_firmas:
                firmante = firma['firmante']
                fecha = firma['fecha']
                if firmante not in firmantes_con_fechas or fecha < firmantes_con_fechas[firmante]:
                    firmantes_con_fechas[firmante] = fecha
            
            # Crear lista ordenada cronológicamente
            firmantes_ordenados = sorted(firmantes_con_fechas.items(), key=lambda x: x[1])
            firmantes_unicos = [firmante for firmante, fecha in firmantes_ordenados]
            
            logger.info(f"[IntegradorResumen] Resumen final: {len(datos_firmas)} fases con firmas, {len(firmantes_unicos)} firmantes únicos")
            logger.info(f"[IntegradorResumen] Datos de firmas: {datos_firmas}")
            logger.info(f"[IntegradorResumen] Firmantes únicos: {firmantes_unicos}")
            
            # Guardar en cache para uso posterior (generación de documentos)
            self._datos_firmas_cache = datos_firmas
            self._firmantes_unicos_cache = firmantes_unicos
            
            # 5. Actualizar tabla de seguimiento
            self._actualizar_tabla_seguimiento(datos_firmas, firmantes_unicos, nombre_contrato)
            
            logger.info(f"[IntegradorResumen] Escaneo completado. {len(datos_firmas)} fases con firmas encontradas")
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error en escaneo de firmas: {e}")
            import traceback
            logger.exception("Error completo:")
    
    def _obtener_carpeta_documentacion_finales(self, nombre_contrato: str) -> str:
        """Obtener la ruta de la carpeta 02-documentacion-finales para un contrato"""
        try:
            # Obtener ruta base de obras
            if hasattr(self.main_window, 'controlador_routes'):
                logger.info(f"[IntegradorResumen] Usando controlador_routes para obtener ruta obras")
                obras_path = self.main_window.controlador_routes.get_ruta_carpeta_obras()
                logger.info(f"[IntegradorResumen] 📂 Ruta obras: {obras_path}")
            else:
                logger.warning(f"[IntegradorResumen] Fallback: controlador_routes no disponible")
                # Fallback usando ruta relativa
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                obras_path = os.path.join(current_dir, "obras")
                logger.info(f"[IntegradorResumen] 📂 Ruta obras (fallback): {obras_path}")
            
            # Construcción directa de la ruta: obras/nombre_carpeta_real/02-documentacion-finales
            nombre_carpeta_real = self._obtener_nombre_carpeta_actual(nombre_contrato)
            documentacion_path = os.path.join(obras_path, nombre_carpeta_real, "02-documentacion-finales")
            
            if os.path.exists(documentacion_path):
                logger.info(f"[IntegradorResumen] Carpeta documentación encontrada: {documentacion_path}")
                return documentacion_path
            else:
                logger.warning(f"[IntegradorResumen] No se encontró carpeta 02-documentacion-finales para {nombre_contrato}")
                logger.info(f"[IntegradorResumen] 📂 Ruta esperada: {documentacion_path}")
                return ""
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error obteniendo carpeta documentación: {e}")
            return ""
    
    def _obtener_carpeta_proyecto(self, nombre_contrato: str) -> str:
        """Obtener la ruta de la carpeta 01-proyecto para un contrato"""
        try:
            # Obtener ruta base de obras
            if hasattr(self.main_window, 'controlador_routes'):
                logger.info(f"[IntegradorResumen] Usando controlador_routes para obtener ruta obras")
                obras_path = self.main_window.controlador_routes.get_ruta_carpeta_obras()
                logger.info(f"[IntegradorResumen] 📂 Ruta obras: {obras_path}")
            else:
                logger.warning(f"[IntegradorResumen] Fallback: controlador_routes no disponible")
                # Fallback usando ruta relativa
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                obras_path = os.path.join(current_dir, "obras")
                logger.info(f"[IntegradorResumen] 📂 Ruta obras (fallback): {obras_path}")
            
            # Construcción directa de la ruta: obras/nombre_carpeta_real/01-proyecto
            nombre_carpeta_real = self._obtener_nombre_carpeta_actual(nombre_contrato)
            proyecto_path = os.path.join(obras_path, nombre_carpeta_real, "01-proyecto")
            
            if os.path.exists(proyecto_path):
                logger.info(f"[IntegradorResumen] Carpeta proyecto encontrada: {proyecto_path}")
                return proyecto_path
            else:
                logger.warning(f"[IntegradorResumen] No se encontró carpeta 01-proyecto para {nombre_contrato}")
                logger.info(f"[IntegradorResumen] 📂 Ruta esperada: {proyecto_path}")
                return ""
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error obteniendo carpeta proyecto: {e}")
            return ""
    
    def _obtener_fecha_documento_creacion(self, nombre_contrato: str, fase: str) -> str:
        """Obtener fecha de documento de creación en 01-proyecto (para fase CREACION)"""
        try:
            if fase != 'CREACION':
                return ""
                
            # Obtener ruta base de obras
            if hasattr(self.main_window, 'controlador_routes'):
                obras_path = self.main_window.controlador_routes.get_ruta_carpeta_obras()
            else:
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                obras_path = os.path.join(current_dir, "obras")
            
            # Construir ruta a 01-proyecto
            nombre_carpeta_real = self._obtener_nombre_carpeta_actual(nombre_contrato)
            carpeta_proyecto = os.path.join(obras_path, nombre_carpeta_real, "01-proyecto")
            
            if not os.path.exists(carpeta_proyecto):
                return ""
            
            # Buscar archivos con "proyecto" en el nombre
            archivos_encontrados = []
            for archivo in os.listdir(carpeta_proyecto):
                if "proyecto" in archivo.lower():
                    ruta_completa = os.path.join(carpeta_proyecto, archivo)
                    fecha_modificacion = os.path.getmtime(ruta_completa)
                    archivos_encontrados.append((archivo, fecha_modificacion))
            
            if not archivos_encontrados:
                return ""
            
            # Obtener el archivo más reciente
            archivo_mas_reciente = max(archivos_encontrados, key=lambda x: x[1])
            fecha_timestamp = archivo_mas_reciente[1]
            
            # Convertir timestamp a fecha legible - SOLO LA FECHA
            from datetime import datetime
            fecha_obj = datetime.fromtimestamp(fecha_timestamp)
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M")
            
            # Devolver solo la fecha
            return fecha_formateada
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error obteniendo fecha documento creación: {e}")
            return ""

    def _obtener_fecha_documento_generado(self, nombre_contrato: str, fase: str) -> str:
        """Obtener fecha del último documento generado para una fase en 04-documentos-sin-firmar"""
        try:
            # Obtener ruta base de obras
            if hasattr(self.main_window, 'controlador_routes'):
                obras_path = self.main_window.controlador_routes.get_ruta_carpeta_obras()
            else:
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                obras_path = os.path.join(current_dir, "obras")
            
            # Construir ruta a 04-documentos-sin-firmar
            nombre_carpeta_real = self._obtener_nombre_carpeta_actual(nombre_contrato)
            carpeta_docs_sin_firmar = os.path.join(obras_path, nombre_carpeta_real, "04-documentos-sin-firmar")
            
            if not os.path.exists(carpeta_docs_sin_firmar):
                return ""
            
            # Crear mapeo de fases a nombres de archivo típicos
            nombres_archivo_por_fase = {
                'CREACION': ['proyecto', 'creacion'],
                'INICIO': ['inicio', 'acta_inicio', 'inicio_contrato'],
                'CARTAS': ['cartas', 'invitacion', 'carta'],
                'ADJUDICACION': ['adjudicacion', 'adjudicar', 'acta_adjudicacion'],
                'CONTRATO': ['contrato'],
                'REPLANTEO': ['replanteo', 'acta_replanteo'],
                'ACTUACION': ['actuacion', 'actuaciones'],
                'RECEPCION': ['recepcion', 'acta_recepcion'],
                'FINALIZACION': ['finalizacion', 'final', 'acta_finalizacion', 'liquidacion']
            }
            
            nombres_buscar = nombres_archivo_por_fase.get(fase, [])
            if not nombres_buscar:
                return ""
            
            # Buscar archivos PDF que coincidan
            archivos_encontrados = []
            for archivo in os.listdir(carpeta_docs_sin_firmar):
                if archivo.lower().endswith('.pdf'):
                    nombre_lower = archivo.lower()
                    for nombre_buscar in nombres_buscar:
                        if nombre_buscar in nombre_lower:
                            ruta_completa = os.path.join(carpeta_docs_sin_firmar, archivo)
                            fecha_modificacion = os.path.getmtime(ruta_completa)
                            archivos_encontrados.append((archivo, fecha_modificacion))
                            break
            
            if not archivos_encontrados:
                return ""
            
            # Obtener el archivo más reciente
            archivo_mas_reciente = max(archivos_encontrados, key=lambda x: x[1])
            nombre_archivo = archivo_mas_reciente[0]
            fecha_timestamp = archivo_mas_reciente[1]
            
            # Convertir timestamp a fecha legible
            from datetime import datetime
            fecha_obj = datetime.fromtimestamp(fecha_timestamp)
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M")
            
            # Devolver nombre del archivo y fecha
            return f"{nombre_archivo}\n{fecha_formateada}"
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error obteniendo fecha documento generado: {e}")
            return ""
    
    def _crear_mapeo_archivos_pdf_fases(self) -> dict:
        """Crear mapeo de nombres de archivos PDF a fases del proyecto"""
        return {
            'CREACION': ['proyecto', 'creacion'],
            'INICIO': ['inicio', 'acta_inicio', 'inicio_contrato'],
            'CARTASINVITACION': ['cartas_invitacion', 'invitacion', 'carta_invitacion'],
            'ADJUDICACION': ['adjudicacion', 'adjudicar'],
            'CARTASADJUDICACION': ['cartas_adjudicacion', 'carta_adjudicacion'],
            'CONTRATO': ['contrato'],
            'REPLANTEO': ['replanteo', 'acta_replanteo'],
            'ACTUACION': ['actuacion', 'actuaciones'],
            'RECEPCION': ['recepcion', 'acta_recepcion'],
            'FINALIZACION': ['finalizacion', 'final', 'acta_finalizacion']
        }
    
    def _determinar_fase_por_archivo(self, nombre_archivo: str, mapeo_fases: dict) -> str:
        """Determinar la fase basándose en el nombre del archivo"""
        nombre_lower = nombre_archivo.lower()
        logger.debug(f"[IntegradorResumen] Determinando fase para archivo: '{nombre_archivo}' -> '{nombre_lower}'")
        
        for fase, palabras_clave in mapeo_fases.items():
            for palabra in palabras_clave:
                if palabra in nombre_lower:
                    logger.info(f"[IntegradorResumen] Coincidencia encontrada: '{palabra}' en '{nombre_lower}' -> Fase: {fase}")
                    return fase
        
        logger.warning(f"[IntegradorResumen] No se encontró fase para archivo: {nombre_archivo}")
        return None
    
    def _extraer_firmas_pdf(self, ruta_pdf: str) -> list:
        """Extraer firmas digitales de un PDF usando la función existente"""
        try:
            logger.debug(f"[IntegradorResumen] Intentando extraer firmas de: {ruta_pdf}")
            
            # Verificar que el archivo existe
            if not os.path.exists(ruta_pdf):
                logger.error(f"[IntegradorResumen] Archivo no existe: {ruta_pdf}")
                return []
            
            logger.info(f"[IntegradorResumen] Archivo existe, tamaño: {os.path.getsize(ruta_pdf)} bytes")
            
            # Importar y usar la función existente de firmas.py
            import sys
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, current_dir)
            
            logger.info(f"[IntegradorResumen] 📂 Buscando firmas.py en: {current_dir}")
            
            from firmas import obtener_firmas_pdf
            logger.info(f"[IntegradorResumen] Función obtener_firmas_pdf importada correctamente")
            
            firmas = obtener_firmas_pdf(ruta_pdf)
            logger.debug(f"[IntegradorResumen] Resultado de obtener_firmas_pdf: {firmas}")
            
            return firmas
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error extrayendo firmas de {ruta_pdf}: {e}")
            import traceback
            logger.exception("Error completo:")
            return []
    
    def _obtener_fecha_creacion_archivo(self, ruta_archivo: str) -> str:
        """Obtener fecha de creación del archivo"""
        try:
            timestamp = os.path.getctime(ruta_archivo)
            fecha = datetime.datetime.fromtimestamp(timestamp)
            return fecha.strftime("%d/%m/%Y %H:%M")
        except:
            return "Fecha no disponible"
    
    def _actualizar_tabla_seguimiento(self, datos_firmas: dict, firmantes_unicos: list, nombre_contrato: str = None):
        """Actualizar la tabla QTableWidget Tabla_seguimiento con los datos de firmas"""
        try:
            # Obtener nombre del contrato si no se proporciona
            if not nombre_contrato:
                if hasattr(self.main_window, 'proyecto') and hasattr(self.main_window.proyecto, 'datos_contrato'):
                    nombre_contrato = self.main_window.proyecto.datos_contrato.nombre
                else:
                    nombre_contrato = "proyecto"  # Fallback
            
            logger.debug(f"[IntegradorResumen] Buscando tabla Tabla_seguimiento en {type(self.main_window)}")
            logger.info(f"[IntegradorResumen] Datos recibidos - {len(datos_firmas)} fases, {len(firmantes_unicos)} firmantes")
            
            # Buscar la tabla en la interfaz
            tabla_seguimiento = self.main_window.findChild(QTableWidget, 'Tabla_seguimiento')
            
            logger.debug(f"[IntegradorResumen] Tabla encontrada: {tabla_seguimiento is not None}")
            if tabla_seguimiento:
                logger.info(f"[IntegradorResumen] Tabla actual - Filas: {tabla_seguimiento.rowCount()}, Columnas: {tabla_seguimiento.columnCount()}")
            
            if not tabla_seguimiento:
                logger.info("[IntegradorResumen] ⚠️ No se encontró QTableWidget 'Tabla_seguimiento'")
                # Buscar todas las tablas disponibles para debug
                all_tables = self.main_window.findChildren(QTableWidget)
                logger.debug(f"[IntegradorResumen] Tablas disponibles: {[t.objectName() for t in all_tables]}")
                return
            
            # Si no hay datos reales, mostrar información sobre el estado
            if not datos_firmas:
                logger.warning(f"[IntegradorResumen] No se encontraron datos de firmas - mostrando tabla vacía")
                self._mostrar_tabla_sin_firmas(tabla_seguimiento)
                return
            
            logger.info(f"[IntegradorResumen] Actualizando tabla con {len(datos_firmas)} fases y {len(firmantes_unicos)} firmantes")
            
            # Configurar columnas: Fase, Fecha Creación, Documento Generado, + una columna por cada firmante
            total_columnas = 3 + len(firmantes_unicos)  # Fase + Fecha + Documento Generado + firmantes
            tabla_seguimiento.setColumnCount(total_columnas)
            
            # Configurar headers - nueva estructura
            headers_firmantes = [f'Firmante{i+1}' for i in range(len(firmantes_unicos))]
            headers = ['Fase', 'Creación Doc', 'Fecha Última Firma'] + headers_firmantes
            tabla_seguimiento.setHorizontalHeaderLabels(headers)
            
            # Determinar fases según tipo de contrato
            tipo_actuacion = ''
            if (self.main_window and 
                hasattr(self.main_window, 'contract_manager') and 
                self.main_window.contract_manager):
                
                contract_data = self.main_window.contract_manager.get_current_contract_data()
                if contract_data:
                    tipo_actuacion = contract_data.get('tipoActuacion', '')
            
            # Definir fases base
            todas_fases = ['CREACION', 'INICIO', 'CARTASINVITACION', 'ADJUDICACION', 'CARTASADJUDICACION', 'CONTRATO', 'ACTUACION', 'FINALIZACION']
            
            # Añadir REPLANTEO y RECEPCION solo para obras
            if tipo_actuacion in ['obras', 'obra_mantenimiento']:
                # Insertar en posiciones correctas
                todas_fases.insert(-2, 'REPLANTEO')  # Antes de ACTUACION
                todas_fases.insert(-1, 'RECEPCION')  # Antes de FINALIZACION
            
            # Configurar filas
            tabla_seguimiento.setRowCount(len(todas_fases))
            
            # Llenar datos
            for fila, fase in enumerate(todas_fases):
                # Columna Fase
                item_fase = QTableWidgetItem(fase)
                tabla_seguimiento.setItem(fila, 0, item_fase)
                
                if fase in datos_firmas:
                    # Fase con datos
                    info_fase = datos_firmas[fase]
                    
                    # Columna 1: Creación Doc - usar fecha_creacion de los datos
                    fecha_creacion_archivo = info_fase.get('fecha_creacion', '')
                    item_creacion = QTableWidgetItem(fecha_creacion_archivo if fecha_creacion_archivo else "Sin datos")
                    if fecha_creacion_archivo:
                        if fase == 'CREACION':
                            item_creacion.setBackground(QColor(200, 255, 255))  # Azul claro para creación
                        else:
                            item_creacion.setBackground(QColor(255, 255, 200))  # Amarillo para otros documentos
                    else:
                        item_creacion.setBackground(QColor(255, 200, 200))  # Rojo claro para sin datos
                    tabla_seguimiento.setItem(fila, 1, item_creacion)
                    
                    # Columna 2: Fecha Última Firma (para todas las fases)
                    if info_fase['firmas']:
                        # Obtener la fecha más reciente de las firmas
                        fechas_firmas = []
                        for firma in info_fase['firmas']:
                            if 'fecha' in firma:
                                fechas_firmas.append(firma['fecha'])
                        if fechas_firmas:
                            fecha_ultima = max(fechas_firmas)
                            item_fecha_ultima = QTableWidgetItem(fecha_ultima)
                            item_fecha_ultima.setBackground(QColor(200, 255, 200))  # Verde claro
                            tabla_seguimiento.setItem(fila, 2, item_fecha_ultima)
                        else:
                            tabla_seguimiento.setItem(fila, 2, QTableWidgetItem(""))
                    else:
                        tabla_seguimiento.setItem(fila, 2, QTableWidgetItem(""))
                    
                    # Columnas de firmantes (ahora empiezan en columna 3)
                    for col, firmante in enumerate(firmantes_unicos, 3):
                        # Buscar si este firmante firmó esta fase
                        firma_encontrada = None
                        for firma in info_fase['firmas']:
                            if firma['firmante'] == firmante:
                                firma_encontrada = firma
                                break
                        
                        if firma_encontrada:
                            dni_texto = f" - {firma_encontrada['dni']}" if 'dni' in firma_encontrada and firma_encontrada['dni'] else ""
                            texto_celda = f"{firmante}{dni_texto}\n{firma_encontrada['fecha']}"
                            item_firmante = QTableWidgetItem(texto_celda)
                            item_firmante.setBackground(QColor(200, 255, 200))  # Verde claro
                        else:
                            item_firmante = QTableWidgetItem("")
                        
                        tabla_seguimiento.setItem(fila, col, item_firmante)
                else:
                    # Fase sin datos de firmas
                    # Columna 1: Creación Doc
                    if fase == 'CREACION':
                        fecha_creacion_doc = self._obtener_fecha_documento_creacion(nombre_contrato, fase)
                        item_creacion = QTableWidgetItem(fecha_creacion_doc if fecha_creacion_doc else "Sin datos")
                        if not fecha_creacion_doc:
                            item_creacion.setBackground(QColor(255, 200, 200))  # Rojo claro
                        else:
                            item_creacion.setBackground(QColor(200, 255, 255))  # Azul claro
                        tabla_seguimiento.setItem(fila, 1, item_creacion)
                    else:
                        fecha_doc_generado = self._obtener_fecha_documento_generado(nombre_contrato, fase)
                        item_doc_generado = QTableWidgetItem(fecha_doc_generado if fecha_doc_generado else "Sin datos")
                        if not fecha_doc_generado:
                            item_doc_generado.setBackground(QColor(255, 200, 200))  # Rojo claro
                        else:
                            item_doc_generado.setBackground(QColor(255, 255, 200))  # Amarillo claro
                        tabla_seguimiento.setItem(fila, 1, item_doc_generado)
                    
                    # Columna 2: Fecha Última Firma (vacía para fases sin datos)
                    tabla_seguimiento.setItem(fila, 2, QTableWidgetItem(""))
                    
                    # Columnas de firmantes vacías (empiezan en columna 3)
                    for col in range(3, total_columnas):
                        item_vacio = QTableWidgetItem("")
                        item_vacio.setBackground(QColor(240, 240, 240))  # Gris claro
                        tabla_seguimiento.setItem(fila, col, item_vacio)
            
            # Ajustar tamaño de columnas
            tabla_seguimiento.resizeColumnsToContents()
            
            # Conectar evento de clic para abrir PDFs
            try:
                # Desconectar conexiones previas para evitar duplicados
                tabla_seguimiento.cellClicked.disconnect()
            except:
                pass
            # Conectar nueva función de clic
            tabla_seguimiento.cellClicked.connect(lambda row, col: self._on_tabla_seguimiento_clicked(row, col, nombre_contrato, datos_firmas))
            logger.info("[IntegradorResumen] ✅ Evento de clic en tabla conectado")
            
            # Forzar actualización de la interfaz
            tabla_seguimiento.update()
            tabla_seguimiento.repaint()
            
            # Verificar que los datos se guardaron
            logger.info(f"[IntegradorResumen] Tabla después del update - Filas: {tabla_seguimiento.rowCount()}, Columnas: {tabla_seguimiento.columnCount()}")
            logger.info("[IntegradorResumen] ✅ Tabla de seguimiento actualizada correctamente")
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error actualizando tabla seguimiento: {e}")
            import traceback
            logger.exception("Error completo:")
            
            # Método fallback: intentar actualización simple
            logger.info("[IntegradorResumen] 🔄 Intentando método fallback...")
            self._actualizar_tabla_seguimiento_fallback(datos_firmas, firmantes_unicos, nombre_contrato)
    
    def _actualizar_tabla_seguimiento_fallback(self, datos_firmas: dict, firmantes_unicos: list, nombre_contrato: str = None):
        """Método fallback más simple para actualizar la tabla"""
        try:
            # Obtener nombre del contrato si no se proporciona
            if not nombre_contrato:
                if hasattr(self.main_window, 'proyecto') and hasattr(self.main_window.proyecto, 'datos_contrato'):
                    nombre_contrato = self.main_window.proyecto.datos_contrato.nombre
                else:
                    nombre_contrato = "proyecto"  # Fallback
                    
            logger.info("[IntegradorResumen] 🔄 Método fallback para actualización tabla...")
            
            # Buscar tabla con método alternativo
            tabla = None
            if hasattr(self.main_window, 'Tabla_seguimiento'):
                tabla = self.main_window.Tabla_seguimiento
                logger.info("[IntegradorResumen] ✅ Tabla encontrada por atributo directo")
            else:
                # Buscar en todos los widgets
                for widget in self.main_window.findChildren(QTableWidget):
                    if widget.objectName() == 'Tabla_seguimiento':
                        tabla = widget
                        logger.info("[IntegradorResumen] ✅ Tabla encontrada por búsqueda")
                        break
            
            if not tabla:
                logger.info("[IntegradorResumen] ❌ Tabla no encontrada en fallback")
                return
            
            # Configuración más simple
            try:
                tabla.clear()
                tabla.setRowCount(11)  # 11 fases
                tabla.setColumnCount(3 + len(firmantes_unicos))
                
                # Headers básicos
                headers_firmantes_basicos = [f'Firmante{i+1}' for i in range(min(5, len(firmantes_unicos)))]
                headers = ['Fase', 'Creación Doc', 'Fecha Última Firma'] + headers_firmantes_basicos
                tabla.setHorizontalHeaderLabels(headers)
                
                # Llenar con datos básicos
                fases = ['CREACION', 'INICIO', 'CARTASINVITACION', 'ADJUDICACION', 'CARTASADJUDICACION', 'CONTRATO', 
                        'REPLANTEO', 'ACTUACION', 'RECEPCION', 'FINALIZACION']
                
                for i, fase in enumerate(fases):
                    tabla.setItem(i, 0, QTableWidgetItem(fase))
                    if fase in datos_firmas:
                        info_fase = datos_firmas[fase]
                        
                        # Columna 1: Creación Doc - usar fecha_creacion de los datos
                        fecha_creacion_archivo = info_fase.get('fecha_creacion', '')
                        item_creacion = QTableWidgetItem(fecha_creacion_archivo if fecha_creacion_archivo else "Sin datos")
                        if fecha_creacion_archivo:
                            if fase == 'CREACION':
                                item_creacion.setBackground(QColor(200, 255, 255))  # Azul claro para creación
                            else:
                                item_creacion.setBackground(QColor(255, 255, 200))  # Amarillo para otros documentos
                        else:
                            item_creacion.setBackground(QColor(255, 200, 200))  # Rojo claro para sin datos
                        tabla.setItem(i, 1, item_creacion)
                        
                        # Columna 2: Fecha Última Firma (para todas las fases)
                        if 'firmas' in info_fase and info_fase['firmas']:
                            # Obtener la fecha más reciente de las firmas
                            fechas_firmas = []
                            for firma in info_fase['firmas']:
                                if 'fecha' in firma:
                                    fechas_firmas.append(firma['fecha'])
                            if fechas_firmas:
                                fecha_ultima = max(fechas_firmas)
                                item_fecha_ultima = QTableWidgetItem(fecha_ultima)
                                item_fecha_ultima.setBackground(QColor(200, 255, 200))  # Verde claro
                                tabla.setItem(i, 2, item_fecha_ultima)
                            else:
                                tabla.setItem(i, 2, QTableWidgetItem(""))
                        else:
                            tabla.setItem(i, 2, QTableWidgetItem(""))
                        
                        # Llenar columnas de firmantes (ahora empiezan en columna 3)
                        for col, firmante in enumerate(firmantes_unicos, 3):  # Empezar en columna 3
                            if col >= 3 + len(firmantes_unicos):  # No exceder columnas disponibles
                                break
                                
                            # Buscar si este firmante firmó esta fase
                            firma_encontrada = None
                            if 'firmas' in info_fase:
                                for firma in info_fase['firmas']:
                                    if firma['firmante'] == firmante:
                                        firma_encontrada = firma
                                        break
                            
                            if firma_encontrada:
                                dni_texto = f" - {firma_encontrada['dni']}" if 'dni' in firma_encontrada and firma_encontrada['dni'] else ""
                                texto_celda = f"{firmante}{dni_texto}\n{firma_encontrada['fecha']}"
                                item_firmante = QTableWidgetItem(texto_celda)
                                item_firmante.setBackground(QColor(200, 255, 200))  # Verde claro
                                tabla.setItem(i, col, item_firmante)
                            else:
                                tabla.setItem(i, col, QTableWidgetItem(""))
                    else:
                        tabla.setItem(i, 1, QTableWidgetItem("Sin datos"))
                        tabla.setItem(i, 2, QTableWidgetItem(""))
                        # Llenar columnas de firmantes vacías para fases sin datos
                        for col in range(3, 3 + len(firmantes_unicos)):
                            if col < tabla.columnCount():
                                item_vacio = QTableWidgetItem("")
                                item_vacio.setBackground(QColor(240, 240, 240))  # Gris claro
                                tabla.setItem(i, col, item_vacio)
                
                tabla.resizeColumnsToContents()
                
                # Conectar evento de clic para abrir PDFs en método fallback
                try:
                    # Desconectar conexiones previas
                    tabla.cellClicked.disconnect()
                except:
                    pass
                # Conectar nueva función de clic
                tabla.cellClicked.connect(lambda row, col: self._on_tabla_seguimiento_clicked(row, col, nombre_contrato, datos_firmas))
                logger.info("[IntegradorResumen] ✅ Evento de clic conectado (fallback)")
                
                logger.info("[IntegradorResumen] ✅ Tabla actualizada con método fallback")
                
            except Exception as e2:
                logger.error(f"[IntegradorResumen] Error en configuración fallback: {e2}")
                
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error en método fallback: {e}")
    
    def _mostrar_tabla_sin_firmas(self, tabla: QTableWidget):
        """Mostrar tabla con información de estado cuando no hay firmas"""
        try:
            logger.info("[IntegradorResumen] 📊 Configurando tabla para mostrar estado sin firmas")
            
            # Configuración básica
            tabla.clear()
            tabla.setRowCount(11)  # 11 fases
            tabla.setColumnCount(4)  # Fase, Fecha Creación, Documento Generado, Estado
            tabla.setHorizontalHeaderLabels(['Fase', 'Fecha Creación', 'Documento Generado', 'Estado'])
            
            fases = ['CREACION', 'INICIO', 'CARTASINVITACION', 'ADJUDICACION', 'CARTASADJUDICACION', 'CONTRATO', 
                    'REPLANTEO', 'ACTUACION', 'RECEPCION', 'FINALIZACION']
            
            for i, fase in enumerate(fases):
                tabla.setItem(i, 0, QTableWidgetItem(fase))
                tabla.setItem(i, 1, QTableWidgetItem("Sin datos"))  # Fecha Creación
                tabla.setItem(i, 2, QTableWidgetItem(""))  # Documento Generado (vacío por ahora)
                tabla.setItem(i, 3, QTableWidgetItem("Sin PDFs"))
                
                # Color de fondo para indicar estado
                for j in range(4):
                    item = tabla.item(i, j)
                    if item:
                        item.setBackground(QColor(255, 255, 200))  # Amarillo claro
            
            tabla.resizeColumnsToContents()
            logger.info("[IntegradorResumen] ✅ Tabla configurada para estado sin firmas")
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error configurando tabla sin firmas: {e}")
    
    def _on_tabla_seguimiento_clicked(self, row: int, col: int, nombre_contrato: str, datos_firmas: Dict):
        """Manejador de clic en tabla de seguimiento - abre el PDF correspondiente"""
        try:
            # Mapear fila a fase
            fases = ['CREACION', 'INICIO', 'CARTASINVITACION', 'ADJUDICACION', 'CARTASADJUDICACION', 'CONTRATO', 
                    'REPLANTEO', 'ACTUACION', 'RECEPCION', 'FINALIZACION']
            
            if row >= len(fases):
                logger.error(f"[IntegradorResumen] Fila inválida: {row}")
                return
                
            fase_clickeada = fases[row]
            logger.info(f"[IntegradorResumen] 📋 Clic en fila {row}, fase: {fase_clickeada}")
            
            # Verificar si hay datos para esta fase
            if fase_clickeada not in datos_firmas:
                logger.warning(f"[IntegradorResumen] No hay datos para la fase: {fase_clickeada}")
                return
                
            info_fase = datos_firmas[fase_clickeada]
            nombre_archivo = info_fase.get('archivo')
            
            if not nombre_archivo:
                logger.warning(f"[IntegradorResumen] No hay archivo asociado a la fase: {fase_clickeada}")
                return
            
            # Determinar la carpeta correcta según la fase
            if fase_clickeada == 'CREACION':
                # CREACION busca en "01-proyecto"
                carpeta_docs = self._obtener_carpeta_proyecto(nombre_contrato)
            else:
                # Otras fases buscan en "02-documentacion-finales"
                carpeta_docs = self._obtener_carpeta_documentacion_finales(nombre_contrato)
            
            if not carpeta_docs or not os.path.exists(carpeta_docs):
                logger.error(f"[IntegradorResumen] No se encontró carpeta de documentos: {carpeta_docs}")
                return
                
            # Construir ruta completa del archivo
            ruta_pdf = os.path.join(carpeta_docs, nombre_archivo)
            
            if not os.path.exists(ruta_pdf):
                logger.error(f"[IntegradorResumen] Archivo no existe: {ruta_pdf}")
                return
            
            # Abrir el PDF
            logger.info(f"[IntegradorResumen] 📂 Abriendo PDF: {ruta_pdf}")
            
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(ruta_pdf)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', ruta_pdf])
            else:  # Linux
                subprocess.call(['xdg-open', ruta_pdf])
                
            logger.info(f"[IntegradorResumen] PDF abierto exitosamente: {nombre_archivo}")
            
        except Exception as e:
            logger.error(f"[IntegradorResumen] Error abriendo PDF: {e}")
            import traceback
            logger.exception("Error completo:")
    
    def test_escaneo_pdf_completo(self, nombre_contrato: str = None):
        """Test completo y detallado del escaneo de PDFs y extracción de firmas"""
        logger.debug("=" * 80)
        logger.debug("🔍 INICIANDO TEST COMPLETO DE ESCANEO PDF Y FIRMAS")
        logger.debug("=" * 80)
        
        try:
            # 1. Determinar contrato a usar
            if not nombre_contrato:
                if hasattr(self.main_window, 'comboBox'):
                    nombre_contrato = self.main_window.comboBox.currentText()
                    logger.info("📋 Contrato desde ComboBox: '{nombre_contrato}'")
                
                if not nombre_contrato or nombre_contrato == "Seleccionar contrato...":
                    nombre_contrato = "MANTENIMIENTO PREVENTIVO-CORRECTIVO DE CUBIERTAS"
                    logger.info("📋 Usando contrato por defecto: '{nombre_contrato}'")
            
            logger.info(f"🎯 CONTRATO OBJETIVO: {nombre_contrato}")
            logger.debug("-" * 80)
            
            # 2. Buscar carpeta de documentación
            logger.info("📂 PASO 1: Buscando carpeta de documentación...")
            carpeta_documentos = self._obtener_carpeta_documentacion_finales(nombre_contrato)
            logger.info(f"📂 Carpeta encontrada: {carpeta_documentos}")
            
            if not carpeta_documentos or not os.path.exists(carpeta_documentos):
                logger.error("❌ ERROR: No se encontró la carpeta de documentación")
                return
            
            # 3. Listar todos los archivos en la carpeta
            logger.debug("-" * 80)
            logger.info("📄 PASO 2: Listando archivos en la carpeta...")
            try:
                todos_archivos = os.listdir(carpeta_documentos)
                logger.info("📄 Total de archivos encontrados: {len(todos_archivos)}")
                for i, archivo in enumerate(todos_archivos, 1):
                    ruta_completa = os.path.join(carpeta_documentos, archivo)
                    tamaño = os.path.getsize(ruta_completa) if os.path.isfile(ruta_completa) else 0
                    tipo = "📄" if archivo.lower().endswith('.pdf') else "📝"
                    logger.info(f"  {i}. {tipo} {archivo} ({tamaño} bytes)")
                
                # Filtrar solo PDFs
                archivos_pdf = [f for f in todos_archivos if f.lower().endswith('.pdf')]
                logger.info(f"🔴 PDFs encontrados: {len(archivos_pdf)}")
                for pdf in archivos_pdf:
                    logger.info(f"  • {pdf}")
                    
            except Exception as e:
                logger.error("❌ Error listando archivos: {e}")
                return
            
            # 4. Probar mapeo de fases
            logger.debug("-" * 80)
            logger.info("🗂️ PASO 3: Probando mapeo de archivos a fases...")
            mapeo_fases = self._crear_mapeo_archivos_pdf_fases()
            logger.info("🗂️ Mapeo de fases configurado:")
            for fase, palabras in mapeo_fases.items():
                logger.info(f"  {fase}: {palabras}")
            
            # 5. Analizar cada PDF individualmente
            logger.debug("-" * 80)
            logger.debug("🔍 PASO 4: Análisis individual de cada PDF...")
            
            for i, archivo_pdf in enumerate(archivos_pdf, 1):
                logger.info(f"\n📄 ANALIZANDO PDF {i}/{len(archivos_pdf)}: {archivo_pdf}")
                logger.debug("-" * 40)
                
                ruta_pdf = os.path.join(carpeta_documentos, archivo_pdf)
                
                # 4a. Verificar archivo
                if os.path.exists(ruta_pdf):
                    tamaño = os.path.getsize(ruta_pdf)
                    logger.info(f"  ✅ Archivo existe: {tamaño} bytes")
                else:
                    logger.info(f"  ❌ Archivo no existe!")
                    continue
                
                # 4b. Determinar fase
                fase = self._determinar_fase_por_archivo(archivo_pdf, mapeo_fases)
                logger.info(f"  🗂️ Fase determinada: {fase if fase else 'NINGUNA'}")
                
                # 4c. Intentar extraer firmas
                logger.info(f"  🔍 Intentando extraer firmas...")
                try:
                    firmas = self._extraer_firmas_pdf(ruta_pdf)
                    if firmas:
                        logger.info(f"  ✅ Firmas encontradas: {len(firmas)}")
                        for j, firma in enumerate(firmas, 1):
                            logger.info(f"    {j}. Firmante: {firma.get('firmante', 'Desconocido')}")
                            logger.info(f"       Fecha: {firma.get('fecha', 'Sin fecha')}")
                            if 'dni' in firma:
                                logger.info(f"       DNI: {firma['dni']}")
                    else:
                        logger.info(f"  ⚠️ No se encontraron firmas")
                        
                except Exception as e:
                    logger.info(f"  ❌ Error extrayendo firmas: {e}")
            
            # 6. Resumen final
            logger.debug("\n" + "=" * 80)
            logger.info("📊 RESUMEN FINAL DEL TEST")
            logger.debug("=" * 80)
            logger.info(f"📂 Carpeta analizada: {carpeta_documentos}")
            logger.info("📄 Total archivos: {len(todos_archivos)}")
            logger.info(f"🔴 PDFs encontrados: {len(archivos_pdf)}")
            logger.info("📋 Archivos PDF:")
            for pdf in archivos_pdf:
                logger.info(f"  • {pdf}")
            logger.debug("=" * 80)
                
        except Exception as e:
            logger.error("❌ ERROR GENERAL EN TEST: {e}")
            import traceback
            logger.exception("Error completo:")


# =================== FUNCIÓN PRINCIPAL DE INTEGRACIÓN ===================

def integrar_resumen_completo(main_window):
    """
    FUNCIÓN PRINCIPAL: Integrar resumen completo en la aplicación
    
    Uso en main_py.py o controlador_grafica.py:
    
    from controladores.controlador_resumen import integrar_resumen_completo
    
    # Después de inicializar la ventana principal:
    integrador = integrar_resumen_completo(self)
    """
    try:
        integrador = IntegradorResumen(main_window)
        
        if integrador.integrar_en_aplicacion():
            logger.info("🎉 RESUMEN INTEGRADO EXITOSAMENTE")
            logger.info("   ✅ Historial de documentos activado") 
            logger.info("   ✅ Tab 'Resumen' agregado a la interfaz")
            logger.info("   ✅ Actualización automática configurada")
            return integrador
        else:
            logger.error("❌ Error integrando el resumen")
            return None
            
    except Exception as e:
        logger.error("❌ Error crítico integrando resumen: {e}")
        return None


if __name__ == "__main__":
    logger.debug("=" * 60)
    logger.info("🚀 INTEGRADOR DE RESUMEN COMPLETO")
    logger.debug("=" * 60)
    logger.debug("")
    logger.info("📋 INCLUYE:")
    logger.info("   📄 Historial completo de documentos") 
    logger.info("   📊 Métricas en tiempo real")
    logger.info("   🔄 Actualización automática")
    logger.debug("")
    logger.info("📝 PARA USAR:")
    logger.info("   from controladores.controlador_resumen import integrar_resumen_completo")
    logger.info("   integrador = integrar_resumen_completo(self)")
    logger.debug("")
    logger.info("   # Para notificar documentos generados:")
    logger.info("   integrador.notificar_documento_generado('acta_inicio', 'Acta de Inicio', '/ruta/archivo.pdf')")
    logger.debug("=" * 60)