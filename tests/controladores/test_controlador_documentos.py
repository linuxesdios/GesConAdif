"""
Tests comprehensivos para controlador_documentos.py
Este es el archivo CRÍTICO con solo 7% de cobertura (1,616 líneas)
Objetivo: Alcanzar >85% de cobertura
"""
import pytest
import os
import sys
import tempfile
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from pathlib import Path

# Agregar el directorio principal al path  
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Mock de docx antes de importar
sys.modules['docx'] = MagicMock()
sys.modules['docx.Document'] = MagicMock()
sys.modules['docx.shared'] = MagicMock()

from controladores.controlador_documentos import ControladorDocumentos


class TestControladorDocumentosInicializacion:
    """Tests para inicialización del controlador"""
    
    @pytest.mark.unit
    def test_inicializacion_sin_main_window(self):
        """Test inicialización sin ventana principal"""
        controlador = ControladorDocumentos()
        assert controlador.main_window is None
        assert controlador.directorio_plantillas == "plantillas"
        assert controlador.gestor_archivos is None
    
    @pytest.mark.unit
    def test_inicializacion_con_main_window(self):
        """Test inicialización con ventana principal"""
        mock_window = Mock()
        mock_window.gestor_archivos_unificado = Mock()
        
        controlador = ControladorDocumentos(mock_window)
        assert controlador.main_window == mock_window
    
    @pytest.mark.unit
    def test_configurar_gestor_unificado_disponible(self):
        """Test configuración de gestor unificado disponible"""
        mock_window = Mock()
        mock_gestor = Mock()
        mock_window.gestor_archivos_unificado = mock_gestor
        
        controlador = ControladorDocumentos(mock_window)
        controlador._configurar_gestor_unificado()
        
        assert controlador.gestor_archivos == mock_gestor
    
    @pytest.mark.unit
    def test_configurar_gestor_unificado_no_disponible(self):
        """Test configuración sin gestor unificado"""
        mock_window = Mock()
        del mock_window.gestor_archivos_unificado  # Sin gestor
        
        controlador = ControladorDocumentos(mock_window)
        controlador._configurar_gestor_unificado()
        
        assert controlador.gestor_archivos is None
    
    @pytest.mark.unit
    @patch('controladores.controlador_documentos.TrackerDocumentos')
    def test_configurar_tracker_documentos_exitoso(self, mock_tracker):
        """Test configuración exitosa del tracker"""
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        controlador = ControladorDocumentos()
        controlador._configurar_tracker_documentos()
        
        assert controlador.tracker == mock_tracker_instance
    
    @pytest.mark.unit
    @patch('controladores.controlador_documentos.TrackerDocumentos')
    def test_configurar_tracker_documentos_error(self, mock_tracker):
        """Test error en configuración del tracker"""
        mock_tracker.side_effect = Exception("Error tracker")
        
        controlador = ControladorDocumentos()
        controlador._configurar_tracker_documentos()
        
        assert controlador.tracker is None


