#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar el funcionamiento del campo nombreCarpeta
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nombre_carpeta():
    print("TEST: Campo nombreCarpeta")
    print("=" * 40)
    
    # Leer BaseDatos.json
    try:
        with open("BaseDatos.json", 'r', encoding='utf-8') as f:
            datos = json.load(f)
        print("OK BaseDatos.json cargado")
    except Exception as e:
        print(f"ERROR: No se pudo leer BaseDatos.json: {e}")
        assert False, f"No se pudo leer BaseDatos.json: {e}"
    
    obras = datos.get('obras', [])
    print(f"OK {len(obras)} obras encontradas")
    
    # Buscar obras con nombreCarpeta
    obras_con_carpeta = []
    for i, obra in enumerate(obras):
        nombre_obra = obra.get('nombreObra', 'Sin nombre')
        nombre_carpeta = obra.get('nombreCarpeta', None)
        numero_expediente = obra.get('numeroExpediente', 'Sin expediente')
        
        if nombre_carpeta:
            obras_con_carpeta.append(obra)
            print(f"[{i}] {nombre_obra[:50]}...")
            print(f"    Expediente: {numero_expediente}")
            print(f"    nombreCarpeta: '{nombre_carpeta}'")
            print()
    
    if obras_con_carpeta:
        print(f"OK {len(obras_con_carpeta)} obras tienen nombreCarpeta")
        
        # Test del controlador de archivos
        print("\nTEST: Controlador de archivos")
        print("-" * 30)
        
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), 'controladores'))
            from controlador_archivos_unificado import GestorArchivos
            
            # Crear instancia temporal
            gestor = GestorArchivos(None)
            
            # Probar _generar_nombre_carpeta con una obra que tiene nombreCarpeta
            obra_test = obras_con_carpeta[0]
            nombre_generado = gestor._generar_nombre_carpeta(obra_test)
            
            print(f"Obra test: {obra_test.get('nombreObra', '')[:50]}...")
            print(f"nombreCarpeta en JSON: '{obra_test.get('nombreCarpeta', '')}'")
            print(f"Nombre generado por controlador: '{nombre_generado}'")
            
            if nombre_generado == obra_test.get('nombreCarpeta'):
                print("OK CORRECTO: El controlador usa nombreCarpeta del JSON")
                assert True  # El controlador usa nombreCarpeta del JSON
            else:
                print("X ERROR: El controlador NO usa nombreCarpeta del JSON")
                assert False, "El controlador NO usa nombreCarpeta del JSON"
                
        except Exception as e:
            print(f"ERROR en test controlador: {e}")
            assert False, f"Error en test controlador: {e}"
    else:
        print("X No hay obras con nombreCarpeta para probar")
        print("  Ejecuta primero el cambio de expediente en la aplicación")
        assert False, "No hay obras con nombreCarpeta para probar"

if __name__ == "__main__":
    resultado = test_nombre_carpeta()
    print("\n" + "=" * 40)
    if resultado:
        print("OK TEST EXITOSO: nombreCarpeta funciona correctamente")
    else:
        print("X TEST FALLIDO: Revisar implementación")