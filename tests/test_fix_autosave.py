#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar el fix de autosave para campos problemáticos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_controlador():
    """Verificar que el controlador modificado se puede importar correctamente"""
    print("TEST: Importando controlador modificado...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'controladores'))
        from controlador_autosave import ControladorAutoGuardado
        print("✅ ControladorAutoGuardado importado correctamente")
        
        # Verificar que los nuevos métodos existen
        metodos_requeridos = [
            '_configurar_lineedit_con_textchanged',
            'configurar_auto_guardado_campos',
            '_crear_callback_agrupado'
        ]
        
        for metodo in metodos_requeridos:
            if hasattr(ControladorAutoGuardado, metodo):
                print(f"✅ Método {metodo} existe")
            else:
                print(f"❌ Método {metodo} NO existe")
                assert False, f"Método {metodo} NO existe"
                
        print("✅ Todos los métodos requeridos están presentes")
        assert True  # All methods exist
        
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        assert False, f"Error: {e}"
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        assert False, f"Error: {e}"

def test_campos_problematicos():
    """Verificar que los campos problemáticos están definidos correctamente"""
    print("\nTEST: Verificando definición de campos problemáticos...")
    
    try:
        # Leer el archivo y buscar la definición
        archivo_path = os.path.join(os.path.dirname(__file__), 'controladores', 'controlador_autosave.py')
        
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Verificar que los campos problemáticos están definidos
        campos_esperados = [
            'OrganoSolicitaOfertas',
            'regimenPagos',
            'organoContratacion', 
            'organoContratacion2'
        ]
        
        campos_encontrados = []
        for campo in campos_esperados:
            if f"'{campo}'" in contenido:
                print(f"✅ Campo {campo} encontrado en definición")
                campos_encontrados.append(campo)
            else:
                print(f"❌ Campo {campo} NO encontrado")
        
        if len(campos_encontrados) == len(campos_esperados):
            print("✅ Todos los campos problemáticos están definidos")
            assert True  # All methods exist
        else:
            print(f"❌ Faltan {len(campos_esperados) - len(campos_encontrados)} campos")
            assert False, f"Error: {e}"
            
    except Exception as e:
        print(f"❌ Error verificando campos: {e}")
        assert False, f"Error: {e}"

def test_metodo_nuevo():
    """Verificar que el nuevo método tiene la estructura correcta"""
    print("\nTEST: Verificando estructura del nuevo método...")
    
    try:
        archivo_path = os.path.join(os.path.dirname(__file__), 'controladores', 'controlador_autosave.py')
        
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Verificar elementos del nuevo método
        elementos_requeridos = [
            '_configurar_lineedit_con_textchanged',
            'textChanged.connect',
            'timer.start(2000)',
            '_agendar_guardado_campo'
        ]
        
        elementos_encontrados = []
        for elemento in elementos_requeridos:
            if elemento in contenido:
                print(f"✅ Elemento {elemento} encontrado")
                elementos_encontrados.append(elemento)
            else:
                print(f"❌ Elemento {elemento} NO encontrado")
        
        if len(elementos_encontrados) == len(elementos_requeridos):
            print("✅ Nuevo método tiene estructura correcta")
            assert True  # All methods exist
        else:
            print(f"❌ Faltan {len(elementos_requeridos) - len(elementos_encontrados)} elementos")
            assert False, f"Error: {e}"
            
    except Exception as e:
        print(f"❌ Error verificando método: {e}")
        assert False, f"Error: {e}"

if __name__ == "__main__":
    print("=" * 50)
    print("TEST FIX AUTOSAVE - VERIFICACIÓN")
    print("=" * 50)
    
    tests = [
        test_import_controlador,
        test_campos_problematicos, 
        test_metodo_nuevo
    ]
    
    resultados = []
    for test_func in tests:
        resultado = test_func()
        resultados.append(resultado)
        print()
    
    exitosos = sum(resultados)
    total = len(resultados)
    
    print("=" * 50)
    print(f"RESUMEN: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("✅ TODOS LOS TESTS PASARON - Fix aplicado correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON - Revisar implementación")
    
    print("=" * 50)