class TestObtenerNombreCarpeta:
    """Tests para _obtener_nombre_carpeta_actual"""
    
    @pytest.mark.unit
    def test_obtener_nombre_carpeta_desde_json_exitoso(self):
        """Test obtener nombre carpeta desde JSON exitosamente"""
        mock_window = Mock()
        mock_controlador_json = Mock()
        mock_window.controlador_json = mock_controlador_json
        
        # Simular datos del contrato
        contrato_data = {"nombreCarpeta": "CARPETA-ACTUALIZADA-2024"}
        mock_controlador_json.leer_contrato_completo.return_value = contrato_data
        
        controlador = ControladorDocumentos(mock_window)
        
        resultado = controlador._obtener_nombre_carpeta_actual("CONTRATO_TEST")
        
        assert resultado == "CARPETA-ACTUALIZADA-2024"
        mock_controlador_json.leer_contrato_completo.assert_called_once_with("CONTRATO_TEST")
    
    @pytest.mark.unit
    def test_obtener_nombre_carpeta_sin_nombre_carpeta_json(self):
        """Test fallback cuando no hay nombreCarpeta en JSON"""
        mock_window = Mock()
        mock_controlador_json = Mock()
        mock_window.controlador_json = mock_controlador_json
        
        # Simular datos sin nombreCarpeta
        contrato_data = {"nombreObra": "OBRA_SIN_CARPETA"}
        mock_controlador_json.leer_contrato_completo.return_value = contrato_data
        
        controlador = ControladorDocumentos(mock_window)
        
        resultado = controlador._obtener_nombre_carpeta_actual("CONTRATO_TEST")
        
        assert resultado == "CONTRATO_TEST"  # Fallback al nombre del contrato
    
    @pytest.mark.unit
    def test_obtener_nombre_carpeta_sin_controlador_json(self):
        """Test fallback cuando no hay controlador JSON"""
        mock_window = Mock()
        mock_window.controlador_json = None
        
        controlador = ControladorDocumentos(mock_window)
        
        resultado = controlador._obtener_nombre_carpeta_actual("CONTRATO_TEST")
        
        assert resultado == "CONTRATO_TEST"
    
    @pytest.mark.unit
    def test_obtener_nombre_carpeta_error_lectura(self):
        """Test manejo de error en lectura de JSON"""
        mock_window = Mock()
        mock_controlador_json = Mock()
        mock_window.controlador_json = mock_controlador_json
        
        # Simular error en lectura
        mock_controlador_json.leer_contrato_completo.side_effect = Exception("Error lectura")
        
        controlador = ControladorDocumentos(mock_window)
        
        resultado = controlador._obtener_nombre_carpeta_actual("CONTRATO_TEST")
        
        assert resultado == "CONTRATO_TEST"  # Fallback seguro


class TestTrackingDocumentos:
    """Tests para funciones de tracking de documentos"""
    
    @pytest.fixture
    def controlador_con_tracker(self):
        """Fixture con controlador y tracker configurado"""
        controlador = ControladorDocumentos()
        controlador.tracker = Mock()
        controlador.contract_name = "CONTRATO_TEST"
        controlador.TipoDocumento = Mock()
        return controlador
    
    @pytest.mark.unit
    def test_iniciar_tracking_documento_exitoso(self, controlador_con_tracker):
        """Test iniciar tracking exitosamente"""
        mock_doc_id = "doc_123"
        controlador_con_tracker.tracker.registrar_documento_iniciado.return_value = mock_doc_id
        
        resultado = controlador_con_tracker._iniciar_tracking_documento(
            "acta_inicio", "Acta de Inicio", "plantilla_acta.docx"
        )
        
        assert resultado == mock_doc_id
        controlador_con_tracker.tracker.registrar_documento_iniciado.assert_called_once_with(
            "CONTRATO_TEST", "acta_inicio", "Acta de Inicio", "plantilla_acta.docx"
        )
    
    @pytest.mark.unit
    def test_iniciar_tracking_documento_sin_tracker(self):
        """Test iniciar tracking sin tracker disponible"""
        controlador = ControladorDocumentos()
        controlador.tracker = None
        
        resultado = controlador._iniciar_tracking_documento("acta_inicio", "Acta")
        
        assert resultado is None
    
    @pytest.mark.unit
    def test_iniciar_tracking_documento_sin_contract_name(self):
        """Test iniciar tracking sin nombre de contrato"""
        controlador = ControladorDocumentos()
        controlador.tracker = Mock()
        # Sin contract_name
        
        resultado = controlador._iniciar_tracking_documento("acta_inicio", "Acta")
        
        assert resultado is None
    
    @pytest.mark.unit
    def test_completar_tracking_documento_exitoso(self, controlador_con_tracker):
        """Test completar tracking exitosamente"""
        controlador_con_tracker.tracker.marcar_documento_completado.return_value = True
        
        resultado = controlador_con_tracker._completar_tracking_documento(
            "doc_123", "/ruta/documento.pdf", "Generado correctamente"
        )
        
        assert resultado is True
        controlador_con_tracker.tracker.marcar_documento_completado.assert_called_once_with(
            "doc_123", "/ruta/documento.pdf", "Generado correctamente"
        )
    
    @pytest.mark.unit
    def test_completar_tracking_documento_error(self, controlador_con_tracker):
        """Test error al completar tracking"""
        controlador_con_tracker.tracker.marcar_documento_completado.side_effect = Exception("Error tracking")
        
        resultado = controlador_con_tracker._completar_tracking_documento("doc_123", "/ruta/doc.pdf")
        
        assert resultado is False
    
    @pytest.mark.unit
    def test_error_tracking_documento(self, controlador_con_tracker):
        """Test registrar error en tracking"""
        controlador_con_tracker.tracker.marcar_documento_error.return_value = True
        
        resultado = controlador_con_tracker._error_tracking_documento("doc_123", "Error generación")
        
        assert resultado is True
        controlador_con_tracker.tracker.marcar_documento_error.assert_called_once_with(
            "doc_123", "Error generación"
        )


