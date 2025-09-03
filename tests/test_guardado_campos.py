#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para diagnosticar problema de guardado de campos específicos
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar solo el gestor JSON directamente
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'controladores'))
    from controlador_json import GestorJsonUnificado
except ImportError as e:
    print(f"Error importando: {e}")
    # Test directo con JSON si no se puede importar
    GestorJsonUnificado = None

def test_guardado_campos():
    """Test para identificar el problema de guardado"""
    print("INICIANDO TEST DE GUARDADO DE CAMPOS")
    print("=" * 50)
    
    json_path = "H:/generador_actas/BaseDatos.json"
    
    if GestorJsonUnificado is None:
        print("⚠️ No se pudo importar GestorJsonUnificado, usando test directo JSON")
        test_directo_json(json_path)
        return
    
    # Inicializar gestor JSON
    gestor = GestorJsonUnificado(json_path)
    
    contrato_nombre = "LIMPIEZA DE ZONAS DE ACCESO ESTACIÓNES DE NUEVOS MINISTERIOS Y P.PIO"
    
    print(f"📋 Contrato de prueba: {contrato_nombre}")
    
    # Test 1: Verificar que el contrato existe
    print("\n1️⃣ TEST: Verificar existencia del contrato")
    contrato = gestor.buscar_contrato_inteligente(contrato_nombre)
    if contrato:
        print(f"✅ Contrato encontrado con {len(contrato)} campos")
        print(f"📋 Campos actuales: {list(contrato.keys())}")
    else:
        print("❌ Contrato NO encontrado")
        return False
    
    # Test 2: Leer campos específicos ANTES del guardado
    print("\n2️⃣ TEST: Lectura de campos problemáticos ANTES")
    campos_test = ['OrganoSolicitaOfertas', 'regimenPagos', 'organoContratacion', 'organoContratacion2']
    
    for campo in campos_test:
        valor = gestor.leer_campo_contrato(contrato_nombre, campo)
        print(f"📖 {campo}: '{valor}' (tipo: {type(valor).__name__})")
    
    # Test 3: Intentar guardar cada campo individualmente
    print("\n3️⃣ TEST: Guardado individual de campos")
    
    valores_test = {
        'OrganoSolicitaOfertas': 'TEST_ORGANO_SOLICITA',
        'regimenPagos': 'TEST_REGIMEN_PAGOS',
        'organoContratacion': 'TEST_ORGANO_CONTRATACION',
        'organoContratacion2': 'TEST_ORGANO_CONTRATACION2'
    }
    
    for campo, valor_test in valores_test.items():
        print(f"\n🔄 Probando guardar {campo} = '{valor_test}'")
        
        # Guardar
        resultado = gestor.guardar_campo_en_json(contrato_nombre, campo, valor_test)
        print(f"   💾 Resultado guardado: {resultado}")
        
        # Verificar inmediatamente
        valor_leido = gestor.leer_campo_contrato(contrato_nombre, campo)
        print(f"   📖 Valor leído después: '{valor_leido}'")
        
        # Verificar consistencia
        if str(valor_leido) == str(valor_test):
            print(f"   ✅ {campo}: GUARDADO CORRECTAMENTE")
        else:
            print(f"   ❌ {campo}: FALLÓ - Esperado '{valor_test}', obtuvo '{valor_leido}'")
    
    # Test 4: Verificar recargar datos
    print("\n4️⃣ TEST: Verificación tras recargar datos")
    gestor.recargar_datos()
    
    for campo, valor_test in valores_test.items():
        valor_recargado = gestor.leer_campo_contrato(contrato_nombre, campo)
        print(f"📄 {campo}: '{valor_recargado}' (tras recarga)")
        
        if str(valor_recargado) == str(valor_test):
            print(f"   ✅ {campo}: PERSISTIDO CORRECTAMENTE")
        else:
            print(f"   ❌ {campo}: NO PERSISTIDO - Esperado '{valor_test}', obtuvo '{valor_recargado}'")
    
    # Test 5: Verificar archivo JSON directamente
    print("\n5️⃣ TEST: Verificación directa del archivo JSON")
    import json
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            datos_archivo = json.load(f)
        
        # Buscar el contrato en el archivo
        contrato_archivo = None
        for obra in datos_archivo.get('obras', []):
            if obra.get('nombreObra') == contrato_nombre:
                contrato_archivo = obra
                break
        
        if contrato_archivo:
            print("📄 Campos encontrados en archivo JSON:")
            for campo, valor_test in valores_test.items():
                valor_archivo = contrato_archivo.get(campo)
                print(f"   📄 {campo}: '{valor_archivo}'")
                
                if str(valor_archivo) == str(valor_test):
                    print(f"   ✅ {campo}: EN ARCHIVO JSON")
                else:
                    print(f"   ❌ {campo}: NO EN ARCHIVO - Esperado '{valor_test}', archivo tiene '{valor_archivo}'")
        else:
            print("❌ Contrato no encontrado en archivo JSON")
            
    except Exception as e:
        print(f"❌ Error leyendo archivo JSON: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TEST COMPLETADO")

