"""
Fixtures compartidas para todos los tests de Generador de Actas ADIF
"""
import pytest
import json
import tempfile
import shutil
import os
from datetime import datetime, date
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock, patch
from faker import Faker

fake = Faker('es_ES')


@pytest.fixture
def sample_empresa_data():
    """Datos de empresa de prueba"""
    return {
        "nombre": "CONSTRUCTORA EJEMPLO S.L.",
        "nif": "B12345678",
        "email": "contacto@ejemplo.com", 
        "contacto": "Juan Pérez García",
        "ofertas": "45000.00"
    }


@pytest.fixture
def sample_contrato_data():
    """Datos de contrato de prueba completos"""
    return {
        "nombreObra": "OBRAS DE REPARACIÓN DE EJEMPLO",
        "numeroExpediente": "EXP-2024-001",
        "tipoActuacion": "Mantenimiento",
        "plazoEjecucion": "30",
        "basePresupuesto": "50000.00",
        "precioAdjudicacion": "45000.00",
        "fechaCreacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fechaAdjudicacion": "2024-01-15",
        "organoContratacion": "ADIF Alta Velocidad",
        "objeto": "Reparación de instalaciones",
        "justificacion": "Necesario para el mantenimiento",
        "nombreCarpeta": "OBRAS_REPARACION_EJEMPLO",
        "empresas": []
    }


@pytest.fixture
def sample_json_data(sample_contrato_data, sample_empresa_data):
    """Estructura JSON completa de prueba"""
    contrato = sample_contrato_data.copy()
    contrato["empresas"] = [sample_empresa_data]
    
    return {
        "firmantes": {
            "firmanteConforme": "Pablo Martín Fernández",
            "cargoConforme": "Técnico de Mantenimiento",
            "firmantePropone": "María García López", 
            "cargoPropone": "Jefe de Proyecto",
            "firmanteAprueba": "Carlos Ruiz Sánchez",
            "cargoAprueba": "Director Técnico"
        },
        "obras": [contrato]
    }


@pytest.fixture
def temp_json_file(sample_json_data):
    """Archivo JSON temporal para tests"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(sample_json_data, f, ensure_ascii=False, indent=2)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture  
def temp_directory():
    """Directorio temporal para tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_pyqt5_widgets():
    """Mock de widgets PyQt5 para tests unitarios"""
    with patch('PyQt5.QtWidgets.QWidget') as mock_widget, \
         patch('PyQt5.QtWidgets.QMainWindow') as mock_main_window, \
         patch('PyQt5.QtWidgets.QLineEdit') as mock_line_edit, \
         patch('PyQt5.QtWidgets.QSpinBox') as mock_spinbox, \
         patch('PyQt5.QtWidgets.QComboBox') as mock_combobox, \
         patch('PyQt5.QtWidgets.QTableWidget') as mock_table, \
         patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
        
        # Configurar mocks básicos
        mock_line_edit.return_value.text.return_value = ""
        mock_spinbox.return_value.value.return_value = 0
        mock_combobox.return_value.currentText.return_value = ""
        mock_table.return_value.rowCount.return_value = 0
        
        yield {
            'widget': mock_widget,
            'main_window': mock_main_window,
            'line_edit': mock_line_edit,
            'spinbox': mock_spinbox,
            'combobox': mock_combobox,
            'table': mock_table,
            'msgbox': mock_msgbox
        }


@pytest.fixture
def mock_file_system():
    """Mock del sistema de archivos"""
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open', create=True) as mock_open, \
         patch('os.listdir') as mock_listdir:
        
        # Configuración por defecto
        mock_exists.return_value = True
        mock_makedirs.return_value = None
        mock_listdir.return_value = []
        
        yield {
            'exists': mock_exists,
            'makedirs': mock_makedirs,
            'open': mock_open,
            'listdir': mock_listdir
        }


@pytest.fixture
def sample_pdf_content():
    """Contenido PDF simulado"""
    return b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n%%EOF'


@pytest.fixture
def sample_word_document():
    """Documento Word simulado"""
    return b'PK\x03\x04...'  # Simulación de archivo ZIP/DOCX


@pytest.fixture
def mock_controlador_json():
    """Mock del controlador JSON"""
    mock = Mock()
    mock.leer_contrato_completo.return_value = {}
    mock.actualizar_contrato.return_value = True
    mock.guardar_datos.return_value = True
    mock.obtener_firmantes.return_value = {}
    mock.listar_contratos.return_value = []
    return mock


@pytest.fixture
def mock_main_window():
    """Mock de ventana principal"""
    mock = Mock()
    mock.comboBox.currentText.return_value = "Contrato de Prueba"
    mock.controlador_json = Mock()
    mock.controlador_documentos = Mock()
    return mock


@pytest.fixture
def sample_empresas_list():
    """Lista de empresas de prueba"""
    return [
        {
            "nombre": "EMPRESA UNO S.L.",
            "nif": "B11111111",
            "email": "uno@empresa.com",
            "contacto": "Juan Uno",
            "ofertas": "40000.00"
        },
        {
            "nombre": "EMPRESA DOS S.A.",
            "nif": "B22222222", 
            "email": "dos@empresa.com",
            "contacto": "María Dos",
            "ofertas": "42000.00"
        },
        {
            "nombre": "EMPRESA TRES S.L.U.",
            "nif": "B33333333",
            "email": "tres@empresa.com", 
            "contacto": "Carlos Tres",
            "ofertas": "38000.00"
        }
    ]


@pytest.fixture
def sample_liquidacion_data():
    """Datos de liquidación de prueba"""
    return {
        "certBase": "45000.00",
        "certIva": "9450.00", 
        "certTotal": "54450.00",
        "adicionalBaseLiquidacion": "0.00",
        "adicionalIvaLiquidacion": "0.00",
        "saldoBaseLiquidacion": "0.00",
        "saldoIvaLiquidacion": "0.00",
        "liquidacionAFavorAdifBase": "0.00",
        "adifIvaAFavor": "0.00"
    }


@pytest.fixture(scope="session")
def plantillas_directory():
    """Directorio de plantillas de prueba"""
    temp_dir = tempfile.mkdtemp()
    
    # Crear archivos de plantilla simulados
    plantillas = [
        "plantilla_acta_inicio.docx",
        "plantilla_cartas_invitacion.docx", 
        "plantilla_acta_adjudicacion.docx",
        "plantilla_contrato.docx"
    ]
    
    for plantilla in plantillas:
        plantilla_path = os.path.join(temp_dir, plantilla)
        with open(plantilla_path, 'wb') as f:
            f.write(b'PK\x03\x04...')  # Simulación de archivo DOCX
    
    yield temp_dir
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def fechas_contrato():
    """Fechas típicas de un contrato"""
    base_date = date(2024, 1, 15)
    return {
        "fechaProyecto": base_date.strftime("%Y-%m-%d"),
        "fechaAdjudicacion": base_date.strftime("%Y-%m-%d"), 
        "fechaInicio": (base_date.replace(month=2)).strftime("%Y-%m-%d"),
        "fechaReplanteo": (base_date.replace(month=2, day=20)).strftime("%Y-%m-%d"),
        "fechaRecepcion": (base_date.replace(month=6)).strftime("%Y-%m-%d"),
        "fechaFinal": (base_date.replace(month=6, day=30)).strftime("%Y-%m-%d")
    }


# Markers para organizar tests
pytestmark = [
    pytest.mark.unit
]