class TestGeneracionDocumentos:
    """Tests para generación de documentos Word"""
    
    @pytest.fixture
    def controlador_con_mocks(self):
        """Fixture con controlador y mocks configurados"""
        mock_window = Mock()
        mock_controlador_json = Mock()
        mock_window.controlador_json = mock_controlador_json
        
        controlador = ControladorDocumentos(mock_window)
        controlador.tracker = Mock()
        
        return controlador, mock_window, mock_controlador_json
    
    @pytest.mark.unit
    @patch('controladores.controlador_documentos.Document')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_generar_documento_plantilla_existente(self, mock_makedirs, mock_exists, mock_document, controlador_con_mocks):
        """Test generación de documento con plantilla existente"""
        controlador, mock_window, mock_json = controlador_con_mocks
        
        # Configurar mocks
        mock_exists.return_value = True
        mock_doc_instance = Mock()
        mock_document.return_value = mock_doc_instance
        
        # Datos del contrato
        datos_contrato = {"nombreObra": "OBRA_TEST", "basePresupuesto": "50000"}
        mock_json.leer_contrato_completo.return_value = datos_contrato
        
        # Simular generación
        with patch.object(controlador, '_obtener_nombre_carpeta_actual', return_value="CARPETA_TEST"):
            resultado = controlador.generar_documento_word(
                "OBRA_TEST",
                "acta_inicio", 
                datos_contrato,
                "plantilla_acta_inicio.docx"
            )
        
        # Verificaciones
        mock_document.assert_called_once()
        mock_doc_instance.save.assert_called_once()
    
    @pytest.mark.unit
    @patch('os.path.exists')
    def test_generar_documento_plantilla_no_existente(self, mock_exists, controlador_con_mocks):
        """Test error cuando plantilla no existe"""
        controlador, mock_window, mock_json = controlador_con_mocks
        
        mock_exists.return_value = False
        
        resultado = controlador.generar_documento_word(
            "OBRA_TEST",
            "acta_inicio",
            {},
            "plantilla_inexistente.docx"
        )
        
        assert resultado is False
    
    @pytest.mark.unit
    @patch('controladores.controlador_documentos.Document')
    @patch('os.path.exists')  
    def test_generar_documento_error_word(self, mock_exists, mock_document, controlador_con_mocks):
        """Test error en generación de documento Word"""
        controlador, mock_window, mock_json = controlador_con_mocks
        
        mock_exists.return_value = True
        mock_document.side_effect = Exception("Error creando documento")
        
        resultado = controlador.generar_documento_word(
            "OBRA_TEST",
            "acta_inicio", 
            {},
            "plantilla_acta.docx"
        )
        
        assert resultado is False


