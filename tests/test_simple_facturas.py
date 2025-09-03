#!/usr/bin/env python3
"""
Test simple para verificar que los componentes básicos funcionan
"""

import sys
import os
import tempfile
import json
from datetime import datetime
from unittest.mock import Mock, patch

# Añadir al path
sys.path.insert(0, os.path.dirname(__file__))

def test_enums_y_dataclasses():
    """Test básico de enums y dataclasses"""
    try:
        from controladores.controlador_resumen import (
            EstadoDocumento, TipoDocumento, DocumentoGenerado
        )
        
        # Test enums
        assert EstadoDocumento.GENERADO.value == "generado"
        assert TipoDocumento.CONTRATO.value == "contrato"
        
        # Test dataclass
        doc = DocumentoGenerado(
            id="test123",
            tipo=TipoDocumento.CONTRATO,
            nombre="Test Doc",
            ruta_archivo="/test.docx",
            fecha_generacion=datetime.now(),
            estado=EstadoDocumento.GENERADO,
            tamano_kb=100.0
        )
        
        assert doc.id == "test123"
        assert doc.tipo == TipoDocumento.CONTRATO
        print("✅ Test enums y dataclasses: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test enums y dataclasses: FAILED - {e}")
        return False

def test_tracker_documentos_basico():
    """Test básico del TrackerDocumentos"""
    try:
        from controladores.controlador_resumen import TrackerDocumentos, TipoDocumento
        
        # Crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = TrackerDocumentos(ruta_base=temp_dir)
            
            # Test inicialización
            assert tracker.ruta_base == temp_dir
            assert isinstance(tracker.documentos, dict)
            
            # Test registrar documento
            doc_id = tracker.registrar_documento_iniciado(
                contrato="test_contrato",
                tipo=TipoDocumento.CONTRATO,
                nombre="Contrato Test"
            )
            
            assert len(doc_id) == 8
            assert "test_contrato" in tracker.documentos
            assert len(tracker.documentos["test_contrato"]) == 1
            
            # Test obtener documentos
            docs = tracker.obtener_documentos_contrato("test_contrato")
            assert len(docs) == 1
            assert docs[0].nombre == "Contrato Test"
            
            print("✅ Test TrackerDocumentos básico: PASSED")
            return True
            
    except Exception as e:
        print(f"❌ Test TrackerDocumentos básico: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_controlador_facturas_mock():
    """Test del ControladorFacturasDirectas con mocks"""
    try:
        # Mock del sistema de rutas
        with patch('controladores.controlador_facturas_directas.rutas') as mock_rutas:
            # Usar directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_rutas.get_base_path.return_value = temp_dir
                mock_rutas.get_ruta_facturas_directas.return_value = os.path.join(temp_dir, "facturas.json")
                
                # Importar después del mock
                from controladores.controlador_facturas_directas import ControladorFacturasDirectas
                
                controlador = ControladorFacturasDirectas()
                
                # Test inicialización
                assert controlador.directorio_base == temp_dir
                assert controlador.archivo_json.endswith("facturas.json")
                
                # Test agregar factura
                datos_factura = {
                    "empresa": "Empresa Test",
                    "importe": 1500.50,
                    "categoria": "Agua",
                    "localidad": "Madrid"
                }
                
                resultado = controlador.agregar_factura(datos_factura)
                assert resultado is True
                
                # Test obtener facturas
                facturas = controlador.obtener_facturas()
                assert len(facturas) == 1
                assert facturas[0]["empresa"] == "Empresa Test"
                
                print("✅ Test ControladorFacturasDirectas mock: PASSED")
                return True
                
    except Exception as e:
        print(f"❌ Test ControladorFacturasDirectas mock: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests"""
    print("=" * 50)
    print("EJECUTANDO TESTS BÁSICOS")
    print("=" * 50)
    
    tests = [
        test_enums_y_dataclasses,
        test_tracker_documentos_basico,
        test_controlador_facturas_mock
    ]
    
    resultados = []
    for test in tests:
        resultados.append(test())
    
    print("=" * 50)
    print(f"RESULTADOS: {sum(resultados)}/{len(resultados)} tests pasaron")
    
    if all(resultados):
        print("🎉 TODOS LOS TESTS BÁSICOS PASARON!")
        return True
    else:
        print("⚠️ ALGUNOS TESTS FALLARON")
        return False

if __name__ == "__main__":
    main()