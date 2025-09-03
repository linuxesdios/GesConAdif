#!/usr/bin/env python3
"""
Tests para controlador_resumen.py
Pruebas unitarias completas para el sistema de resumen unificado ADIF
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, date
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QPushButton, 
                            QTableWidget, QTextEdit, QGraphicsView, QGraphicsScene)
from PyQt5.QtCore import QUrl
from PyQt5.QtTest import QTest

# Configurar ruta de importación
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock de PyQt5.QtChart antes de importar
sys.modules['PyQt5.QtChart'] = MagicMock()
sys.modules['PyQt5.QtChart.QChart'] = MagicMock()
sys.modules['PyQt5.QtChart.QChartView'] = MagicMock()
sys.modules['PyQt5.QtChart.QPieSeries'] = MagicMock()
sys.modules['PyQt5.QtChart.QPieSlice'] = MagicMock()

from controladores.controlador_resumen import (
    EstadoDocumento,
    TipoDocumento,
    DocumentoGenerado,
    TrackerDocumentos,
    IntegradorResumen
)


class TestEstadoDocumento:
    """Tests para enum EstadoDocumento"""
    
    def test_valores_estado(self):
        """Test valores del enum EstadoDocumento"""
        assert EstadoDocumento.GENERANDO.value == "generando"
        assert EstadoDocumento.GENERADO.value == "generado"
        assert EstadoDocumento.ERROR.value == "error"
        assert EstadoDocumento.MODIFICADO.value == "modificado"
        assert EstadoDocumento.ENVIADO.value == "enviado"
        assert EstadoDocumento.FIRMADO.value == "firmado"


class TestTipoDocumento:
    """Tests para enum TipoDocumento"""
    
    def test_valores_tipo(self):
        """Test valores del enum TipoDocumento"""
        assert TipoDocumento.INVITACION.value == "invitacion"
        assert TipoDocumento.ADJUDICACION.value == "adjudicacion"
        assert TipoDocumento.ACTA_INICIO.value == "acta_inicio"
        assert TipoDocumento.ACTA_REPLANTEO.value == "acta_replanteo"
        assert TipoDocumento.ACTA_RECEPCION.value == "acta_recepcion"
        assert TipoDocumento.ACTA_FINALIZACION.value == "acta_finalizacion"
        assert TipoDocumento.LIQUIDACION.value == "liquidacion"
        assert TipoDocumento.CONTRATO.value == "contrato"
        assert TipoDocumento.OTRO.value == "otro"


class TestDocumentoGenerado:
    """Tests para dataclass DocumentoGenerado"""
    
    def test_creacion_documento_basico(self):
        """Test creación básica de DocumentoGenerado"""
        fecha = datetime.now()
        doc = DocumentoGenerado(
            id="test123",
            tipo=TipoDocumento.CONTRATO,
            nombre="Contrato Test",
            ruta_archivo="/path/test.docx",
            fecha_generacion=fecha,
            estado=EstadoDocumento.GENERADO,
            tamano_kb=150.5
        )
        
        assert doc.id == "test123"
        assert doc.tipo == TipoDocumento.CONTRATO
        assert doc.nombre == "Contrato Test"
        assert doc.ruta_archivo == "/path/test.docx"
        assert doc.fecha_generacion == fecha
        assert doc.estado == EstadoDocumento.GENERADO
        assert doc.tamano_kb == 150.5
        assert doc.observaciones == ""  # Valor por defecto
        assert doc.plantilla_usada == ""  # Valor por defecto
    
    def test_creacion_documento_completo(self):
        """Test creación completa de DocumentoGenerado"""
        fecha = datetime.now()
        doc = DocumentoGenerado(
            id="test456",
            tipo=TipoDocumento.INVITACION,
            nombre="Invitación Test",
            ruta_archivo="/path/invitacion.docx",
            fecha_generacion=fecha,
            estado=EstadoDocumento.ENVIADO,
            tamano_kb=250.75,
            observaciones="Documento enviado por email",
            plantilla_usada="plantilla_invitacion.docx"
        )
        
        assert doc.observaciones == "Documento enviado por email"
        assert doc.plantilla_usada == "plantilla_invitacion.docx"


class TestTrackerDocumentos:
    """Tests para la clase TrackerDocumentos"""
    
    @pytest.fixture
    def temp_dir(self):
        """Directorio temporal para tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def tracker(self, temp_dir):
        """Fixture de tracker con directorio temporal"""
        return TrackerDocumentos(ruta_base=temp_dir)
    
    @pytest.fixture
    def sample_documento(self):
        """Documento de ejemplo para tests"""
        return DocumentoGenerado(
            id="doc123",
            tipo=TipoDocumento.CONTRATO,
            nombre="Contrato Test",
            ruta_archivo="/path/contrato.docx",
            fecha_generacion=datetime(2024, 1, 15, 10, 30),
            estado=EstadoDocumento.GENERADO,
            tamano_kb=125.5,
            observaciones="Documento de prueba",
            plantilla_usada="plantilla_contrato.docx"
        )
    
    def test_init_tracker_con_ruta(self, temp_dir):
        """Test inicialización con ruta específica"""
        tracker = TrackerDocumentos(ruta_base=temp_dir)
        
        assert tracker.ruta_base == temp_dir
        assert tracker.archivo_historial == os.path.join(temp_dir, "historial_documentos.json")
        assert isinstance(tracker.documentos, dict)
    
    def test_init_tracker_sin_ruta(self):
        """Test inicialización sin ruta (usando rutas centralizadas)"""
        with patch('controladores.controlador_resumen.rutas') as mock_rutas:
            mock_rutas.get_base_path.return_value = "/test/base"
            mock_rutas.get_ruta_historial_documentos.return_value = "/test/historial.json"
            
            tracker = TrackerDocumentos()
            
            assert tracker.ruta_base == "/test/base"
            assert tracker.archivo_historial == "/test/historial.json"
    
    def test_cargar_historial_archivo_no_existe(self, tracker):
        """Test cargar historial cuando no existe archivo"""
        # El archivo no existe, debería inicializar vacío
        assert tracker.documentos == {}
    
    def test_cargar_historial_archivo_valido(self, tracker, temp_dir):
        """Test cargar historial desde archivo válido"""
        # Crear archivo de historial
        datos_historial = {
            "contrato_test": [
                {
                    "id": "doc123",
                    "tipo": "contrato",
                    "nombre": "Contrato Test",
                    "ruta_archivo": "/path/test.docx",
                    "fecha_generacion": "2024-01-15T10:30:00",
                    "estado": "generado",
                    "tamano_kb": 150.5,
                    "observaciones": "Test doc",
                    "plantilla_usada": "plantilla.docx"
                }
            ]
        }
        
        with open(tracker.archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(datos_historial, f)
        
        # Recargar historial
        tracker.cargar_historial()
        
        assert "contrato_test" in tracker.documentos
        assert len(tracker.documentos["contrato_test"]) == 1
        
        doc = tracker.documentos["contrato_test"][0]
        assert doc.id == "doc123"
        assert doc.tipo == TipoDocumento.CONTRATO
        assert doc.nombre == "Contrato Test"
        assert doc.estado == EstadoDocumento.GENERADO
    
    def test_cargar_historial_archivo_corrupto(self, tracker, temp_dir):
        """Test cargar historial con archivo corrupto"""
        # Escribir JSON inválido
        with open(tracker.archivo_historial, 'w') as f:
            f.write("JSON inválido")
        
        tracker.cargar_historial()
        
        # Debería inicializar vacío
        assert tracker.documentos == {}
    
    def test_cargar_historial_documento_invalido(self, tracker, temp_dir):
        """Test cargar historial con documento inválido"""
        datos_historial = {
            "contrato_test": [
                {
                    "id": "doc123",
                    # Falta campo "tipo" requerido
                    "nombre": "Test",
                    "ruta_archivo": "/test.docx",
                    "fecha_generacion": "2024-01-15T10:30:00",
                    "estado": "generado",
                    "tamano_kb": 100
                },
                {
                    "id": "doc456",
                    "tipo": "contrato",
                    "nombre": "Test 2",
                    "ruta_archivo": "/test2.docx",
                    "fecha_generacion": "2024-01-16T11:00:00",
                    "estado": "generado",
                    "tamano_kb": 200
                }
            ]
        }
        
        with open(tracker.archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(datos_historial, f)
        
        tracker.cargar_historial()
        
        # Solo debería cargar el documento válido
        assert "contrato_test" in tracker.documentos
        assert len(tracker.documentos["contrato_test"]) == 1
        assert tracker.documentos["contrato_test"][0].id == "doc456"
    
    def test_guardar_historial_exitoso(self, tracker, sample_documento):
        """Test guardar historial exitosamente"""
        # Agregar documento
        tracker.documentos["contrato_test"] = [sample_documento]
        
        resultado = tracker.guardar_historial()
        assert resultado is True
        
        # Verificar que se guardó
        assert os.path.exists(tracker.archivo_historial)
        
        # Verificar contenido
        with open(tracker.archivo_historial, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        assert "contrato_test" in datos
        assert len(datos["contrato_test"]) == 1
        assert datos["contrato_test"][0]["id"] == "doc123"
    
    def test_guardar_historial_error(self, tracker):
        """Test error al guardar historial"""
        with patch('builtins.open', side_effect=PermissionError("No permission")):
            resultado = tracker.guardar_historial()
            assert resultado is False
    
    def test_registrar_documento_iniciado_con_enum(self, tracker):
        """Test registrar documento iniciado con enum"""
        doc_id = tracker.registrar_documento_iniciado(
            contrato="test_contrato",
            tipo=TipoDocumento.INVITACION,
            nombre="Invitación Test",
            plantilla="plantilla_invitacion.docx"
        )
        
        assert len(doc_id) == 8  # UUID truncado
        assert "test_contrato" in tracker.documentos
        assert len(tracker.documentos["test_contrato"]) == 1
        
        doc = tracker.documentos["test_contrato"][0]
        assert doc.id == doc_id
        assert doc.tipo == TipoDocumento.INVITACION
        assert doc.nombre == "Invitación Test"
        assert doc.estado == EstadoDocumento.GENERANDO
        assert doc.plantilla_usada == "plantilla_invitacion.docx"
        assert doc.ruta_archivo == ""
        assert doc.tamano_kb == 0.0
    
    def test_registrar_documento_iniciado_con_string(self, tracker):
        """Test registrar documento iniciado con string"""
        doc_id = tracker.registrar_documento_iniciado(
            contrato="test_contrato",
            tipo="invitacion",
            nombre="Invitación Test"
        )
        
        doc = tracker.documentos["test_contrato"][0]
        assert doc.tipo == TipoDocumento.INVITACION
    
    def test_registrar_documento_iniciado_string_invalido(self, tracker):
        """Test registrar documento con tipo string inválido"""
        doc_id = tracker.registrar_documento_iniciado(
            contrato="test_contrato",
            tipo="tipo_inexistente",
            nombre="Test Doc"
        )
        
        doc = tracker.documentos["test_contrato"][0]
        assert doc.tipo == TipoDocumento.OTRO
    
    def test_registrar_documento_completado(self, tracker):
        """Test registrar documento como completado"""
        # Iniciar documento
        doc_id = tracker.registrar_documento_iniciado(
            contrato="test_contrato",
            tipo=TipoDocumento.CONTRATO,
            nombre="Contrato Test"
        )
        
        # Crear archivo temporal para simular documento generado
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(b"Test content")
            archivo_path = temp_file.name
        
        try:
            # Completar documento
            tracker.registrar_documento_completado(
                contrato="test_contrato",
                documento_id=doc_id,
                ruta_archivo=archivo_path,
                observaciones="Documento completado exitosamente"
            )
            
            doc = tracker.documentos["test_contrato"][0]
            assert doc.estado == EstadoDocumento.GENERADO
            assert doc.ruta_archivo == archivo_path
            assert doc.tamano_kb > 0
            assert doc.observaciones == "Documento completado exitosamente"
        
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(archivo_path)
            except:
                pass
    
    def test_registrar_documento_completado_no_existe(self, tracker):
        """Test completar documento que no existe"""
        tracker.registrar_documento_completado(
            contrato="test_contrato",
            documento_id="inexistente",
            ruta_archivo="/test.docx"
        )
        
        # No debería hacer nada
        assert tracker.documentos.get("test_contrato", []) == []
    
    def test_registrar_documento_error(self, tracker):
        """Test registrar documento con error"""
        # Iniciar documento
        doc_id = tracker.registrar_documento_iniciado(
            contrato="test_contrato",
            tipo=TipoDocumento.CONTRATO,
            nombre="Contrato Test"
        )
        
        # Registrar error
        tracker.registrar_documento_error(
            contrato="test_contrato",
            documento_id=doc_id,
            error="Error al generar documento"
        )
        
        doc = tracker.documentos["test_contrato"][0]
        assert doc.estado == EstadoDocumento.ERROR
        assert doc.observaciones == "Error: Error al generar documento"
    
    def test_obtener_documentos_contrato_existente(self, tracker, sample_documento):
        """Test obtener documentos de contrato existente"""
        tracker.documentos["test_contrato"] = [sample_documento]
        
        docs = tracker.obtener_documentos_contrato("test_contrato")
        assert len(docs) == 1
        assert docs[0] == sample_documento
    
    def test_obtener_documentos_contrato_no_existe(self, tracker):
        """Test obtener documentos de contrato que no existe"""
        docs = tracker.obtener_documentos_contrato("contrato_inexistente")
        assert docs == []
    
    def test_obtener_resumen_contrato_sin_documentos(self, tracker):
        """Test obtener resumen de contrato sin documentos"""
        resumen = tracker.obtener_resumen_contrato("contrato_vacio")
        
        expected = {
            'total_documentos': 0,
            'por_tipo': {},
            'por_estado': {},
            'ultimo_generado': None,
            'tamano_total_kb': 0.0,
            'documentos_generados_hoy': 0,
            'documentos_con_error': 0
        }
        
        assert resumen == expected
    
    def test_obtener_resumen_contrato_con_documentos(self, tracker, temp_dir):
        """Test obtener resumen de contrato con documentos"""
        # Crear archivos temporales
        archivo1 = os.path.join(temp_dir, "doc1.docx")
        archivo2 = os.path.join(temp_dir, "doc2.docx")
        
        with open(archivo1, 'w') as f:
            f.write("A" * 1024)  # 1KB
        with open(archivo2, 'w') as f:
            f.write("B" * 2048)  # 2KB
        
        # Crear documentos
        hoy = datetime.now()
        ayer = datetime.now().replace(day=hoy.day-1) if hoy.day > 1 else datetime.now().replace(month=hoy.month-1, day=28)
        
        docs = [
            DocumentoGenerado(
                id="doc1",
                tipo=TipoDocumento.CONTRATO,
                nombre="Contrato 1",
                ruta_archivo=archivo1,
                fecha_generacion=hoy,
                estado=EstadoDocumento.GENERADO,
                tamano_kb=1.0
            ),
            DocumentoGenerado(
                id="doc2",
                tipo=TipoDocumento.INVITACION,
                nombre="Invitación 1",
                ruta_archivo=archivo2,
                fecha_generacion=ayer,
                estado=EstadoDocumento.ERROR,
                tamano_kb=2.0
            ),
            DocumentoGenerado(
                id="doc3",
                tipo=TipoDocumento.CONTRATO,
                nombre="Contrato 2",
                ruta_archivo="/inexistente.docx",
                fecha_generacion=hoy,
                estado=EstadoDocumento.GENERADO,
                tamano_kb=0.5
            )
        ]
        
        tracker.documentos["test_contrato"] = docs
        
        resumen = tracker.obtener_resumen_contrato("test_contrato")
        
        assert resumen['total_documentos'] == 3
        assert resumen['por_tipo']['contrato'] == 2
        assert resumen['por_tipo']['invitacion'] == 1
        assert resumen['por_estado']['generado'] == 2
        assert resumen['por_estado']['error'] == 1
        assert resumen['documentos_generados_hoy'] == 2
        assert resumen['documentos_con_error'] == 1
        assert resumen['tamano_total_kb'] == 3.0  # Solo archivos existentes
        
        ultimo = resumen['ultimo_generado']
        assert ultimo['tipo'] in ['contrato', 'invitacion']
        assert ultimo['fecha'] == hoy.strftime('%Y-%m-%d %H:%M')
        assert ultimo['estado'] in ['generado', 'error']
    
    def test_generar_reporte_html_sin_documentos(self, tracker):
        """Test generar reporte HTML sin documentos"""
        html = tracker.generar_reporte_html("contrato_vacio")
        
        assert "No hay documentos generados" in html
        assert "contrato_vacio" not in html  # No debería mostrar nombre del contrato
    
    def test_generar_reporte_html_con_documentos(self, tracker, temp_dir):
        """Test generar reporte HTML con documentos"""
        # Crear archivo temporal
        archivo = os.path.join(temp_dir, "test.docx")
        with open(archivo, 'w') as f:
            f.write("Test content")
        
        # Crear documento
        doc = DocumentoGenerado(
            id="doc1",
            tipo=TipoDocumento.CONTRATO,
            nombre="Contrato Test",
            ruta_archivo=archivo,
            fecha_generacion=datetime(2024, 1, 15, 10, 30),
            estado=EstadoDocumento.GENERADO,
            tamano_kb=125.5,
            observaciones="Documento de prueba",
            plantilla_usada="plantilla_contrato.docx"
        )
        
        tracker.documentos["test_contrato"] = [doc]
        
        html = tracker.generar_reporte_html("test_contrato")
        
        assert "test_contrato" in html
        assert "Contrato Test" in html
        assert "2024-01-15" in html
        assert "10:30" in html
        assert "GENERADO" in html
        assert "125.5 KB" in html
        assert "plantilla_contrato.docx" in html
        assert "Documento de prueba" in html
        assert "📋" in html  # Icono de contrato
    
    def test_buscar_documento_existente(self, tracker, sample_documento):
        """Test buscar documento existente"""
        tracker.documentos["test_contrato"] = [sample_documento]
        
        doc = tracker._buscar_documento("test_contrato", "doc123")
        assert doc == sample_documento
    
    def test_buscar_documento_no_existe(self, tracker):
        """Test buscar documento que no existe"""
        doc = tracker._buscar_documento("test_contrato", "inexistente")
        assert doc is None
    
    def test_obtener_tamano_archivo_existente(self, tracker, temp_dir):
        """Test obtener tamaño de archivo existente"""
        archivo = os.path.join(temp_dir, "test.txt")
        with open(archivo, 'w') as f:
            f.write("A" * 1024)  # 1KB
        
        tamano = tracker._obtener_tamano_archivo(archivo)
        assert tamano == 1.0  # 1KB
    
    def test_obtener_tamano_archivo_no_existe(self, tracker):
        """Test obtener tamaño de archivo que no existe"""
        tamano = tracker._obtener_tamano_archivo("/archivo/inexistente.txt")
        assert tamano == 0.0


class TestIntegradorResumen:
    """Tests para la clase IntegradorResumen"""
    
    @pytest.fixture
    def main_window_mock(self):
        """Mock de ventana principal"""
        mock = Mock()
        mock.controlador_json = Mock()
        mock.controlador_fases = Mock()
        mock.comboBox = Mock()
        mock.comboBox.currentText.return_value = "contrato_test"
        
        # Simular tabs
        mock.tabWidget = Mock(spec=QTabWidget)
        
        # Simular botones
        mock.btn_generar_fichero_resumen = Mock(spec=QPushButton)
        mock.btn_actualizar_resumen = Mock(spec=QPushButton)
        
        # Simular tabla
        mock.Tabla_seguimiento = Mock(spec=QTableWidget)
        
        # Simular área de texto
        mock.textEdit_resumen = Mock(spec=QTextEdit)
        
        # Simular cronograma
        mock.cronograma_fases_timeline = Mock(spec=QGraphicsView)
        mock.cronograma_fases_timeline.scene.return_value = Mock(spec=QGraphicsScene)
        
        # Simular findChild
        def mock_find_child(widget_type, name=None):
            if name == 'btn_generar_fichero_resumen':
                return mock.btn_generar_fichero_resumen
            elif name == 'btn_actualizar_resumen':
                return mock.btn_actualizar_resumen
            elif name == 'Tabla_seguimiento':
                return mock.Tabla_seguimiento
            elif name == 'cronograma_fases_timeline':
                return mock.cronograma_fases_timeline
            return None
        
        mock.findChild = mock_find_child
        mock.findChildren.return_value = [mock.tabWidget]
        
        return mock
    
    @pytest.fixture
    def integrador(self, main_window_mock):
        """Fixture de integrador"""
        return IntegradorResumen(main_window_mock)
    
    def test_init_integrador(self, main_window_mock):
        """Test inicialización del integrador"""
        integrador = IntegradorResumen(main_window_mock)
        
        assert integrador.main_window == main_window_mock
        assert integrador.widget_resumen is None
        assert integrador.tab_index is None
    
    def test_obtener_nombre_carpeta_actual_desde_json(self, integrador):
        """Test obtener nombre carpeta desde JSON"""
        # Simular datos del JSON
        integrador.main_window.controlador_json.leer_contrato_completo.return_value = {
            'nombreCarpeta': 'carpeta_real_123'
        }
        
        resultado = integrador._obtener_nombre_carpeta_actual("contrato_test")
        
        assert resultado == "carpeta_real_123"
        integrador.main_window.controlador_json.leer_contrato_completo.assert_called_once_with("contrato_test")
    
    def test_obtener_nombre_carpeta_actual_sin_json(self, integrador):
        """Test obtener nombre carpeta sin datos JSON"""
        # Simular que no hay datos JSON
        integrador.main_window.controlador_json.leer_contrato_completo.return_value = None
        
        resultado = integrador._obtener_nombre_carpeta_actual("contrato_test")
        
        assert resultado == "contrato_test"
    
    def test_obtener_nombre_carpeta_actual_error(self, integrador):
        """Test obtener nombre carpeta con error"""
        # Simular error
        integrador.main_window.controlador_json.leer_contrato_completo.side_effect = Exception("Error JSON")
        
        resultado = integrador._obtener_nombre_carpeta_actual("contrato_test")
        
        assert resultado == "contrato_test"
    
    def test_integrar_en_aplicacion_exitoso(self, integrador):
        """Test integración exitosa en aplicación"""
        with patch.object(integrador, '_conectar_senales') as mock_conectar:
            resultado = integrador.integrar_en_aplicacion()
            
            assert resultado is True
            mock_conectar.assert_called_once()
    
    def test_integrar_en_aplicacion_error(self, integrador):
        """Test error al integrar en aplicación"""
        with patch.object(integrador, '_conectar_senales', side_effect=Exception("Error")):
            resultado = integrador.integrar_en_aplicacion()
            
            assert resultado is False
    
    def test_encontrar_tab_widget_por_atributo(self, integrador):
        """Test encontrar QTabWidget por atributo"""
        tab_widget = integrador._encontrar_tab_widget()
        
        assert tab_widget == integrador.main_window.tabWidget
    
    def test_encontrar_tab_widget_por_busqueda(self, integrador):
        """Test encontrar QTabWidget por búsqueda recursiva"""
        # Quitar atributo directo
        delattr(integrador.main_window, 'tabWidget')
        
        # Simular findChildren
        mock_tab_widget = Mock(spec=QTabWidget)
        integrador.main_window.findChildren.return_value = [mock_tab_widget]
        
        tab_widget = integrador._encontrar_tab_widget()
        
        assert tab_widget == mock_tab_widget
    
    def test_encontrar_tab_widget_no_existe(self, integrador):
        """Test cuando no se encuentra QTabWidget"""
        # Quitar atributo directo y simular búsqueda vacía
        delattr(integrador.main_window, 'tabWidget')
        integrador.main_window.findChildren.return_value = []
        
        tab_widget = integrador._encontrar_tab_widget()
        
        assert tab_widget is None
    
    def test_conectar_senales(self, integrador):
        """Test conectar señales"""
        with patch.object(integrador, '_conectar_botones_ui') as mock_botones:
            integrador._conectar_senales()
            
            mock_botones.assert_called_once()
    
    def test_conectar_botones_ui_exitoso(self, integrador):
        """Test conectar botones UI exitosamente"""
        with patch.object(integrador, '_agregar_cronograma_visual'):
            integrador._conectar_botones_ui()
            
            # Verificar que se desconectaron y reconectaron los botones
            integrador.main_window.btn_generar_fichero_resumen.clicked.disconnect.assert_called()
            integrador.main_window.btn_actualizar_resumen.clicked.disconnect.assert_called()
            integrador.main_window.btn_generar_fichero_resumen.clicked.connect.assert_called()
            integrador.main_window.btn_actualizar_resumen.clicked.connect.assert_called()
    
    def test_conectar_botones_ui_botones_no_encontrados(self, integrador):
        """Test conectar botones cuando no se encuentran"""
        # Simular que no se encuentran botones
        integrador.main_window.findChild = Mock(return_value=None)
        delattr(integrador.main_window, 'btn_generar_fichero_resumen')
        delattr(integrador.main_window, 'btn_actualizar_resumen')
        
        with patch.object(integrador, '_agregar_cronograma_visual'):
            integrador._conectar_botones_ui()
            
            # No debería haber errores, solo mensajes de log
    
    def test_reconectar_botones_si_es_necesario(self, integrador):
        """Test reconectar botones públicamente"""
        with patch.object(integrador, '_conectar_botones_ui') as mock_conectar:
            integrador.reconectar_botones_si_es_necesario()
            
            mock_conectar.assert_called_once()
    
    def test_test_botones_resumen(self, integrador):
        """Test método de prueba de botones"""
        with patch.object(integrador, '_on_actualizar_resumen') as mock_actualizar:
            with patch.object(integrador, '_on_generar_fichero_resumen') as mock_generar:
                integrador.test_botones_resumen()
                
                mock_actualizar.assert_called_once()
                mock_generar.assert_called_once()
    
    def test_test_botones_resumen_con_error(self, integrador):
        """Test método de prueba de botones con error"""
        with patch.object(integrador, '_on_actualizar_resumen', side_effect=Exception("Error")):
            with patch.object(integrador, '_on_generar_fichero_resumen'):
                # No debería fallar, solo imprimir error
                integrador.test_botones_resumen()
    
    def test_test_tabla_seguimiento_existente(self, integrador):
        """Test tabla de seguimiento existente"""
        mock_tabla = Mock(spec=QTableWidget)
        integrador.main_window.findChild = Mock(return_value=mock_tabla)
        
        integrador.test_tabla_seguimiento()
        
        mock_tabla.setRowCount.assert_called_with(3)
        mock_tabla.setColumnCount.assert_called_with(3)
        mock_tabla.setHorizontalHeaderLabels.assert_called_with(['Test1', 'Test2', 'Test3'])
        assert mock_tabla.setItem.call_count == 9  # 3x3 grid
    
    def test_test_tabla_seguimiento_no_existe(self, integrador):
        """Test tabla de seguimiento no existe"""
        integrador.main_window.findChild = Mock(return_value=None)
        integrador.main_window.findChildren.return_value = []
        
        # No debería fallar
        integrador.test_tabla_seguimiento()
    
    def test_on_anchor_clicked_archivo_local_windows(self, integrador):
        """Test clic en enlace de archivo local en Windows"""
        with patch('platform.system', return_value="Windows"):
            with patch('os.path.exists', return_value=True):
                with patch('os.startfile') as mock_startfile:
                    url = QUrl("file:///C:/test/documento.pdf")
                    
                    integrador._on_anchor_clicked(url)
                    
                    expected_path = "C:\\test\\documento.pdf"
                    mock_startfile.assert_called_once_with(expected_path)
    
    def test_on_anchor_clicked_archivo_no_existe(self, integrador):
        """Test clic en enlace de archivo que no existe"""
        with patch('platform.system', return_value="Windows"):
            with patch('os.path.exists', return_value=False):
                with patch('controladores.controlador_resumen.QMessageBox.warning') as mock_warning:
                    url = QUrl("file:///C:/test/inexistente.pdf")
                    
                    integrador._on_anchor_clicked(url)
                    
                    mock_warning.assert_called_once()
    
    def test_on_anchor_clicked_error_abriendo_archivo(self, integrador):
        """Test error al abrir archivo"""
        with patch('platform.system', return_value="Windows"):
            with patch('os.path.exists', return_value=True):
                with patch('os.startfile', side_effect=Exception("Error")):
                    with patch('controladores.controlador_resumen.QMessageBox.warning') as mock_warning:
                        url = QUrl("file:///C:/test/documento.pdf")
                        
                        integrador._on_anchor_clicked(url)
                        
                        mock_warning.assert_called()
    
    def test_on_anchor_clicked_enlace_externo(self, integrador):
        """Test clic en enlace externo"""
        url = QUrl("https://www.example.com")
        
        # No debería fallar, solo imprimir log
        integrador._on_anchor_clicked(url)
    
    def test_agregar_cronograma_visual_existente(self, integrador):
        """Test agregar cronograma visual cuando existe"""
        mock_view = Mock(spec=QGraphicsView)
        integrador.main_window.findChild = Mock(return_value=mock_view)
        
        integrador._agregar_cronograma_visual()
        
        # Verificar que se configuró el QGraphicsView
        mock_view.setRenderHints.assert_called()
        mock_view.setDragMode.assert_called()
    
    def test_agregar_cronograma_visual_no_existe(self, integrador):
        """Test agregar cronograma cuando no existe"""
        integrador.main_window.findChild = Mock(return_value=None)
        
        # No debería fallar
        integrador._agregar_cronograma_visual()
    
    def test_actualizar_cronograma_visual_con_datos(self, integrador):
        """Test actualizar cronograma visual con datos"""
        mock_view = Mock(spec=QGraphicsView)
        mock_scene = Mock(spec=QGraphicsScene)
        mock_view.scene.return_value = mock_scene
        integrador.main_window.findChild = Mock(return_value=mock_view)
        
        # Simular datos en cache
        integrador._datos_firmas_cache = {
            'CREACION': {
                'fecha_creacion': '2024-01-15',
                'firmas': [{'fecha': '2024-01-16'}]
            }
        }
        integrador._firmantes_unicos_cache = ['Firmante 1']
        
        with patch.object(integrador, '_dibujar_timeline_firmas') as mock_dibujar:
            integrador._actualizar_cronograma_visual("contrato_test")
            
            mock_scene.clear.assert_called()
            mock_dibujar.assert_called_once()
    
    def test_actualizar_cronograma_visual_sin_datos(self, integrador):
        """Test actualizar cronograma visual sin datos"""
        mock_view = Mock(spec=QGraphicsView)
        mock_scene = Mock(spec=QGraphicsScene)
        mock_view.scene.return_value = mock_scene
        integrador.main_window.findChild = Mock(return_value=mock_view)
        
        # Sin datos en cache
        integrador._datos_firmas_cache = {}
        
        integrador._actualizar_cronograma_visual("contrato_test")
        
        mock_scene.clear.assert_called()
        mock_scene.addText.assert_called()
    
    def test_dibujar_timeline_firmas(self, integrador):
        """Test dibujar timeline de firmas"""
        mock_scene = Mock(spec=QGraphicsScene)
        
        datos_firmas = {
            'CREACION': {
                'fecha_creacion': '2024-01-15',
                'firmas': [{'fecha': '2024-01-16'}]
            },
            'INICIO': {
                'fecha_creacion': '2024-01-20'
                # Sin firmas
            }
        }
        firmantes_unicos = ['Firmante 1']
        
        integrador._dibujar_timeline_firmas(mock_scene, datos_firmas, firmantes_unicos)
        
        # Verificar que se añadieron elementos al scene
        assert mock_scene.addRect.call_count >= 2  # Al menos 2 fases
        assert mock_scene.addText.call_count >= 2  # Títulos y leyenda


@pytest.mark.integration
class TestIntegrationResumen:
    """Tests de integración para el sistema de resumen"""
    
    @pytest.fixture
    def temp_env(self):
        """Entorno temporal completo"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_flujo_completo_documentos(self, temp_env):
        """Test flujo completo de gestión de documentos"""
        # 1. Crear tracker
        tracker = TrackerDocumentos(ruta_base=temp_env)
        
        # 2. Registrar documento iniciado
        doc_id = tracker.registrar_documento_iniciado(
            contrato="contrato_integration",
            tipo=TipoDocumento.CONTRATO,
            nombre="Contrato Integration Test",
            plantilla="plantilla_test.docx"
        )
        
        assert len(doc_id) == 8
        assert "contrato_integration" in tracker.documentos
        
        # 3. Simular generación exitosa
        archivo_test = os.path.join(temp_env, "contrato_generado.docx")
        with open(archivo_test, 'w') as f:
            f.write("Contenido del contrato" * 100)  # ~2KB
        
        tracker.registrar_documento_completado(
            contrato="contrato_integration",
            documento_id=doc_id,
            ruta_archivo=archivo_test,
            observaciones="Documento generado exitosamente"
        )
        
        # 4. Verificar estado final
        docs = tracker.obtener_documentos_contrato("contrato_integration")
        assert len(docs) == 1
        
        doc = docs[0]
        assert doc.estado == EstadoDocumento.GENERADO
        assert doc.ruta_archivo == archivo_test
        assert doc.tamano_kb > 1.0  # Al menos 1KB
        assert doc.observaciones == "Documento generado exitosamente"
        
        # 5. Obtener resumen
        resumen = tracker.obtener_resumen_contrato("contrato_integration")
        assert resumen['total_documentos'] == 1
        assert resumen['por_tipo']['contrato'] == 1
        assert resumen['por_estado']['generado'] == 1
        assert resumen['tamano_total_kb'] > 1.0
        
        # 6. Generar reporte HTML
        html = tracker.generar_reporte_html("contrato_integration")
        assert "contrato_integration" in html
        assert "Contrato Integration Test" in html
        assert "GENERADO" in html
        
        # 7. Verificar persistencia
        assert os.path.exists(tracker.archivo_historial)
        
        # 8. Crear nuevo tracker y verificar carga
        tracker2 = TrackerDocumentos(ruta_base=temp_env)
        docs2 = tracker2.obtener_documentos_contrato("contrato_integration")
        assert len(docs2) == 1
        assert docs2[0].nombre == "Contrato Integration Test"
    
    def test_integracion_con_main_window_mock(self, temp_env):
        """Test integración con ventana principal simulada"""
        # Crear mock de ventana principal más realista
        main_window = Mock()
        
        # Configurar controlador JSON
        main_window.controlador_json = Mock()
        main_window.controlador_json.leer_contrato_completo.return_value = {
            'nombreCarpeta': 'carpeta_test_123',
            'datos_contrato': {'descripcion': 'Test contract'}
        }
        
        # Configurar ComboBox
        main_window.comboBox = Mock()
        main_window.comboBox.currentText.return_value = "contrato_test"
        
        # Configurar botones
        main_window.btn_generar_fichero_resumen = Mock(spec=QPushButton)
        main_window.btn_actualizar_resumen = Mock(spec=QPushButton)
        
        # Configurar findChild para devolver botones
        def mock_find_child(widget_type, name=None):
            if name == 'btn_generar_fichero_resumen':
                return main_window.btn_generar_fichero_resumen
            elif name == 'btn_actualizar_resumen':
                return main_window.btn_actualizar_resumen
            return None
        
        main_window.findChild = mock_find_child
        
        # Crear integrador
        integrador = IntegradorResumen(main_window)
        
        # Test integración
        resultado = integrador.integrar_en_aplicacion()
        assert resultado is True
        
        # Test obtener nombre de carpeta
        nombre_carpeta = integrador._obtener_nombre_carpeta_actual("contrato_test")
        assert nombre_carpeta == "carpeta_test_123"
        
        # Test reconexión de botones
        integrador.reconectar_botones_si_es_necesario()
        
        # Verificar que se intentó conectar botones
        main_window.btn_generar_fichero_resumen.clicked.connect.assert_called()
        main_window.btn_actualizar_resumen.clicked.connect.assert_called()
    
    def test_manejo_errores_y_recuperacion(self, temp_env):
        """Test manejo de errores y recuperación del sistema"""
        tracker = TrackerDocumentos(ruta_base=temp_env)
        
        # 1. Registrar documento iniciado
        doc_id = tracker.registrar_documento_iniciado(
            contrato="contrato_error_test",
            tipo=TipoDocumento.LIQUIDACION,
            nombre="Liquidación con Error"
        )
        
        # 2. Simular error en generación
        tracker.registrar_documento_error(
            contrato="contrato_error_test",
            documento_id=doc_id,
            error="Error simulado en generación"
        )
        
        # 3. Verificar estado de error
        docs = tracker.obtener_documentos_contrato("contrato_error_test")
        assert len(docs) == 1
        assert docs[0].estado == EstadoDocumento.ERROR
        assert "Error simulado" in docs[0].observaciones
        
        # 4. Intentar recuperación - registrar nuevo documento
        doc_id_2 = tracker.registrar_documento_iniciado(
            contrato="contrato_error_test",
            tipo=TipoDocumento.LIQUIDACION,
            nombre="Liquidación Recuperada"
        )
        
        # 5. Completar exitosamente
        archivo_recuperado = os.path.join(temp_env, "liquidacion_ok.docx")
        with open(archivo_recuperado, 'w') as f:
            f.write("Liquidación generada correctamente")
        
        tracker.registrar_documento_completado(
            contrato="contrato_error_test",
            documento_id=doc_id_2,
            ruta_archivo=archivo_recuperado,
            observaciones="Recuperación exitosa"
        )
        
        # 6. Verificar estado final
        resumen = tracker.obtener_resumen_contrato("contrato_error_test")
        assert resumen['total_documentos'] == 2
        assert resumen['documentos_con_error'] == 1
        assert resumen['por_estado']['error'] == 1
        assert resumen['por_estado']['generado'] == 1
        
        # 7. Verificar reporte HTML incluye ambos documentos
        html = tracker.generar_reporte_html("contrato_error_test")
        assert "Liquidación con Error" in html
        assert "Liquidación Recuperada" in html
        assert "ERROR" in html
        assert "GENERADO" in html