class TestSustitucionVariables:
    """Tests para sustitución de variables en documentos"""
    
    @pytest.fixture
    def controlador_basico(self):
        """Controlador básico para tests de sustitución"""
        return ControladorDocumentos()
    
    @pytest.mark.unit
    def test_sustituir_variables_texto_simple(self, controlador_basico):
        """Test sustitución de variables en texto simple"""
        texto = "El presupuesto es @basePresupuesto@ euros"
        variables = {"basePresupuesto": "50000"}
        
        resultado = controlador_basico._sustituir_variables_texto(texto, variables)
        
        assert resultado == "El presupuesto es 50000 euros"
    
    @pytest.mark.unit
    def test_sustituir_variables_multiples(self, controlador_basico):
        """Test sustitución de múltiples variables"""
        texto = "Obra: @nombreObra@, Presupuesto: @basePresupuesto@, Plazo: @plazoEjecucion@ días"
        variables = {
            "nombreObra": "REPARACIÓN EDIFICIO",
            "basePresupuesto": "75000",
            "plazoEjecucion": "60"
        }
        
        resultado = controlador_basico._sustituir_variables_texto(texto, variables)
        
        esperado = "Obra: REPARACIÓN EDIFICIO, Presupuesto: 75000, Plazo: 60 días"
        assert resultado == esperado
    
    @pytest.mark.unit
    def test_sustituir_variables_no_encontradas(self, controlador_basico):
        """Test variables no encontradas en datos"""
        texto = "Variable existente: @nombreObra@, Variable inexistente: @variableInexistente@"
        variables = {"nombreObra": "OBRA_TEST"}
        
        resultado = controlador_basico._sustituir_variables_texto(texto, variables)
        
        # Las variables no encontradas deben quedarse como están
        assert "@variableInexistente@" in resultado
        assert "OBRA_TEST" in resultado
    
    @pytest.mark.unit
    def test_sustituir_variables_valores_vacios(self, controlador_basico):
        """Test sustitución con valores vacíos"""
        texto = "Valor: @valor@"
        variables = {"valor": ""}
        
        resultado = controlador_basico._sustituir_variables_texto(texto, variables)
        
        assert resultado == "Valor: "
    
    @pytest.mark.unit
    @patch('controladores.controlador_documentos.Document')
    def test_procesar_paragraph_con_variables(self, mock_document, controlador_basico):
        """Test procesamiento de párrafo con variables"""
        # Mock del párrafo
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "El presupuesto es @basePresupuesto@ euros"
        mock_paragraph.runs = [mock_run]
        
        variables = {"basePresupuesto": "50000"}
        
        controlador_basico._procesar_paragraph_con_variables(mock_paragraph, variables)
        
        # Verificar que el texto fue actualizado
        assert mock_run.text == "El presupuesto es 50000 euros"


class TestGeneracionFicheroResumen:
    """Tests específicos para generación de fichero de resumen"""
    
    @pytest.mark.unit
    @patch('controladores.controlador_documentos.Document')
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('controladores.controlador_documentos.datetime')
    def test_generar_fichero_resumen_exitoso(self, mock_datetime, mock_makedirs, mock_exists, mock_document):
        """Test generación exitosa de fichero resumen"""
        # Configurar mocks
        mock_exists.return_value = True
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        
        mock_doc_instance = Mock()
        mock_document.return_value = mock_doc_instance
        
        # Configurar controlador
        mock_window = Mock()
        mock_window.controlador_json.leer_contrato_completo.return_value = {"nombreCarpeta": "TEST_CARPETA"}
        mock_window.controlador_resumen._generar_resumen_con_fases.return_value = "<html>Resumen</html>"
        
        controlador = ControladorDocumentos(mock_window)
        
        with patch.object(controlador, '_obtener_nombre_carpeta_actual', return_value="TEST_CARPETA"):
            resultado = controlador.generar_fichero_resumen("CONTRATO_TEST", {"nombreObra": "TEST"})
        
        # Verificaciones
        assert resultado is not False  # Debería devolver ruta o True
        mock_document.assert_called_once()
        mock_doc_instance.save.assert_called_once()
    
    @pytest.mark.unit
    @patch('os.path.exists')
    def test_generar_fichero_resumen_sin_datos(self, mock_exists):
        """Test generación de resumen sin datos de contrato"""
        mock_exists.return_value = True
        
        controlador = ControladorDocumentos()
        
        resultado = controlador.generar_fichero_resumen("", {})
        
        assert resultado is False


class TestGeneracionCartasInvitacion:
    """Tests para generación de cartas de invitación"""
    
    @pytest.mark.unit
    @patch('controladores.controlador_documentos.Document')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_generar_cartas_invitacion_multiples_empresas(self, mock_makedirs, mock_exists, mock_document):
        """Test generación de cartas para múltiples empresas"""
        mock_exists.return_value = True
        mock_doc_instance = Mock()
        mock_document.return_value = mock_doc_instance
        
        # Datos de prueba
        empresas = [
            {"nombre": "EMPRESA A", "contacto": "Juan A"},
            {"nombre": "EMPRESA B", "contacto": "María B"}
        ]
        
        datos_contrato = {"nombreObra": "OBRA_TEST", "empresas": empresas}
        
        mock_window = Mock()
        mock_window.controlador_json.leer_contrato_completo.return_value = datos_contrato
        
        controlador = ControladorDocumentos(mock_window)
        
        with patch.object(controlador, '_obtener_nombre_carpeta_actual', return_value="CARPETA_TEST"):
            resultado = controlador.generar_cartas_invitacion("OBRA_TEST", datos_contrato)
        
        # Debe generar una carta por empresa
        assert mock_document.call_count == len(empresas)
    
    @pytest.mark.unit
    def test_generar_cartas_invitacion_sin_empresas(self):
        """Test generación sin empresas"""
        datos_contrato = {"nombreObra": "OBRA_TEST", "empresas": []}
        
        controlador = ControladorDocumentos()
        
        resultado = controlador.generar_cartas_invitacion("OBRA_TEST", datos_contrato)
        
        assert resultado is False