def test_directo_json(json_path):
    """Test directo sobre archivo JSON sin importar controladores"""
    print("📄 TEST DIRECTO JSON")
    
    contrato_nombre = "LIMPIEZA DE ZONAS DE ACCESO ESTACIÓNES DE NUEVOS MINISTERIOS Y P.PIO"
    
    # Leer archivo actual
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        print(f"✅ Archivo JSON cargado exitosamente")
    except Exception as e:
        print(f"❌ Error cargando JSON: {e}")
        return
    
    # Buscar contrato
    contrato = None
    contrato_index = None
    for i, obra in enumerate(datos.get('obras', [])):
        if obra.get('nombreObra') == contrato_nombre:
            contrato = obra
            contrato_index = i
            break
    
    if not contrato:
        print(f"❌ Contrato '{contrato_nombre}' no encontrado")
        return
    
    print(f"✅ Contrato encontrado en índice {contrato_index}")
    
    # Test campos problemáticos
    campos_test = ['OrganoSolicitaOfertas', 'regimenPagos', 'organoContratacion', 'organoContratacion2']
    
    print(f"\n📋 Estados actuales de campos problemáticos:")
    for campo in campos_test:
        valor = contrato.get(campo, "NO_EXISTE")
        print(f"   {campo}: '{valor}'")
    
    # Test: Modificar directamente y guardar
    print(f"\n🔄 Modificando campos directamente...")
    
    valores_test = {
        'OrganoSolicitaOfertas': 'TEST_ORGANO_DIRECTO',
        'regimenPagos': 'TEST_REGIMEN_DIRECTO',
        'organoContratacion': 'TEST_ORGANO1_DIRECTO',
        'organoContratacion2': 'TEST_ORGANO2_DIRECTO'
    }
    
    # Modificar en memoria
    for campo, valor in valores_test.items():
        datos['obras'][contrato_index][campo] = valor
        print(f"   ✏️ Modificado {campo} = '{valor}'")
    
    # Guardar archivo
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print(f"✅ Archivo guardado exitosamente")
    except Exception as e:
        print(f"❌ Error guardando: {e}")
        return
    
    # Verificar recargando
    print(f"\n🔄 Verificando tras recarga...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            datos_recargados = json.load(f)
        
        contrato_recargado = None
        for obra in datos_recargados.get('obras', []):
            if obra.get('nombreObra') == contrato_nombre:
                contrato_recargado = obra
                break
        
        if contrato_recargado:
            for campo, valor_esperado in valores_test.items():
                valor_actual = contrato_recargado.get(campo, "NO_EXISTE")
                if str(valor_actual) == str(valor_esperado):
                    print(f"   ✅ {campo}: GUARDADO CORRECTAMENTE ('{valor_actual}')")
                else:
                    print(f"   ❌ {campo}: FALLÓ - Esperado '{valor_esperado}', obtuvo '{valor_actual}'")
        else:
            print("❌ Contrato no encontrado tras recarga")
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
    
    print("🏁 TEST DIRECTO COMPLETADO")

if __name__ == "__main__":
    test_guardado_campos()