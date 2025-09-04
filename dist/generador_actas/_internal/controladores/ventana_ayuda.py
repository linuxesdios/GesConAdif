#!/usr/bin/env python3
"""
Sistema de Ayuda Integrado para Generador de Actas ADIF
Ventana completa de documentación y guías de uso
"""
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging

logger = logging.getLogger(__name__)

class VentanaAyuda(QDialog):
    """Ventana de ayuda completa con documentación integrada"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Guía Completa - Generador de Actas ADIF")
        self.setWindowIcon(self._get_app_icon())
        self.setup_ui()
        self.cargar_contenido()
        
        # Configurar ventana
        self.resize(1000, 700)
        self.setModal(False)  # Permitir que funcione junto con la aplicación principal
        
    def _get_app_icon(self):
        """Obtener icono de la aplicación"""
        try:
            if hasattr(sys, '_MEIPASS'):
                icono_path = os.path.join(sys._MEIPASS, 'images', 'icono.ico')
            else:
                icono_path = 'images/icono.ico'
            
            if os.path.exists(icono_path):
                return QIcon(icono_path)
        except Exception as e:
            logger.debug(f"Error cargando icono ayuda: {e}")
        
        return QIcon()
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Header con logo y título
        self.create_header(layout)
        
        # Pestañas principales
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Crear pestañas
        self.create_tabs()
        
        # Botones inferiores
        self.create_bottom_buttons(layout)
    
    def create_header(self, layout):
        """Crear header de la ventana"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0066CC, stop: 1 #004499);
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header_frame.setMaximumHeight(120)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Logo (si está disponible)
        try:
            if hasattr(sys, '_MEIPASS'):
                logo_path = os.path.join(sys._MEIPASS, 'images', 'adif.png')
            else:
                logo_path = 'images/adif.png'
            
            if os.path.exists(logo_path):
                logo_label = QLabel()
                pixmap = QPixmap(logo_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
                header_layout.addWidget(logo_label)
        except:
            pass
        
        # Título y subtítulo
        title_layout = QVBoxLayout()
        
        title_label = QLabel("📋 Guía Completa - Generador de Actas ADIF")
        title_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin: 5px;
        """)
        
        subtitle_label = QLabel("Sistema integral de gestión de contratos y documentos oficiales")
        subtitle_label.setStyleSheet("""
            color: #E6F3FF;
            font-size: 12px;
            margin: 5px;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Versión
        version_label = QLabel("v3.2")
        version_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            margin: 10px;
        """)
        header_layout.addWidget(version_label)
        
        layout.addWidget(header_frame)
    
    def create_tabs(self):
        """Crear todas las pestañas de ayuda"""
        # 1. Inicio Rápido
        self.tab_inicio = self.create_scroll_tab()
        self.tab_widget.addTab(self.tab_inicio, "🚀 Inicio Rápido")
        
        # 2. Gestión de Contratos
        self.tab_contratos = self.create_scroll_tab()
        self.tab_widget.addTab(self.tab_contratos, "🏗️ Contratos")
        
        # 3. Generación de Documentos
        self.tab_documentos = self.create_scroll_tab()
        self.tab_widget.addTab(self.tab_documentos, "📄 Documentos")
        
        # 4. Facturas Directas
        self.tab_facturas = self.create_scroll_tab()
        self.tab_widget.addTab(self.tab_facturas, "💰 Facturas Directas")
        
        # 5. Seguimiento y Reportes
        self.tab_seguimiento = self.create_scroll_tab()
        self.tab_widget.addTab(self.tab_seguimiento, "📊 Seguimiento")
        
        # 6. Solución de Problemas
        self.tab_problemas = self.create_scroll_tab()
        self.tab_widget.addTab(self.tab_problemas, "🔧 Problemas")
        
        # 7. Acerca de
        self.tab_acerca = self.create_scroll_tab()
        self.tab_widget.addTab(self.tab_acerca, "ℹ️ Acerca de")
    
    def create_scroll_tab(self):
        """Crear una pestaña con scroll"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        return scroll_area
    
    def create_bottom_buttons(self, layout):
        """Crear botones inferiores"""
        button_layout = QHBoxLayout()
        
        # Botón proyecto actual
        self.btn_proyecto = QPushButton("📋 Ver Proyecto Actual")
        self.btn_proyecto.setStyleSheet("""
            QPushButton {
                background-color: #0066CC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052A3;
            }
        """)
        self.btn_proyecto.clicked.connect(self.mostrar_proyecto_actual)
        button_layout.addWidget(self.btn_proyecto)
        
        button_layout.addStretch()
        
        # Botón cerrar
        btn_cerrar = QPushButton("❌ Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        btn_cerrar.clicked.connect(self.close)
        button_layout.addWidget(btn_cerrar)
        
        layout.addLayout(button_layout)
    
    def cargar_contenido(self):
        """Cargar todo el contenido de ayuda"""
        self.cargar_inicio_rapido()
        self.cargar_gestion_contratos()
        self.cargar_generacion_documentos()
        self.cargar_facturas_directas()
        self.cargar_seguimiento()
        self.cargar_solucion_problemas()
        self.cargar_acerca_de()
    
    def cargar_inicio_rapido(self):
        """Cargar contenido de inicio rápido"""
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setText("""
        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
        
        <h1 style="color: #0066CC;">🚀 Inicio Rápido</h1>
        
        <h2>📋 Primeros Pasos</h2>
        <ol>
            <li><strong>Ejecutar la aplicación</strong>: La ventana principal se abre con el splash screen ADIF</li>
            <li><strong>Interfaz principal</strong>: 5 pestañas organizadas (Proyecto, Facturas Directas, Resumen, Actuaciones, Configuración)</li>
            <li><strong>Primer proyecto</strong>: Usar "Nuevo Proyecto" para comenzar</li>
            <li><strong>Estructura automática</strong>: Se crean carpetas organizadas automáticamente</li>
        </ol>
        
        <h2>🖥️ Interfaz de Usuario</h2>
        <div style="background: #F0F8FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Panel Principal - 5 Pestañas:</h3>
            <ul>
                <li><strong>📋 Proyecto</strong>: Gestión de contratos, empresas y generación de documentos</li>
                <li><strong>💰 Facturas Directas</strong>: Sistema independiente para contratación menor</li>
                <li><strong>📊 Resumen</strong>: Dashboard visual con cronogramas y estados</li>
                <li><strong>🔄 Actuaciones</strong>: Histórico de acciones y seguimiento</li>
                <li><strong>⚙️ Configuración</strong>: Firmantes, plantillas y preferencias</li>
            </ul>
        </div>
        
        <h2>📁 Estructura de Carpetas</h2>
        <div style="background: #F5F5F5; padding: 15px; border-radius: 8px; font-family: monospace;">
            obras/[NOMBRE_PROYECTO]/<br>
            ├── 01-proyecto/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Documentos iniciales<br>
            ├── 02-documentacion-finales/ &nbsp;&nbsp;# Versiones definitivas<br>
            ├── 03-cartas-invitacion/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Invitaciones a empresas<br>
            ├── 04-ofertas-recibidas/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Ofertas de licitadores<br>
            ├── 05-actas-adjudicacion/ &nbsp;&nbsp;&nbsp;&nbsp;# Documentos de adjudicación<br>
            ├── 06-contratos/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Contratos firmados<br>
            ├── 07-seguimiento/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Control de ejecución<br>
            ├── 08-liquidacion/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Documentos finales<br>
            └── 9_Guardado_seguridad/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Respaldos automáticos
        </div>
        
        <h2>⚡ Acciones Rápidas</h2>
        <div style="background: #E8F5E8; padding: 15px; border-radius: 8px;">
            <ul>
                <li><strong>Crear proyecto</strong>: Menú → Archivo → Nuevo Proyecto</li>
                <li><strong>Agregar empresa</strong>: Pestaña Proyecto → Tabla Empresas → Botón +</li>
                <li><strong>Generar documento</strong>: Pestaña Proyecto → Botones de generación</li>
                <li><strong>Nueva factura directa</strong>: Pestaña Facturas Directas → Nueva Factura</li>
                <li><strong>Ver seguimiento</strong>: Pestaña Resumen → Dashboard visual</li>
            </ul>
        </div>
        
        <div style="background: #FFF3CD; border: 1px solid #FFC107; padding: 10px; border-radius: 5px; margin: 15px 0;">
            <strong>💡 Consejo:</strong> Utiliza siempre el botón "Guardar" después de hacer cambios importantes.
            La aplicación hace respaldos automáticos, pero es recomendable guardar manualmente.
        </div>
        
        </div>
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(content)
        layout.addStretch()
        self.tab_inicio.widget().setLayout(layout)
    
    def cargar_gestion_contratos(self):
        """Cargar contenido de gestión de contratos"""
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setText("""
        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
        
        <h1 style="color: #0066CC;">🏗️ Gestión de Contratos</h1>
        
        <h2>📋 Crear Nuevo Contrato</h2>
        <div style="background: #F0F8FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Paso 1: Datos Básicos</h3>
            <ul>
                <li><strong>Nombre del Proyecto</strong>: Título descriptivo (ej: "OBRAS DE REPARACIÓN EN LAS INSTALACIONES")</li>
                <li><strong>Expediente</strong>: Código oficial (ej: "EXP-2024-001")</li>
                <li><strong>Tipo de Contrato</strong>: Obras, Servicios, o Mantenimiento</li>
                <li><strong>Presupuesto Base</strong>: Importe de licitación (ej: 50.000,00 €)</li>
                <li><strong>Plazo de Ejecución</strong>: Duración en días (ej: 60 días)</li>
            </ul>
        </div>
        
        <h2>🏢 Tipos de Contrato</h2>
        <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
            <tr style="background: #E8F4FD;">
                <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Tipo</strong></th>
                <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Descripción</strong></th>
                <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Límite</strong></th>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">🏗️ <strong>Obras</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Construcción, reformas, reparaciones</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">≤ 15.000 € (directa)</td>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">🔧 <strong>Servicios</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Mantenimiento, servicios técnicos</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">≤ 40.000 € (directa)</td>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">⚡ <strong>Mantenimiento</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Mantenimiento especializado</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Sin límite específico</td>
            </tr>
        </table>
        
        <h2>👥 Gestión de Empresas y Ofertas</h2>
        <div style="background: #F8F9FA; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Agregar Empresas Licitadoras:</h3>
            <ol>
                <li><strong>Ir a Pestaña "Proyecto"</strong></li>
                <li><strong>Localizar Tabla "Empresas"</strong></li>
                <li><strong>Clic en botón "+" (Agregar)</strong></li>
                <li><strong>Completar datos obligatorios</strong>:
                    <ul>
                        <li>Nombre de la empresa</li>
                        <li>NIF/CIF (se valida formato)</li>
                        <li>Email de contacto</li>
                        <li>Persona de contacto</li>
                    </ul>
                </li>
                <li><strong>Guardar</strong>: Los datos se sincronizan automáticamente</li>
            </ol>
        </div>
        
        <div style="background: #E8F5E8; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Control de Ofertas Automático:</h3>
            <ul>
                <li><strong>Sincronización</strong>: Al agregar empresa, aparece automáticamente en tabla de ofertas</li>
                <li><strong>Validación</strong>: Los importes se validan como números válidos</li>
                <li><strong>Comparación</strong>: Ordenamiento automático por importe (menor a mayor)</li>
                <li><strong>Estado</strong>: Control de ofertas presentadas, adjudicadas, rechazadas</li>
            </ul>
        </div>
        
        <h2>📊 Estados del Contrato</h2>
        <div style="background: #FFF3CD; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <ul>
                <li><strong>🟡 En Licitación</strong>: Proceso de invitación a empresas</li>
                <li><strong>🟠 Evaluando Ofertas</strong>: Análisis de propuestas recibidas</li>
                <li><strong>🟢 Adjudicado</strong>: Empresa seleccionada, contrato en preparación</li>
                <li><strong>🔵 En Ejecución</strong>: Trabajos en curso</li>
                <li><strong>✅ Finalizado</strong>: Trabajos completados satisfactoriamente</li>
                <li><strong>💰 Liquidado</strong>: Proceso económico cerrado</li>
            </ul>
        </div>
        
        <div style="background: #D1ECF1; border: 1px solid #17A2B8; padding: 10px; border-radius: 5px; margin: 15px 0;">
            <strong>💡 Consejo Avanzado:</strong> Utiliza el sistema de seguimiento en la pestaña "Resumen" 
            para tener una visión completa del estado de todos tus contratos.
        </div>
        
        </div>
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(content)
        layout.addStretch()
        self.tab_contratos.widget().setLayout(layout)
    
    def cargar_generacion_documentos(self):
        """Cargar contenido de generación de documentos"""
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setText("""
        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
        
        <h1 style="color: #0066CC;">📄 Generación de Documentos</h1>
        
        <h2>🎯 Proceso de Generación</h2>
        <div style="background: #F0F8FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <ol>
                <li><strong>Completar datos</strong> del contrato (nombre, expediente, presupuesto)</li>
                <li><strong>Agregar empresas</strong> participantes con sus ofertas</li>
                <li><strong>Seleccionar documento</strong> a generar según la fase del proyecto</li>
                <li><strong>Clic en botón</strong> correspondiente en la pestaña "Proyecto"</li>
                <li><strong>Validación automática</strong>: El sistema verifica que todos los datos necesarios estén completos</li>
                <li><strong>Generación automática</strong>: Se crea el documento Word (.docx)</li>
                <li><strong>Conversión a PDF</strong>: Si está disponible, también genera PDF</li>
                <li><strong>Guardado automático</strong>: Se almacena en la carpeta correspondiente</li>
            </ol>
        </div>
        
        <h2>📋 Documentos por Fase del Proyecto</h2>
        
        <h3>🔄 FASE DE LICITACIÓN</h3>
        <div style="background: #FFF8DC; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>📧 Cartas de Invitación</strong><br>
            <em>Cuándo usar</em>: Al inicio del proceso de licitación<br>
            <em>Se genera</em>: Una carta por cada empresa invitada<br>
            <em>Ubicación</em>: <code>03-cartas-invitacion/</code>
        </div>
        
        <h3>📋 FASE DE ADJUDICACIÓN</h3>
        <div style="background: #F0FFF0; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>📋 Acta de Adjudicación</strong><br>
            <em>Cuándo usar</em>: Tras evaluar todas las ofertas y seleccionar ganadora<br>
            <em>Se genera</em>: Documento oficial de adjudicación<br>
            <em>Ubicación</em>: <code>05-actas-adjudicacion/</code><br><br>
            
            <strong>✉️ Cartas de Adjudicación</strong><br>
            <em>Cuándo usar</em>: Para comunicar resultado a todas las empresas<br>
            <em>Se genera</em>: Carta de adjudicación (ganadora) + Cartas de no adjudicación (resto)<br>
            <em>Ubicación</em>: <code>05-actas-adjudicacion/</code>
        </div>
        
        <h3>🏗️ FASE DE EJECUCIÓN</h3>
        <div style="background: #E6F3FF; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>🟢 Acta de Inicio</strong><br>
            <em>Cuándo usar</em>: Al comenzar físicamente los trabajos<br>
            <em>Ubicación</em>: <code>07-seguimiento/</code><br><br>
            
            <strong>📐 Acta de Replanteo</strong> (solo obras)<br>
            <em>Cuándo usar</em>: Para obras que requieren replanteo técnico<br>
            <em>Ubicación</em>: <code>07-seguimiento/</code><br><br>
            
            <strong>👷 Nombramiento Director</strong><br>
            <em>Cuándo usar</em>: Para obras complejas que requieren director de obra<br>
            <em>Ubicación</em>: <code>06-contratos/</code><br><br>
            
            <strong>📄 Contrato Oficial</strong><br>
            <em>Cuándo usar</em>: Documento contractual tras adjudicación definitiva<br>
            <em>Ubicación</em>: <code>06-contratos/</code>
        </div>
        
        <h3>✅ FASE DE FINALIZACIÓN</h3>
        <div style="background: #F0F8FF; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>✅ Acta de Recepción</strong><br>
            <em>Cuándo usar</em>: Al finalizar satisfactoriamente los trabajos<br>
            <em>Ubicación</em>: <code>07-seguimiento/</code><br><br>
            
            <strong>💰 Acta de Liquidación</strong><br>
            <em>Cuándo usar</em>: Para el cierre económico final del contrato<br>
            <em>Ubicación</em>: <code>08-liquidacion/</code>
        </div>
        
        <h2>🔧 Variables de Plantilla</h2>
        <div style="background: #F5F5F5; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p>Las plantillas utilizan <strong>marcadores automáticos</strong> que se reemplazan por datos reales:</p>
            <div style="font-family: monospace; background: white; padding: 10px; border-radius: 5px;">
                @nombreProyecto@ → Nombre completo del proyecto<br>
                @expediente@ → Número de expediente oficial<br>
                @presupuestoBase@ → Presupuesto base (formato: 50.000,00 €)<br>
                @empresaAdjudicataria@ → Nombre de la empresa seleccionada<br>
                @importeAdjudicacion@ → Importe de la oferta ganadora<br>
                @firmanteConforme@ → Nombre del jefe de proyecto<br>
                @fechaContrato@ → Fecha del contrato (dd/mm/aaaa)
            </div>
        </div>
        
        <h2>⚠️ Validaciones Automáticas</h2>
        <div style="background: #FFE6E6; border: 1px solid #FF6B6B; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Antes de generar cualquier documento, el sistema verifica:</strong></p>
            <ul>
                <li>✅ <strong>Datos básicos completos</strong> (nombre, expediente, presupuesto)</li>
                <li>✅ <strong>Empresas con ofertas válidas</strong> (para documentos de adjudicación)</li>
                <li>✅ <strong>Fechas coherentes</strong> (inicio anterior a fin)</li>
                <li>✅ <strong>Importes numéricos correctos</strong></li>
                <li>✅ <strong>Firmantes configurados</strong> (menú Configuración)</li>
                <li>✅ <strong>Plantillas disponibles</strong> en carpeta plantillas/</li>
            </ul>
            
            <p><strong>Si falta algún dato crítico, verás un mensaje como:</strong></p>
            <div style="background: #FFF3CD; padding: 10px; border-radius: 5px; margin: 10px 0;">
                ⚠️ No se puede generar el documento<br>
                Faltan los siguientes datos obligatorios:<br>
                • Fecha de contrato<br>
                • Empresa adjudicataria<br>
                • Importe de adjudicación
            </div>
        </div>
        
        </div>
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(content)
        layout.addStretch()
        self.tab_documentos.widget().setLayout(layout)
    
    def cargar_facturas_directas(self):
        """Cargar contenido de facturas directas"""
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setText("""
        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
        
        <h1 style="color: #0066CC;">💰 Sistema de Facturas Directas</h1>
        
        <h2>🎯 ¿Cuándo Usar Facturas Directas?</h2>
        <div style="background: #E8F5E8; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>✅ Casos Apropiados:</h3>
            <ul>
                <li><strong>Servicios de urgencia</strong> (reparaciones inmediatas que no pueden esperar)</li>
                <li><strong>Contrataciones menores</strong> (por debajo del umbral de licitación)</li>
                <li><strong>Servicios especializados únicos</strong> (solo una empresa puede hacerlo)</li>
                <li><strong>Trabajos de mantenimiento rutinario</strong></li>
                <li><strong>Suministros menores</strong> (materiales básicos)</li>
            </ul>
        </div>
        
        <div style="background: #FFE6E6; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>❌ No Usar Para:</h3>
            <ul>
                <li>Contratos que superen los umbrales legales</li>
                <li>Obras o servicios que requieren licitación pública</li>
                <li>Contratos con múltiples oferentes disponibles</li>
            </ul>
        </div>
        
        <h2>📝 Crear Nueva Factura Directa</h2>
        <div style="background: #F0F8FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Paso 1: Acceder al Sistema</h3>
            <ol>
                <li><strong>Ir a pestaña "💰 Facturas Directas"</strong></li>
                <li><strong>Clic en "Nueva Factura"</strong></li>
                <li><strong>Se abre formulario de creación</strong></li>
            </ol>
            
            <h3>Paso 2: Completar Datos Básicos</h3>
            <ul>
                <li><strong>Descripción del Servicio</strong>: Breve descripción del trabajo</li>
                <li><strong>Empresa Contratista</strong>: Nombre completo de la empresa</li>
                <li><strong>NIF/CIF</strong>: Identificación fiscal (se valida formato)</li>
                <li><strong>Importe Sin IVA</strong>: Cantidad en euros</li>
                <li><strong>Fecha de Solicitud</strong>: Fecha actual por defecto</li>
                <li><strong>Categoría</strong>: Mantenimiento, Obras, Suministros, Urgencias</li>
            </ul>
            
            <h3>Paso 3: Información Adicional</h3>
            <ul>
                <li><strong>Ubicación del Trabajo</strong>: Lugar específico donde se realizará</li>
                <li><strong>Plazo de Ejecución</strong>: Tiempo estimado</li>
                <li><strong>Email de Contacto</strong>: Para comunicaciones</li>
                <li><strong>Observaciones</strong>: Detalles especiales</li>
            </ul>
        </div>
        
        <h2>🎛️ Estados de las Facturas</h2>
        <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
            <tr style="background: #E8F4FD;">
                <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Estado</strong></th>
                <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Descripción</strong></th>
                <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Acciones Disponibles</strong></th>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">🟢 <strong>Activa</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">En proceso de ejecución</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Editar, Cerrar, Generar Orden</td>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">🟡 <strong>Pendiente</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Esperando aprobación</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Editar, Aprobar, Rechazar</td>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">🔵 <strong>En Ejecución</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Trabajo en curso</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Ver Progreso, Comunicar</td>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">✅ <strong>Finalizada</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Completada satisfactoriamente</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Ver Resumen, Archivar</td>
            </tr>
            <tr>
                <td style="border: 1px solid #0066CC; padding: 8px;">🔴 <strong>Anulada</strong></td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Cancelada o rechazada</td>
                <td style="border: 1px solid #0066CC; padding: 8px;">Ver Motivo, Archivar</td>
            </tr>
        </table>
        
        <h2>💼 Límites Automáticos</h2>
        <div style="background: #FFF3CD; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>📊 Límites por Tipo de Servicio:</h3>
            <ul>
                <li><strong>🏗️ OBRAS</strong>: ≤ 40.000 € (contratación directa)</li>
                <li><strong>🔧 SERVICIOS</strong>: ≤ 15.000 € (contratación directa)</li>
                <li><strong>📦 SUMINISTROS</strong>: ≤ 15.000 € (contratación directa)</li>
                <li><strong>⚡ URGENCIAS</strong>: ≤ 60.000 € (justificación especial)</li>
            </ul>
            
            <p><strong>⚠️ El sistema alertará automáticamente si se superan estos límites.</strong></p>
        </div>
        
        <h2>🔍 Búsqueda y Filtrado</h2>
        <div style="background: #F8F9FA; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Filtros disponibles en el dashboard:</strong></p>
            <ul>
                <li><strong>🗓️ Rango de Fechas</strong>: Filtrar por período específico</li>
                <li><strong>🏢 Empresa</strong>: Ver facturas de una empresa concreta</li>
                <li><strong>💰 Rango de Importes</strong>: Filtrar por cantidad</li>
                <li><strong>🎯 Categoría</strong>: Por tipo de servicio</li>
                <li><strong>📍 Ubicación</strong>: Por lugar de trabajo</li>
                <li><strong>📝 Texto en Descripción</strong>: Búsqueda por palabras clave</li>
            </ul>
        </div>
        
        <h2>📄 Documentos Generados</h2>
        <div style="background: #E6F3FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>📋 Orden de Trabajo</h3>
            <p>Documento oficial que se envía a la empresa con:</p>
            <ul>
                <li>Datos completos de la empresa</li>
                <li>Descripción detallada del trabajo</li>
                <li>Importe total (base + IVA)</li>
                <li>Plazo de ejecución y fecha límite</li>
                <li>Condiciones especiales</li>
                <li>Datos del responsable ADIF</li>
            </ul>
            
            <h3>📋 Justificación de Contratación Directa</h3>
            <p>Documento interno que incluye:</p>
            <ul>
                <li>Motivo de urgencia o especialización</li>
                <li>Justificación legal aplicable</li>
                <li>Verificación de límites respetados</li>
                <li>Autorización del responsable</li>
            </ul>
        </div>
        
        </div>
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(content)
        layout.addStretch()
        self.tab_facturas.widget().setLayout(layout)
    
    def cargar_seguimiento(self):
        """Cargar contenido de seguimiento"""
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setText("""
        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
        
        <h1 style="color: #0066CC;">📊 Sistema de Seguimiento</h1>
        
        <h2>📈 Dashboard Principal</h2>
        <div style="background: #F0F8FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>La pestaña "📊 Resumen" proporciona una vista completa del estado de tus proyectos:</strong></p>
            <ul>
                <li><strong>Cronograma Visual</strong>: Timeline con todas las fases del proyecto</li>
                <li><strong>Estados en Tiempo Real</strong>: Indicadores de progreso actualizados</li>
                <li><strong>Tabla de Seguimiento</strong>: Control detallado de documentos y fechas</li>
                <li><strong>Historial de Acciones</strong>: Registro de todas las actividades</li>
            </ul>
        </div>
        
        <h2>🎯 Cronograma Visual</h2>
        <div style="background: #F8F9FA; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Fases del Proyecto:</h3>
            <div style="font-family: monospace; background: white; padding: 15px; border-radius: 5px;">
                📋 LICITACIÓN    →  📊 EVALUACIÓN  →  🏆 ADJUDICACIÓN<br>
                     ↓                    ↓                    ↓<br>
                🏗️ EJECUCIÓN     →  ✅ RECEPCIÓN   →  💰 LIQUIDACIÓN
            </div>
            
            <p><strong>Cada fase incluye:</strong></p>
            <ul>
                <li><strong>Fecha de inicio y fin</strong> estimada y real</li>
                <li><strong>Estado actual</strong> (completada, en progreso, pendiente)</li>
                <li><strong>Documentos asociados</strong> y su estado de generación</li>
                <li><strong>Responsable</strong> de cada fase</li>
            </ul>
        </div>
        
        <h2>📋 Tabla de Seguimiento</h2>
        <div style="background: #E8F5E8; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Información Detallada por Documento:</h3>
            <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr style="background: #E8F4FD;">
                    <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Documento</strong></th>
                    <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Estado</strong></th>
                    <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Fecha</strong></th>
                    <th style="border: 1px solid #0066CC; padding: 8px;"><strong>Acción</strong></th>
                </tr>
                <tr>
                    <td style="border: 1px solid #0066CC; padding: 8px;">Cartas Invitación</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">✅ Generado</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">15/03/2024</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">👁️ Ver | 📧 Enviar</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #0066CC; padding: 8px;">Acta Adjudicación</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">🟡 Pendiente</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">-</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">🔧 Generar</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #0066CC; padding: 8px;">Contrato</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">⏳ No iniciado</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">-</td>
                    <td style="border: 1px solid #0066CC; padding: 8px;">⏸️ Esperando adjudicación</td>
                </tr>
            </table>
        </div>
        
        <h2>🔄 Historial de Actuaciones</h2>
        <div style="background: #FFF3CD; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>La pestaña "🔄 Actuaciones" registra automáticamente:</strong></p>
            <ul>
                <li><strong>📅 Fecha y hora</strong> de cada acción</li>
                <li><strong>👤 Usuario</strong> que realizó la acción</li>
                <li><strong>📋 Tipo de acción</strong> (creación, modificación, generación de documento)</li>
                <li><strong>📄 Documentos afectados</strong></li>
                <li><strong>📝 Comentarios</strong> adicionales</li>
            </ul>
            
            <h3>Ejemplo de Entradas del Historial:</h3>
            <div style="font-family: monospace; background: white; padding: 10px; border-radius: 5px; margin: 10px 0;">
                15/03/2024 10:30 | Juan Pérez | 📋 Proyecto creado: "Reparación instalaciones"<br>
                15/03/2024 11:15 | Juan Pérez | 🏢 Empresa agregada: "ElectroServ S.L."<br>
                15/03/2024 14:20 | Juan Pérez | 📄 Generadas cartas de invitación (3 empresas)<br>
                18/03/2024 09:45 | Juan Pérez | 💰 Oferta registrada: ElectroServ - 12.500€<br>
                20/03/2024 16:30 | María García | 🏆 Adjudicación: ElectroServ S.L.
            </div>
        </div>
        
        <h2>📊 Reportes y Estadísticas</h2>
        <div style="background: #E6F3FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>Informes Disponibles:</h3>
            <ul>
                <li><strong>📈 Informe de Estado General</strong>: Resumen de todos los contratos activos</li>
                <li><strong>💰 Informe Económico</strong>: Análisis de presupuestos vs adjudicaciones</li>
                <li><strong>📅 Informe de Plazos</strong>: Control de fechas límite y vencimientos</li>
                <li><strong>🏢 Informe por Empresa</strong>: Análisis de adjudicaciones por contratista</li>
                <li><strong>📋 Informe de Facturas Directas</strong>: Resumen mensual de contratación menor</li>
            </ul>
            
            <h3>Exportación:</h3>
            <ul>
                <li><strong>📊 Excel</strong>: Todos los informes pueden exportarse a Excel</li>
                <li><strong>📄 PDF</strong>: Versiones imprimibles de los reportes</li>
                <li><strong>📧 Email</strong>: Envío automático de informes periódicos</li>
            </ul>
        </div>
        
        <h2>🔔 Alertas y Notificaciones</h2>
        <div style="background: #FFE6E6; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>El sistema te alerta automáticamente sobre:</h3>
            <ul>
                <li><strong>📅 Fechas límite próximas</strong>: Plazos de licitación, ejecución, etc.</li>
                <li><strong>📄 Documentos pendientes</strong>: Generaciones necesarias para continuar</li>
                <li><strong>💰 Límites económicos</strong>: Importes que se acercan a umbrales legales</li>
                <li><strong>🏢 Concentración de adjudicaciones</strong>: Múltiples contratos a la misma empresa</li>
                <li><strong>⏰ Contratos sin actividad</strong>: Proyectos estancados que requieren atención</li>
            </ul>
        </div>
        
        <div style="background: #D1ECF1; border: 1px solid #17A2B8; padding: 10px; border-radius: 5px; margin: 15px 0;">
            <strong>💡 Consejo de Productividad:</strong> Revisa el dashboard de seguimiento al menos una vez por semana 
            para mantener todos tus proyectos al día y no perder ninguna fecha importante.
        </div>
        
        </div>
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(content)
        layout.addStretch()
        self.tab_seguimiento.widget().setLayout(layout)
    
    def cargar_solucion_problemas(self):
        """Cargar contenido de solución de problemas"""
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setText("""
        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
        
        <h1 style="color: #0066CC;">🔧 Solución de Problemas</h1>
        
        <h2>❌ Problemas Comunes</h2>
        
        <h3>📄 Error al Generar PDF</h3>
        <div style="background: #FFE6E6; border: 1px solid #FF6B6B; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Mensaje:</strong> <code>Error: No se puede convertir a PDF</code></p>
            <p><strong>🔍 Causas posibles:</strong></p>
            <ul>
                <li>Microsoft Word no está instalado</li>
                <li>Word está abierto con documentos sin guardar</li>
                <li>Permisos insuficientes para ejecutar Word</li>
                <li>Plantilla dañada o corrupta</li>
            </ul>
            <p><strong>✅ Soluciones:</strong></p>
            <ol>
                <li><strong>Verificar instalación de Word</strong>: Abrir Word manualmente</li>
                <li><strong>Cerrar todos los documentos</strong> de Word y reintentar</li>
                <li><strong>Ejecutar aplicación como administrador</strong></li>
                <li><strong>Verificar plantillas</strong> en carpeta plantillas/</li>
                <li><strong>Generar solo Word</strong> (.docx) si el problema persiste</li>
            </ol>
        </div>
        
        <h3>💾 Los Datos No Se Guardan</h3>
        <div style="background: #FFF3CD; border: 1px solid #FFC107; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Mensaje:</strong> <code>Error: No se pueden guardar los cambios</code></p>
            <p><strong>🔍 Causas posibles:</strong></p>
            <ul>
                <li>Permisos de escritura insuficientes</li>
                <li>Disco lleno o sin espacio</li>
                <li>Archivo JSON bloqueado por otro proceso</li>
                <li>Ruta de guardado incorrecta</li>
            </ul>
            <p><strong>✅ Soluciones:</strong></p>
            <ol>
                <li><strong>Ejecutar como administrador</strong> la aplicación</li>
                <li><strong>Verificar espacio en disco</strong> disponible</li>
                <li><strong>Cerrar otras aplicaciones</strong> que puedan usar los archivos</li>
                <li><strong>Verificar permisos</strong> de la carpeta de instalación</li>
                <li><strong>Cambiar ubicación</strong> de guardado si es necesario</li>
            </ol>
        </div>
        
        <h3>📋 Plantilla No Encontrada</h3>
        <div style="background: #E6F3FF; border: 1px solid #17A2B8; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Mensaje:</strong> <code>Error: Plantilla no encontrada</code></p>
            <p><strong>🔍 Causas posibles:</strong></p>
            <ul>
                <li>Archivos de plantilla eliminados o movidos</li>
                <li>Nombres de plantilla incorrectos</li>
                <li>Carpeta plantillas/ no existe</li>
                <li>Permisos de lectura insuficientes</li>
            </ul>
            <p><strong>✅ Soluciones:</strong></p>
            <ol>
                <li><strong>Verificar carpeta plantillas/</strong> en directorio de instalación</li>
                <li><strong>Restaurar plantillas</strong> desde respaldo o reinstalación</li>
                <li><strong>Verificar nombres exactos</strong> de archivos de plantilla</li>
                <li><strong>Comprobar permisos de lectura</strong> en la carpeta</li>
                <li><strong>Ejecutar aplicación desde ubicación correcta</strong></li>
            </ol>
        </div>
        
        <h3>🏢 Error al Agregar Empresa</h3>
        <div style="background: #F0F8FF; border: 1px solid #6C7B7F; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Mensaje:</strong> <code>Error: Datos de empresa inválidos</code></p>
            <p><strong>🔍 Causas posibles:</strong></p>
            <ul>
                <li>Formato de NIF/CIF incorrecto</li>
                <li>Email con formato inválido</li>
                <li>Campos obligatorios vacíos</li>
                <li>Empresa duplicada</li>
            </ul>
            <p><strong>✅ Soluciones:</strong></p>
            <ol>
                <li><strong>Verificar formato NIF</strong>: 12345678X o B-12345678</li>
                <li><strong>Verificar email</strong>: debe contener @ y dominio válido</li>
                <li><strong>Completar todos los campos</strong> obligatorios</li>
                <li><strong>Verificar unicidad</strong>: no puede haber empresas duplicadas</li>
                <li><strong>Usar caracteres válidos</strong> (evitar símbolos especiales)</li>
            </ol>
        </div>
        
        <h2>🐛 Modo Debug y Logs</h2>
        <div style="background: #F8F9FA; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>📄 Ubicación de Logs:</h3>
            <ul>
                <li><strong>En desarrollo</strong>: <code>app.log</code> en directorio actual</li>
                <li><strong>En EXE</strong>: <code>_internal/app.log</code> junto al ejecutable</li>
            </ul>
            
            <h3>🔍 Información de Debug:</h3>
            <p>Los logs contienen información sobre:</p>
            <ul>
                <li>Errores detallados con stack traces</li>
                <li>Operaciones de guardado y carga</li>
                <li>Generación de documentos</li>
                <li>Validaciones fallidas</li>
                <li>Estados de la aplicación</li>
            </ul>
            
            <h3>📧 Reportar Problemas:</h3>
            <p><strong>Incluir siempre esta información:</strong></p>
            <ol>
                <li><strong>Descripción detallada</strong> del problema</li>
                <li><strong>Pasos exactos</strong> para reproducir el error</li>
                <li><strong>Mensaje de error completo</strong></li>
                <li><strong>Archivo de log</strong> relevante</li>
                <li><strong>Versión de la aplicación</strong></li>
                <li><strong>Sistema operativo</strong> y versión</li>
            </ol>
        </div>
        
        <h2>⚡ Consejos de Rendimiento</h2>
        <div style="background: #E8F5E8; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <ul>
                <li><strong>💾 Guardar frecuentemente</strong>: Usar Ctrl+S después de cambios importantes</li>
                <li><strong>🧹 Limpiar respaldos antiguos</strong>: En carpetas 9_Guardado_seguridad/</li>
                <li><strong>📄 Cerrar documentos Word</strong>: Antes de generar nuevos documentos</li>
                <li><strong>🔄 Reiniciar aplicación</strong>: Si funciona lenta después de uso prolongado</li>
                <li><strong>💿 Mantener espacio libre</strong>: Al menos 1GB libre en disco</li>
                <li><strong>🖥️ Cerrar otras aplicaciones</strong>: Si hay problemas de memoria</li>
            </ul>
        </div>
        
        <h2>🔄 Recuperación de Datos</h2>
        <div style="background: #D1ECF1; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>📦 Respaldos Automáticos:</h3>
            <p>La aplicación crea respaldos automáticos en:</p>
            <ul>
                <li><code>obras/[proyecto]/9_Guardado_seguridad/</code></li>
                <li><code>BaseDatos.json.backup_[fecha]</code></li>
            </ul>
            
            <h3>🔧 Recuperar Datos Perdidos:</h3>
            <ol>
                <li><strong>Localizar respaldo</strong> más reciente</li>
                <li><strong>Copiar archivo</strong> de respaldo</li>
                <li><strong>Renombrar a nombre original</strong></li>
                <li><strong>Reiniciar aplicación</strong></li>
                <li><strong>Verificar datos restaurados</strong></li>
            </ol>
        </div>
        
        <div style="background: #D4EDDA; border: 1px solid #28A745; padding: 10px; border-radius: 5px; margin: 15px 0;">
            <strong>💡 Consejo Importante:</strong> Si ninguna solución funciona, contacta con el soporte técnico 
            proporcionando toda la información de debug posible. Los logs son fundamentales para resolver problemas.
        </div>
        
        </div>
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(content)
        layout.addStretch()
        self.tab_problemas.widget().setLayout(layout)
    
    def cargar_acerca_de(self):
        """Cargar contenido acerca de"""
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setText("""
        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
        
        <h1 style="color: #0066CC;">ℹ️ Acerca del Generador de Actas ADIF</h1>
        
        <h2>🎯 Descripción del Sistema</h2>
        <div style="background: #F0F8FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>GesConAdif</strong> es una aplicación de escritorio desarrollada específicamente para 
            <strong>ADIF (Administrador de Infraestructuras Ferroviarias)</strong> que automatiza la gestión 
            completa de contratos de obras y servicios, desde la licitación hasta la liquidación final.</p>
            
            <h3>✨ Características Principales:</h3>
            <ul>
                <li><strong>🏗️ Gestión integral</strong>: Control completo del ciclo de vida de contratos</li>
                <li><strong>📄 Generación automática</strong>: +15 tipos de documentos oficiales</li>
                <li><strong>💰 Control financiero</strong>: Seguimiento de ofertas y facturación</li>
                <li><strong>📊 Facturas directas</strong>: Sistema para contratación menor</li>
                <li><strong>🔄 Seguimiento visual</strong>: Dashboard con cronogramas</li>
                <li><strong>📁 Organización automática</strong>: Estructura de carpetas por proyecto</li>
                <li><strong>💾 Respaldos automáticos</strong>: Seguridad de datos garantizada</li>
                <li><strong>🖥️ Interfaz moderna</strong>: UI intuitiva con splash screen profesional</li>
            </ul>
        </div>
        
        <h2>📊 Información Técnica</h2>
        <div style="background: #F8F9FA; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px; background: #E8F4FD;"><strong>Versión Actual</strong></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">3.2 (Producción)</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px; background: #E8F4FD;"><strong>Tecnología</strong></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Python 3.8+ con PyQt5</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px; background: #E8F4FD;"><strong>Plataforma</strong></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Windows 10/11</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px; background: #E8F4FD;"><strong>Base de Datos</strong></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">JSON (Máxima compatibilidad)</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px; background: #E8F4FD;"><strong>Documentos</strong></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">Microsoft Word (.docx) → PDF</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px; background: #E8F4FD;"><strong>Líneas de Código</strong></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">+15.000 líneas Python</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px; background: #E8F4FD;"><strong>Módulos</strong></td>
                    <td style="border: 1px solid #ccc; padding: 8px;">+50 archivos organizados</td>
                </tr>
            </table>
        </div>
        
        <h2>👨‍💻 Información de Desarrollo</h2>
        <div style="background: #E8F5E8; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <ul>
                <li><strong>👤 Desarrollador</strong>: Pablo Martín Fernández</li>
                <li><strong>🎓 Cargo</strong>: Ingeniero Industrial</li>
                <li><strong>🏢 Departamento</strong>: Patrimonio y Urbanismo</li>
                <li><strong>🏛️ Organización</strong>: ADIF</li>
                <li><strong>📅 Período de Desarrollo</strong>: 6+ meses activos</li>
                <li><strong>🔧 Estado</strong>: Producción estable</li>
            </ul>
        </div>
        
        <h2>📈 Historial de Versiones</h2>
        <div style="background: #FFF3CD; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>🚀 Versión 3.2 (Actual) - Septiembre 2024</h3>
            <ul>
                <li>✅ <strong>Splash screen profesional</strong> con logo ADIF</li>
                <li>✅ <strong>Iconos en barra de tareas</strong> y ventanas</li>
                <li>✅ <strong>Optimización de arranque</strong> con lazy loading</li>
                <li>✅ <strong>Logs organizados</strong> en _internal/ para EXE</li>
                <li>✅ <strong>Sistema de facturas directas</strong> completamente funcional</li>
                <li>✅ <strong>Dashboard avanzado</strong> con estadísticas</li>
                <li>✅ <strong>Compilación optimizada</strong> para distribución</li>
                <li>✅ <strong>Interfaz mejorada</strong> con tema corporativo</li>
                <li>✅ <strong>Sistema de ayuda integrado</strong> (esta ventana)</li>
            </ul>
            
            <h3>🎯 Versión 3.3 (Próxima) - Q4 2024</h3>
            <ul>
                <li>🔄 <strong>Integración con sistemas ADIF</strong> corporativos</li>
                <li>🔄 <strong>Notificaciones automáticas</strong> por email</li>
                <li>🔄 <strong>Dashboard ejecutivo</strong> con KPIs</li>
                <li>🔄 <strong>API REST</strong> para integraciones externas</li>
                <li>🔄 <strong>Workflow automatizado</strong> de aprobaciones</li>
                <li>🔄 <strong>Firma digital</strong> integrada</li>
            </ul>
        </div>
        
        <h2>📄 Licencia y Uso</h2>
        <div style="background: #FFE6E6; border: 1px solid #FF6B6B; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Este software es propiedad de ADIF (Administrador de Infraestructuras Ferroviarias)</strong> 
            y está destinado exclusivamente para uso interno de la organización.</p>
            
            <h3>📋 Restricciones de Uso:</h3>
            <ul>
                <li>❌ <strong>No distribución externa</strong>: No se permite compartir fuera de ADIF</li>
                <li>❌ <strong>No uso comercial por terceros</strong>: Exclusivo para operaciones internas</li>
                <li>❌ <strong>No modificación sin autorización</strong>: Cambios requieren aprobación</li>
                <li>✅ <strong>Uso interno ADIF autorizado</strong>: Libre uso dentro de la organización</li>
            </ul>
        </div>
        
        <h2>🛠️ Dependencias Principales</h2>
        <div style="background: #E6F3FF; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <ul>
                <li><strong>🐍 Python 3.8+</strong>: Lenguaje de programación principal</li>
                <li><strong>🖥️ PyQt5 5.15+</strong>: Framework de interfaz gráfica</li>
                <li><strong>📄 python-docx</strong>: Generación de documentos Word</li>
                <li><strong>📊 openpyxl</strong>: Manejo de archivos Excel</li>
                <li><strong>🖼️ Pillow</strong>: Procesamiento de imágenes</li>
                <li><strong>📋 docx2pdf</strong>: Conversión a PDF</li>
                <li><strong>🧪 pytest</strong>: Framework de testing</li>
            </ul>
        </div>
        
        <h2>📞 Soporte y Contacto</h2>
        <div style="background: #D1ECF1; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Para reportar problemas o solicitar mejoras:</strong></p>
            <ol>
                <li><strong>Descripción detallada</strong> del problema o solicitud</li>
                <li><strong>Pasos para reproducir</strong> el error (si aplica)</li>
                <li><strong>Archivos de log</strong> relevantes</li>
                <li><strong>Versión de la aplicación</strong> (mostrada en esta ventana)</li>
                <li><strong>Capturas de pantalla</strong> si es necesario</li>
            </ol>
            
            <p><strong>📧 Contacto Interno ADIF</strong>: A través de los canales habituales de soporte técnico</p>
        </div>
        
        <div style="background: #D4EDDA; border: 1px solid #28A745; padding: 10px; border-radius: 5px; margin: 15px 0;">
            <strong>🏆 Reconocimiento:</strong> Desarrollado con ❤️ para optimizar los procesos de contratación en ADIF.
            Gracias por utilizar el Generador de Actas ADIF y contribuir a la eficiencia de nuestros procesos.
        </div>
        
        </div>
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(content)
        layout.addStretch()
        self.tab_acerca.widget().setLayout(layout)
    
    def mostrar_proyecto_actual(self):
        """Mostrar información del proyecto actual"""
        # Obtener referencia al controlador principal
        parent_window = self.parent()
        if parent_window and hasattr(parent_window, 'proyecto_actual'):
            if parent_window.proyecto_actual and hasattr(parent_window, 'controlador_json'):
                try:
                    contract_data = parent_window.controlador_json.obtener_datos_contrato(parent_window.proyecto_actual)
                    
                    if contract_data:
                        mensaje = f"""
                        <div style="font-family: Segoe UI; line-height: 1.6; padding: 20px;">
                        <h2 style="color: #0066CC;">📋 Información del Proyecto Actual</h2>
                        <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                            <tr>
                                <td style="border: 1px solid #0066CC; padding: 8px; background: #E8F4FD;"><strong>Nombre</strong></td>
                                <td style="border: 1px solid #0066CC; padding: 8px;">{contract_data.get('nombre_proyecto', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #0066CC; padding: 8px; background: #E8F4FD;"><strong>Expediente</strong></td>
                                <td style="border: 1px solid #0066CC; padding: 8px;">{contract_data.get('numero_expediente', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #0066CC; padding: 8px; background: #E8F4FD;"><strong>Tipo</strong></td>
                                <td style="border: 1px solid #0066CC; padding: 8px;">{contract_data.get('tipo_contrato', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #0066CC; padding: 8px; background: #E8F4FD;"><strong>Presupuesto</strong></td>
                                <td style="border: 1px solid #0066CC; padding: 8px;">{contract_data.get('presupuesto_licitacion', 'N/A')} €</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #0066CC; padding: 8px; background: #E8F4FD;"><strong>Estado</strong></td>
                                <td style="border: 1px solid #0066CC; padding: 8px;">{contract_data.get('estado', 'N/A')}</td>
                            </tr>
                        </table>
                        </div>
                        """
                        
                        QMessageBox.information(self, "Proyecto Actual", mensaje)
                    else:
                        QMessageBox.information(self, "Proyecto Actual", "No se pudieron obtener los datos del proyecto actual.")
                        
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error obteniendo datos del proyecto: {e}")
            else:
                QMessageBox.information(self, "Información", "No hay ningún proyecto cargado actualmente.")
        else:
            QMessageBox.information(self, "Información", "No se pudo acceder a la información del proyecto.")