class TestValidacionDatos:
    """Tests para validación de datos de entrada"""
    
    @pytest.mark.unit
    def test_validar_datos_contrato_completos(self):
        """Test validación de datos completos"""
        datos_completos = {
            "nombreObra": "OBRA_COMPLETA",
            "basePresupuesto": "50000",
            "plazoEjecucion": "60",
            "empresas": [{"nombre": "EMPRESA_TEST"}]
        }
        
        controlador = ControladorDocumentos()
        resultado = controlador._validar_datos_basicos_contrato(datos_completos)
        
        assert resultado is True
    
    @pytest.mark.unit
    def test_validar_datos_contrato_incompletos(self):
        """Test validación con datos faltantes"""
        datos_incompletos = {
            "nombreObra": "",  # Faltante
            "basePresupuesto": "50000"
        }
        
        controlador = ControladorDocumentos()
        resultado = controlador._validar_datos_basicos_contrato(datos_incompletos)
        
        assert resultado is False
    
    @pytest.mark.unit
    def test_validar_plantilla_existente(self):
        """Test validación de existencia de plantilla"""
        with patch('os.path.exists', return_value=True):
            controlador = ControladorDocumentos()
            resultado = controlador._validar_plantilla_existe("plantilla_test.docx")
            assert resultado is True
        
        with patch('os.path.exists', return_value=False):
            controlador = ControladorDocumentos()
            resultado = controlador._validar_plantilla_existe("plantilla_inexistente.docx")
            assert resultado is False


class TestIntegracionControladorDocumentos:
    """Tests de integración para flujos completos"""
    
    @pytest.mark.integration
    @patch('controladores.controlador_documentos.Document')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_flujo_completo_generacion_acta_inicio(self, mock_makedirs, mock_exists, mock_document):
        """Test flujo completo de generación de acta de inicio"""
        # Configurar mocks
        mock_exists.return_value = True
        mock_doc_instance = Mock()
        mock_document.return_value = mock_doc_instance
        
        # Configurar datos
        datos_contrato = {
            "nombreObra": "REPARACIÓN INTEGRAL EDIFICIO",
            "basePresupuesto": "75000.00",
            "plazoEjecucion": "90",
            "fechaAdjudicacion": "2024-01-15",
            "nombreCarpeta": "REPARACION_INTEGRAL_2024"
        }
        
        # Configurar controlador con mocks
        mock_window = Mock()
        mock_json = Mock()
        mock_window.controlador_json = mock_json
        mock_json.leer_contrato_completo.return_value = datos_contrato
        
        controlador = ControladorDocumentos(mock_window)
        controlador.tracker = Mock()
        controlador.tracker.registrar_documento_iniciado.return_value = "doc_123"
        controlador.tracker.marcar_documento_completado.return_value = True
        
        # Ejecutar generación
        resultado = controlador.generar_acta_inicio("REPARACIÓN INTEGRAL EDIFICIO", datos_contrato)
        
        # Verificaciones
        mock_document.assert_called_once()
        mock_doc_instance.save.assert_called_once()
        
        # Verificar que el tracking se completó
        controlador.tracker.registrar_documento_iniciado.assert_called_once()
        controlador.tracker.marcar_documento_completado.assert_called_once()
    
    @pytest.mark.integration 
    def test_flujo_error_recuperacion_graceful(self):
        """Test recuperación elegante ante errores"""
        # Simular error en cada etapa del proceso
        mock_window = Mock()
        mock_window.controlador_json.leer_contrato_completo.side_effect = Exception("Error JSON")
        
        controlador = ControladorDocumentos(mock_window)
        
        # No debe lanzar excepción, debe retornar False
        resultado = controlador.generar_documento_word("TEST", "acta", {}, "plantilla.docx")
        
        assert resultado is False


# Marks para organizar los tests
pytestmark = [pytest.mark.critical, pytest.mark.unit]