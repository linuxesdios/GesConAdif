"""
Diálogos para gestión de contratos y tipos
Incluye: Crear contrato, Borrar contrato, Cambiar tipo
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTextEdit, QComboBox, QCheckBox, QMessageBox,
                           QFormLayout, QGroupBox, QScrollArea, QWidget, QFrame)
from PyQt5.QtCore import Qt


class DialogoSeleccionTipo(QDialog):
    """Diálogo para seleccionar tipo de contrato"""
    
    def __init__(self, parent=None, tipo_actual=""):
        super().__init__(parent)
        self.tipo_seleccionado = None
        self.tipo_actual = tipo_actual
        self._setup_ui()
        
    def _setup_ui(self):
        """Configurar interfaz"""
        self.setWindowTitle("Cambiar Tipo de Contrato")
        self.setModal(True)
        self.resize(400, 280)  # Aumentar altura para el nuevo tipo
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("🔄 Seleccionar Nuevo Tipo de Contrato")
        titulo.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tipo actual
        if self.tipo_actual:
            actual = QLabel(f"Tipo actual: <b>{self.tipo_actual}</b>")
            actual.setStyleSheet("color: #666; margin: 5px;")
            layout.addWidget(actual)
        
        # Selector ACTUALIZADO
        layout.addWidget(QLabel("Nuevo tipo:"))
        self.combo_tipos = QComboBox()
        self.combo_tipos.addItems([
            "Seleccionar tipo...",
            "obras",
            "servicios", 
            "serv_mantenimiento",
            "obra_mantenimiento"
        ])
        
        # Seleccionar tipo actual si existe
        if self.tipo_actual:
            index = self.combo_tipos.findText(self.tipo_actual.title())
            if index >= 0:
                self.combo_tipos.setCurrentIndex(index)
        
        layout.addWidget(self.combo_tipos)
        
        # Descripción ACTUALIZADA con el nuevo tipo
        descripcion = QTextEdit()
        descripcion.setReadOnly(True)
        descripcion.setMaximumHeight(120)  # Aumentar altura
        descripcion.setHtml("""
        <b>📋 Tipos de Contrato:</b><br>
        • <b>Obras:</b> Contratos de construcción y obra civil<br>
        • <b>Servicios:</b> Contratos de servicios profesionales<br>
        • <b>Mantenimiento:</b> Contratos de mantenimiento y conservación<br>
        • <b>Facturas:</b> Gestión de facturación y pagos internos
        """)
        layout.addWidget(descripcion)
        
        # Conectar cambio de selección
        self.combo_tipos.currentTextChanged.connect(self._on_tipo_changed)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        self.btn_aceptar = QPushButton("✅ Aceptar")
        self.btn_aceptar.setEnabled(False)
        self.btn_aceptar.clicked.connect(self._confirmar_cambio)
        
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(self.btn_aceptar)
        
        layout.addLayout(botones_layout)



    def _on_tipo_changed(self, texto):
        """Manejar cambio en la selección"""
        self.btn_aceptar.setEnabled(
            texto and not texto.startswith("Seleccionar") and texto != self.tipo_actual
        )
        
    def _confirmar_cambio(self):
        """Confirmar cambio de tipo"""
        tipo_nuevo = self.combo_tipos.currentText()
        
        if not tipo_nuevo or tipo_nuevo.startswith("Seleccionar"):
            QMessageBox.warning(self, "Selección Inválida", 
                              "⚠️ Debes seleccionar un tipo válido")
            return
            
        if tipo_nuevo == self.tipo_actual:
            QMessageBox.information(self, "Sin Cambios", 
                                  "ℹ️ El tipo seleccionado es el mismo actual")
            return
        
        # Diálogo de confirmación
        respuesta = QMessageBox.question(
            self, "Confirmar Cambio",
            f"¿Estás seguro de cambiar el tipo de contrato?\n\n"
            f"De: <b>{self.tipo_actual or 'Sin tipo'}</b>\n"
            f"A: <b>{tipo_nuevo}</b>\n\n"
            f"Este cambio afectará:\n"
            f"• Las pestañas visibles\n"
            f"• Las validaciones aplicadas\n"
            f"• Los documentos generables\n\n"
            f"Se guardará automáticamente en el JSON.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.tipo_seleccionado = tipo_nuevo
            self.accept()
        
    def get_tipo_seleccionado(self):
        """Obtener el tipo seleccionado"""
        return self.tipo_seleccionado


class DialogoCrearContrato(QDialog):
    """Diálogo simplificado para crear nuevo contrato - Solo nombre y tipo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = None
        self.setWindowTitle("Crear Nuevo Contrato")
        self.setModal(True)
        self.resize(400, 200)  # Más pequeño
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz simplificada"""
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("🆕 Crear Nuevo Contrato")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Formulario simple
        form_layout = QFormLayout()
        
        # Solo nombre de obra (obligatorio)
        self.nombre_obra = QLineEdit()
        self.nombre_obra.setPlaceholderText("Introduce el nombre completo de la obra...")
        form_layout.addRow("Nombre de la obra*:", self.nombre_obra)
        
        # Solo tipo de actuación (obligatorio)
        self.tipo_actuacion = QComboBox()
        self.tipo_actuacion.addItems([
            "Seleccionar tipo...",
            "obras",
            "servicios", 
            "serv_mantenimiento",
            "obra_mantenimiento"
        ])
        form_layout.addRow("Tipo de actuación*:", self.tipo_actuacion)
        
        layout.addLayout(form_layout)
        
        # Espaciador
        layout.addStretch()
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        self.btn_crear = QPushButton("✅ Crear Contrato")
        self.btn_crear.clicked.connect(self.validar_y_crear)
        self.btn_crear.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.btn_crear.setEnabled(False)  # Deshabilitado inicialmente
        
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(self.btn_crear)
        
        layout.addLayout(botones_layout)
        
        # Conectar validación en tiempo real
        self.nombre_obra.textChanged.connect(self.validar_campos)
        
        # Focus inicial en nombre
        self.nombre_obra.setFocus()
        
    def validar_campos(self):
        """Validar campos en tiempo real"""
        nombre_valido = bool(self.nombre_obra.text().strip())
        self.btn_crear.setEnabled(nombre_valido)
    
    def validar_y_crear(self):
        """Validar datos y crear contrato"""
        nombre_obra = self.nombre_obra.text().strip()
        
        if not nombre_obra:
            QMessageBox.warning(self, "Error", "⚠️ El nombre de la obra es obligatorio")
            return
        
        # Preparar datos mínimos
        self.result = {
            "nombreObra": nombre_obra,
            "tipoActuacion": self.tipo_actuacion.currentText()
        }
        
        self.accept()

class DialogoClonarContrato(QDialog):
    """Diálogo para clonar contrato existente con opciones selectivas"""
    
    def __init__(self, parent=None, contrato_origen="", datos_contrato=None):
        super().__init__(parent)
        self.result = None
        self.contrato_origen = contrato_origen
        self.datos_contrato = datos_contrato or {}
        self.checkboxes = {}
        self.setWindowTitle("Clonar Contrato - Opciones Selectivas")
        self.setModal(True)
        self.resize(600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Título
        titulo = QLabel("📋 Clonar Contrato - Selecciona qué copiar")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #1976D2;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Información origen
        info_grupo = QGroupBox("📄 Contrato Original")
        info_layout = QVBoxLayout()
        
        origen_label = QLabel(f"<b>Origen:</b> {self.contrato_origen}")
        origen_label.setWordWrap(True)
        origen_label.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(origen_label)
        info_grupo.setLayout(info_layout)
        layout.addWidget(info_grupo)
        
        # Nuevo nombre
        form_layout = QFormLayout()
        self.nombre_nuevo = QLineEdit()
        self.nombre_nuevo.setPlaceholderText("Introduce el nuevo nombre...")
        self.nombre_nuevo.setText(f"{self.contrato_origen} - Copia")
        self.nombre_nuevo.setStyleSheet("padding: 8px; font-size: 12px;")
        form_layout.addRow("<b>Nuevo nombre*:</b>", self.nombre_nuevo)
        layout.addLayout(form_layout)
        
        # Área de desplazamiento para las opciones
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Botones de selección rápida
        botones_rapidos_layout = QHBoxLayout()
        btn_todo = QPushButton("✅ Seleccionar Todo")
        btn_nada = QPushButton("❌ Deseleccionar Todo")
        btn_basico = QPushButton("📋 Solo Básico")
        
        btn_todo.clicked.connect(self.seleccionar_todo)
        btn_nada.clicked.connect(self.deseleccionar_todo)
        btn_basico.clicked.connect(self.seleccionar_basico)
        
        for btn in [btn_todo, btn_nada, btn_basico]:
            btn.setStyleSheet("QPushButton { padding: 5px 10px; margin: 2px; }")
        
        botones_rapidos_layout.addWidget(btn_todo)
        botones_rapidos_layout.addWidget(btn_nada)
        botones_rapidos_layout.addWidget(btn_basico)
        botones_rapidos_layout.addStretch()
        scroll_layout.addLayout(botones_rapidos_layout)
        
        # Secciones de clonación por GroupBox
        self.crear_secciones_groupbox(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #ddd; }")
        layout.addWidget(scroll_area)
        
        # Botones principales
        botones_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("QPushButton { padding: 10px 20px; }")
        
        self.btn_clonar = QPushButton("📋 Clonar Contrato")
        self.btn_clonar.clicked.connect(self.validar_y_clonar)
        self.btn_clonar.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                font-weight: bold; 
                padding: 10px 20px; 
                border-radius: 5px;
            }
        """)
        
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_clonar)
        
        layout.addLayout(botones_layout)
        
        # Seleccionar básico por defecto
        self.seleccionar_basico()
        
        # Seleccionar texto del nombre
        self.nombre_nuevo.selectAll()
        self.nombre_nuevo.setFocus()
    
    def crear_checkbox(self, key, texto, descripcion="", checked=False):
        """Crear checkbox con descripción"""
        checkbox = QCheckBox(texto)
        checkbox.setChecked(checked)
        checkbox.setStyleSheet("QCheckBox { font-size: 12px; margin: 2px; }")
        
        if descripcion:
            checkbox.setToolTip(descripcion)
        
        self.checkboxes[key] = checkbox
        return checkbox
    
    def crear_secciones_groupbox(self, layout):
        """Crear secciones organizadas por GroupBox de la UI"""
        
        # Diccionario con la estructura de GroupBox y sus campos
        groupbox_estructura = {
            "groupBox_2": {
                "titulo": "📋 INFORMACIÓN DEL CONTRATO",
                "campos": {
                    "OrganoSolicitaOfertas": "Órgano Solicita Ofertas",
                    "organoContratacion": "Órgano Contratación",
                    "organoContratacion2": "Órgano Contratación 2", 
                    "nombreObra": "Nombre Obra",
                    "plazoEjecucion": "Plazo Ejecución",
                    "basePresupuesto": "Base Presupuesto",
                    "ivaPresupuestoBase": "IVA Presupuesto Base",
                    "totalPresupuestoBase": "Total Presupuesto Base"
                }
            },
            "groupBox_3": {
                "titulo": "📝 DESCRIPCIÓN Y JUSTIFICACIÓN", 
                "campos": {
                    "objeto": "Objeto",
                    "justificacion": "Justificación",
                    "insuficiencia": "Insuficiencia",
                    "justificacionLimites": "Justificación Límites",
                    "regimenPagos": "Régimen Pagos"
                }
            },
            "groupBox": {
                "titulo": "💰 ACTA DE LIQUIDACIÓN",
                "campos": {
                    "TantoPorCiento": "Tanto Por Ciento",
                    "adicionalBaseLiquidacion": "Adicional Base Liquidación",
                    "adicionalIvaLiquidacion": "Adicional IVA Liquidación",
                    "adicionalTotalLiquidacion_2": "Adicional Total Liquidación 2",
                    "saldoBaseLiquidacion": "Saldo Base Liquidación",
                    "saldoIvaLiquidacion": "Saldo IVA Liquidación", 
                    "adicionalTotalLiquidacion": "Adicional Total Liquidación",
                    "empresaBaseAFavor": "Empresa Base A Favor",
                    "empresaIvaAFavor": "Empresa IVA A Favor",
                    "empresaTotalAFavor": "Empresa Total A Favor",
                    "liquidacionAFavorAdifBase": "Liquidación A Favor ADIF Base",
                    "adifIvaAFavor": "ADIF IVA A Favor",
                    "adifTotalAFavor": "ADIF Total A Favor",
                    "certBase": "Cert Base",
                    "certIva": "Cert IVA",
                    "certTotal": "Cert Total",
                    "AfavorDe": "A Favor De",
                    "lugarFirma": "Lugar Firma",
                    "representanteContratista": "Representante Contratista",
                    "fechaRecepcion": "Fecha Recepción"
                }
            },
            "groupBox_9": {
                "titulo": "📨 CARTAS DE INVITACIÓN",
                "campos": {
                    "mailDeRecepcion": "Mail De Recepción",
                    "consultasAdministrativas": "Consultas Administrativas", 
                    "consultasTecnicas": "Consultas Técnicas",
                    "horaDeApertura": "Hora De Apertura",
                    "diaDeApertura": "Día De Apertura"
                }
            },
            "groupBox_10": {
                "titulo": "🏆 ACTA Y CARTAS DE ADJUDICACIÓN",
                "campos": {
                    "precioAdjudicacion": "Precio Adjudicación",
                    "precioAdjudicacionIva": "Precio Adjudicación IVA",
                    "precioAdjudicacionTotal": "Precio Adjudicación Total",
                    "empresaAdjudicada": "Empresa Adjudicada",
                    "contratistaCIF": "Contratista CIF",
                    "numEmpresasPresentadas": "Num Empresas Presentadas",
                    "numEmpresasSolicitadas": "Num Empresas Solicitadas",
                    "numeroExpediente": "Número Expediente",
                    "fechaAdjudicacion": "Fecha Adjudicación",
                    "licitacion15": "Licitación 15%",
                    "licitacion07": "Licitación 7%"
                }
            },
            "groupBox_11": {
                "titulo": "📋 CONTRATO",
                "campos": {
                    "BaseAnualidad1": "Base Anualidad 1",
                    "IvaAnualidad1": "IVA Anualidad 1", 
                    "TotalAnualidad1": "Total Anualidad 1",
                    "BaseAnualidad2": "Base Anualidad 2",
                    "IvaAnualidad2": "IVA Anualidad 2",
                    "TotalAnualidad2": "Total Anualidad 2",
                    "CIf_Contrato": "CIF Contrato",
                    "Lugar_Contrato": "Lugar Contrato",
                    "fechaContrato": "Fecha Contrato",
                    "Contrato_Por_Empresa": "Contrato Por Empresa",
                    "Contrato_Por_Adif": "Contrato Por ADIF"
                }
            },
            "groupBox_5": {
                "titulo": "📐 ACTA DE REPLANTEO",
                "campos": {
                    "fechaInforme": "Fecha Informe",
                    "fechaProyecto": "Fecha Proyecto",
                    "fechaReplanteo": "Fecha Replanteo",
                    "nombreAsistenteAdjudicatario": "Nombre Asistente Adjudicatario",
                    "nombreAsistenteAdif": "Nombre Asistente ADIF",
                    "representanteFirmaReplanteo": "Representante Firma Replanteo",
                    "lugarReplanteo": "Lugar Replanteo"
                }
            },
            "groupBox_6": {
                "titulo": "✅ ACTA DE RECEPCIÓN",
                "campos": {
                    "localizacion": "Localización",
                    "provincia": "Provincia",
                    "responsableContratoRecepcion": "Responsable Contrato Recepción",
                    "representanteContratistaRecepcion": "Representante Contratista Recepción",
                    "directorFacultativo": "Director Facultativo",
                    "tipoContrato": "Tipo Contrato",
                    "fechaLegalFin": "Fecha Legal Fin",
                    "fechaFinal": "Fecha Final",
                    "fechaRecepcion": "Fecha Recepción"
                }
            }
        }
        
        # Crear secciones por cada GroupBox
        for groupbox_id, info in groupbox_estructura.items():
            self.crear_seccion_groupbox_individual(layout, groupbox_id, info["titulo"], info["campos"])
    
    def crear_seccion_groupbox_individual(self, layout, groupbox_id, titulo, campos):
        """Crear una sección individual para un GroupBox"""
        grupo = QGroupBox(titulo)
        grupo_layout = QVBoxLayout()
        
        # Checkbox principal para seleccionar todo el GroupBox
        checkbox_grupo = QCheckBox(f"🔲 Seleccionar todo el grupo")
        checkbox_grupo.setStyleSheet("QCheckBox { font-weight: bold; font-size: 13px; color: #1976D2; margin: 5px; }")
        checkbox_grupo.stateChanged.connect(lambda state, gid=groupbox_id: self.toggle_groupbox(gid, state))
        
        self.checkboxes[f"groupbox_{groupbox_id}"] = checkbox_grupo
        grupo_layout.addWidget(checkbox_grupo)
        
        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #ddd;")
        grupo_layout.addWidget(line)
        
        # Crear checkboxes para cada campo individual
        for campo_id, campo_nombre in campos.items():
            checkbox = self.crear_checkbox(
                f"{groupbox_id}_{campo_id}",
                f"  ▫ {campo_nombre}",
                f"Copiar el campo {campo_nombre} del grupo {titulo}"
            )
            checkbox.setStyleSheet("QCheckBox { font-size: 11px; margin-left: 20px; }")
            grupo_layout.addWidget(checkbox)
        
        grupo.setLayout(grupo_layout) 
        layout.addWidget(grupo)
        
        # Guardar referencia de campos por GroupBox para el toggle
        if not hasattr(self, 'groupbox_campos'):
            self.groupbox_campos = {}
        self.groupbox_campos[groupbox_id] = [f"{groupbox_id}_{campo}" for campo in campos.keys()]
    
    def toggle_groupbox(self, groupbox_id, state):
        """Alternar selección de todos los campos de un GroupBox"""
        if groupbox_id in self.groupbox_campos:
            checked = state == 2  # Qt.Checked
            for campo_key in self.groupbox_campos[groupbox_id]:
                if campo_key in self.checkboxes:
                    self.checkboxes[campo_key].setChecked(checked)
    
    def crear_seccion_datos_contrato(self, layout):
        """Crear sección de datos del contrato"""
        grupo = QGroupBox("📋 Datos del Contrato")
        grupo_layout = QVBoxLayout()
        
        # Checkboxes para datos del contrato (sin número de expediente)
        grupo_layout.addWidget(self.crear_checkbox(
            "objeto_contrato", 
            "Objeto del Contrato",
            "Copia la descripción del objeto del contrato"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "tipo_contrato", 
            "Tipo de Contrato (Obra/Servicio)",
            "Copia el tipo de contrato seleccionado"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "organo_contratacion", 
            "Órgano de Contratación",
            "Copia el órgano de contratación del contrato original"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "importes", 
            "Importes de Licitación",
            "Copia todos los importes (licitación, IVA, total)"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "plazos", 
            "Duración y Plazos",
            "Copia la duración y plazos de ejecución"
        ))
        
        grupo.setLayout(grupo_layout)
        layout.addWidget(grupo)
    
    def crear_seccion_empresas(self, layout):
        """Crear sección de empresas"""
        grupo = QGroupBox("🏢 Empresas Licitadoras")
        grupo_layout = QVBoxLayout()
        
        grupo_layout.addWidget(self.crear_checkbox(
            "empresas_datos", 
            "Datos de Empresas",
            "Copia todos los datos de las empresas (nombre, NIF, email, contacto)"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "empresas_invitadas", 
            "Lista de Empresas Invitadas",
            "Mantiene la lista de empresas que fueron invitadas"
        ))
        
        grupo.setLayout(grupo_layout)
        layout.addWidget(grupo)
    
    def crear_seccion_ofertas(self, layout):
        """Crear sección de ofertas económicas"""
        grupo = QGroupBox("💰 Ofertas Económicas")
        grupo_layout = QVBoxLayout()
        
        grupo_layout.addWidget(self.crear_checkbox(
            "ofertas_importes", 
            "Importes de Ofertas",
            "Copia los importes ofertados por cada empresa"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "ofertas_clasificacion", 
            "Orden Clasificatorio",
            "Mantiene el orden de clasificación de las ofertas"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "empresa_adjudicataria", 
            "Empresa Adjudicataria",
            "Copia qué empresa resultó adjudicataria"
        ))
        
        grupo.setLayout(grupo_layout)
        layout.addWidget(grupo)
    
    def crear_seccion_fechas(self, layout):
        """Crear sección de fechas"""
        grupo = QGroupBox("📅 Fechas del Proceso")
        grupo_layout = QVBoxLayout()
        
        grupo_layout.addWidget(self.crear_checkbox(
            "fechas_proceso", 
            "Fechas del Proceso Licitatorio",
            "Copia todas las fechas (invitación, presentación ofertas, adjudicación)"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "fechas_ejecucion", 
            "Fechas de Ejecución",
            "Copia fechas de inicio, replanteo y recepción"
        ))
        
        grupo.setLayout(grupo_layout)
        layout.addWidget(grupo)
    
    def crear_seccion_liquidacion(self, layout):
        """Crear sección de liquidación"""
        grupo = QGroupBox("💰 Datos de Liquidación")
        grupo_layout = QVBoxLayout()
        
        grupo_layout.addWidget(self.crear_checkbox(
            "liquidacion_importes", 
            "Importes de Liquidación",
            "Copia importes licitados, facturados y penalizaciones"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "liquidacion_saldos", 
            "Saldos Finales",
            "Copia los saldos a favor de ADIF o empresa"
        ))
        
        grupo.setLayout(grupo_layout)
        layout.addWidget(grupo)
    
    def crear_seccion_documentos(self, layout):
        """Crear sección de documentos generados"""
        grupo = QGroupBox("📄 Documentos y Configuración")
        grupo_layout = QVBoxLayout()
        
        grupo_layout.addWidget(self.crear_checkbox(
            "firmantes", 
            "Firmantes",
            "Copia la configuración de firmantes de documentos"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "plantillas_config", 
            "Configuración de Plantillas",
            "Mantiene la configuración de plantillas utilizadas"
        ))
        
        # NOTA: No incluimos documentos generados físicamente
        nota = QLabel("<i>Nota: Los documentos PDF/Word generados NO se copian, solo la configuración</i>")
        nota.setStyleSheet("color: #666; font-size: 10px; margin: 5px;")
        grupo_layout.addWidget(nota)
        
        grupo.setLayout(grupo_layout)
        layout.addWidget(grupo)
    
    def crear_seccion_documentos_especificos(self, layout):
        """Crear sección específica para documentos que se pueden clonar"""
        grupo = QGroupBox("📋 Documentos Específicos (TODOS los campos en blanco excepto básicos)")
        grupo_layout = QVBoxLayout()
        
        grupo_layout.addWidget(self.crear_checkbox(
            "acta_inicio_datos", 
            "Datos de Acta de Inicio",
            "Copia SOLO datos básicos para generar acta inicio (resto campos en blanco)"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "contrato_datos", 
            "Datos de Contrato",
            "Copia SOLO datos básicos para generar contrato (resto campos en blanco)"
        ))
        
        grupo_layout.addWidget(self.crear_checkbox(
            "cartas_invitacion_datos", 
            "Datos de Cartas de Invitación",
            "Copia SOLO datos básicos para generar cartas invitación (resto campos en blanco)"
        ))
        
        # Nota importante
        nota = QLabel("<b>IMPORTANTE:</b> Estos documentos se generarán con datos mínimos.<br>"
                     "El resto de campos aparecerán en BLANCO para rellenar manualmente.")
        nota.setStyleSheet("color: #d32f2f; font-size: 11px; margin: 10px; padding: 8px; "
                          "border: 1px solid #d32f2f; border-radius: 4px; background-color: #ffebee;")
        nota.setWordWrap(True)
        grupo_layout.addWidget(nota)
        
        grupo.setLayout(grupo_layout)
        layout.addWidget(grupo)
    
    def seleccionar_todo(self):
        """Seleccionar todas las opciones"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def deseleccionar_todo(self):
        """Deseleccionar todas las opciones"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def seleccionar_basico(self):
        """Seleccionar solo opciones básicas recomendadas"""
        self.deseleccionar_todo()
        
        # Opciones básicas recomendadas (solo datos de contrato y empresas)
        basicas = [
            "objeto_contrato",
            "tipo_contrato", 
            "organo_contratacion",
            "importes",
            "empresas_datos"
        ]
        
        for key in basicas:
            if key in self.checkboxes:
                self.checkboxes[key].setChecked(True)
    
    def get_opciones_seleccionadas(self):
        """Obtener diccionario de opciones seleccionadas"""
        return {key: checkbox.isChecked() for key, checkbox in self.checkboxes.items()}
    
    def validar_y_clonar(self):
        """Validar y clonar con opciones seleccionadas"""
        nuevo_nombre = self.nombre_nuevo.text().strip()
        
        if not nuevo_nombre:
            QMessageBox.warning(self, "Error", "⚠️ El nuevo nombre es obligatorio")
            return
        
        if nuevo_nombre == self.contrato_origen:
            QMessageBox.warning(self, "Error", "⚠️ El nuevo nombre debe ser diferente al original")
            return
        
        opciones = self.get_opciones_seleccionadas()
        seleccionadas = sum(1 for v in opciones.values() if v)
        
        if seleccionadas == 0:
            respuesta = QMessageBox.question(
                self, 
                "Sin Opciones", 
                "⚠️ No has seleccionado ninguna opción para clonar.\n¿Deseas crear un contrato completamente vacío?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.No:
                return
        
        self.result = {
            "origen": self.contrato_origen,
            "nuevo_nombre": nuevo_nombre,
            "opciones": opciones
        }
        
        self.accept()
class DialogoBorrarContrato(QDialog):
    """Diálogo para confirmar borrado de contrato"""
    
    def __init__(self, parent=None, nombre_contrato="", datos_contrato=None):
        super().__init__(parent)
        self.confirmado = False
        self.borrar_carpeta = False
        self.nombre_contrato = nombre_contrato
        self.datos_contrato = datos_contrato or {}
        self.setWindowTitle("Borrar Contrato")
        self.setModal(True)
        self.resize(450, 350)  # Aumentar altura para el nuevo checkbox
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz"""
        layout = QVBoxLayout(self)
        
        # Título de advertencia
        titulo = QLabel("⚠️ ELIMINAR CONTRATO")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f; margin: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Información del contrato
        info_grupo = QGroupBox("📋 Información del Contrato")
        info_layout = QVBoxLayout()
        
        # Nombre
        nombre_label = QLabel(f"<b>Nombre:</b> {self.nombre_contrato}")
        nombre_label.setWordWrap(True)
        info_layout.addWidget(nombre_label)
        
        # Datos adicionales si existen
        if self.datos_contrato:
            tipo = self.datos_contrato.get('tipoActuacion', 'No especificado')
            expediente = self.datos_contrato.get('numeroExpediente', 'No especificado')
            
            info_layout.addWidget(QLabel(f"<b>Tipo:</b> {tipo}"))
            info_layout.addWidget(QLabel(f"<b>Expediente:</b> {expediente}"))
        
        info_grupo.setLayout(info_layout)
        layout.addWidget(info_grupo)
        
        # Advertencia
        advertencia = QLabel("""
        <div style='background-color: #ffebee; padding: 10px; border-left: 4px solid #f44336;'>
        <b>⚠️ ATENCIÓN:</b><br>
        Esta acción eliminará:<br>
        • El contrato del archivo JSON<br>
        • La carpeta asociada y todo su contenido<br>
        • Todos los documentos y archivos relacionados<br><br>
        <b>Esta acción NO se puede deshacer.</b>
        </div>
        """)
        advertencia.setWordWrap(True)
        layout.addWidget(advertencia)
        
        # Confirmación
        self.checkbox_confirmar = QCheckBox("He leído la advertencia y confirmo que quiero eliminar este contrato")
        layout.addWidget(self.checkbox_confirmar)
        
        # Checkbox adicional para borrar carpeta
        self.checkbox_borrar_carpeta = QCheckBox("🗂️ También borrar la carpeta de obra (si existe)")
        self.checkbox_borrar_carpeta.setStyleSheet("QCheckBox { color: #d32f2f; font-weight: bold; margin-top: 10px; }")
        self.checkbox_borrar_carpeta.setToolTip("Buscará y eliminará la carpeta física del proyecto en la carpeta 'obras'")
        layout.addWidget(self.checkbox_borrar_carpeta)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        self.btn_eliminar = QPushButton("🗑️ ELIMINAR DEFINITIVAMENTE")
        self.btn_eliminar.clicked.connect(self.confirmar_eliminacion)
        self.btn_eliminar.setEnabled(False)
        self.btn_eliminar.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; font-weight: bold; }")
        
        # Conectar checkbox
        self.checkbox_confirmar.toggled.connect(self.btn_eliminar.setEnabled)
        
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(self.btn_eliminar)
        
        layout.addLayout(botones_layout)
    
    def confirmar_eliminacion(self):
        """Confirmar eliminación con doble verificación"""
        if self.checkbox_borrar_carpeta.isChecked():
            respuesta = QMessageBox.question(
                self, "⚠️ CONFIRMACIÓN DE BORRADO",
                f"¿Confirmas borrar el contrato?\n\n"
                f"'{self.nombre_contrato}'\n\n"
                f"- Se eliminará del JSON\n"
                f"- También se buscará y borrará la carpeta física\n\n"
                f"¿Proceder?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
        else:
            respuesta = QMessageBox.question(
                self, "⚠️ CONFIRMACIÓN DE BORRADO",
                f"¿Confirmas borrar el contrato del JSON?\n\n"
                f"'{self.nombre_contrato}'\n\n"
                f"(No se tocará la carpeta física)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
        
        if respuesta == QMessageBox.Yes:
            self.confirmado = True
            self.borrar_carpeta = self.checkbox_borrar_carpeta.isChecked()
            self.accept()