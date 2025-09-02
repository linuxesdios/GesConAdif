#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test del fix final para el bug de contaminación de datos entre contratos.
Simula el escenario completo donde cambiar plazoEjecucion se revertía al cambiar contratos.
"""

import json
import sys
import os
import time
import traceback
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def leer_json():
    """Lee el archivo BaseDatos.json"""
    try:
        with open('BaseDatos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR leyendo BaseDatos.json: {e}")
        return None

def obtener_plazo_ejecucion(datos, nombre_obra):
    """Obtiene el plazoEjecucion de una obra específica"""
    obras = datos.get("obras", [])
    for obra in obras:
        if nombre_obra.lower() in obra.get("nombreObra", "").lower():
            return obra.get("plazoEjecucion", "N/A")
    return "Obra no encontrada"

def test_aislamiento_datos():
    """
    Test completo del fix de aislamiento de datos:
    1. Verifica estado inicial
    2. Simula cambio en obra REPARACION
    3. Simula cambio a otra obra  
    4. Simula regreso a obra REPARACION
    5. Verifica que el valor se mantiene
    """
    print("="*70)
    print("TEST DE AISLAMIENTO DE DATOS - FIX FINAL")
    print("="*70)
    
    # Importar después de configurar el path
    try:
        from controladores.controlador_json import GestorJsonUnificado
    except ImportError as e:
        print(f"ERROR importando GestorJsonUnificado: {e}")
        return False
    
    # Paso 1: Estado inicial
    print("\nPASO 1: Verificando estado inicial...")
    datos_inicial = leer_json()
    if not datos_inicial:
        return False
    
    plazo_reparacion = obtener_plazo_ejecucion(datos_inicial, "REPARACIÓN")
    plazo_mantenimiento = obtener_plazo_ejecucion(datos_inicial, "MANTENIMIENTO")
    
    print(f"   REPARACIÓN plazoEjecucion inicial: {plazo_reparacion}")
    print(f"   MANTENIMIENTO plazoEjecucion inicial: {plazo_mantenimiento}")
    
    # Paso 2: Simular cambio en obra REPARACION usando el controlador
    print("\nPASO 2: Cambiando plazoEjecucion en REPARACIÓN a '99'...")
    gestor = GestorJsonUnificado()
    
    # Encontrar nombre exacto de la obra REPARACIÓN
    nombre_obra_reparacion = None
    for obra in datos_inicial.get("obras", []):
        if "REPARACIÓN" in obra.get("nombreObra", ""):
            nombre_obra_reparacion = obra.get("nombreObra")
            break
    
    if not nombre_obra_reparacion:
        print("ERROR: No se encontró obra REPARACIÓN")
        return False
    
    # Usar el método actualizar_contrato con aislamiento
    resultado_actualizacion = gestor.actualizar_contrato(
        nombre_obra_reparacion, 
        {"plazoEjecucion": "99"}
    )
    
    if resultado_actualizacion:
        print("   OK: Actualización exitosa con aislamiento de datos")
    else:
        print("   ERROR: Error en actualización")
        return False
    
    # Verificar que se guardó correctamente
    datos_despues_cambio = leer_json()
    plazo_reparacion_nuevo = obtener_plazo_ejecucion(datos_despues_cambio, "REPARACIÓN")
    print(f"   REPARACIÓN plazoEjecucion después del cambio: {plazo_reparacion_nuevo}")
    
    if plazo_reparacion_nuevo != "99":
        print("ERROR: El cambio no se guardó correctamente")
        return False
    
    # Paso 3: Simular cambio a otra obra (contaminación potencial)
    print("\nPASO 3: Cambiando a obra MANTENIMIENTO...")
    
    # Encontrar nombre exacto de la obra MANTENIMIENTO
    nombre_obra_mantenimiento = None
    for obra in datos_inicial.get("obras", []):
        if "MANTENIMIENTO" in obra.get("nombreObra", ""):
            nombre_obra_mantenimiento = obra.get("nombreObra")
            break
    
    if not nombre_obra_mantenimiento:
        print("ERROR: No se encontró obra MANTENIMIENTO")
        return False
    
    # Simular carga de la otra obra (esto antes causaba contaminación)
    print(f"   Cargando obra: {nombre_obra_mantenimiento}")
    
    # Hacer un cambio en MANTENIMIENTO también
    resultado_mantenimiento = gestor.actualizar_contrato(
        nombre_obra_mantenimiento,
        {"plazoEjecucion": "77"}
    )
    
    if resultado_mantenimiento:
        print("   OK: Cambio en MANTENIMIENTO exitoso")
    else:
        print("   ERROR: Error cambiando MANTENIMIENTO")
        return False
    
    # Verificar estado después del cambio en MANTENIMIENTO
    datos_despues_mantenimiento = leer_json()
    plazo_mantenimiento_nuevo = obtener_plazo_ejecucion(datos_despues_mantenimiento, "MANTENIMIENTO")
    plazo_reparacion_check = obtener_plazo_ejecucion(datos_despues_mantenimiento, "REPARACIÓN")
    
    print(f"   MANTENIMIENTO plazoEjecucion: {plazo_mantenimiento_nuevo}")
    print(f"   REPARACIÓN plazoEjecucion (debe seguir siendo 99): {plazo_reparacion_check}")
    
    # Paso 4: Regresar a obra REPARACION - AQUÍ ERA EL PROBLEMA
    print("\nPASO 4: VERIFICACIÓN CRÍTICA - Regresando a obra REPARACIÓN...")
    print("   (Aquí es donde ocurría la reversión del valor antes del fix)")
    
    # Simular regreso a REPARACIÓN - leer datos frescos
    datos_final = leer_json()
    plazo_reparacion_final = obtener_plazo_ejecucion(datos_final, "REPARACIÓN")
    
    print(f"   REPARACIÓN plazoEjecucion al regresar: {plazo_reparacion_final}")
    
    # Paso 5: Verificación final
    print("\nPASO 5: VERIFICACIÓN FINAL...")
    
    if plazo_reparacion_final == "99":
        print("OK: FIX EXITOSO! El valor se mantiene después del cambio de contrato")
        print("OK: El aislamiento de datos previene la contaminación cruzada")
        return True
    else:
        print(f"ERROR: FIX FALLIDO: El valor se revirtió de '99' a '{plazo_reparacion_final}'")
        print("ERROR: Aún existe contaminación de datos entre contratos")
        return False

def main():
    """Función principal del test"""
    print("Iniciando test del fix de aislamiento de datos...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        resultado = test_aislamiento_datos()
        
        print("\n" + "="*70)
        if resultado:
            print("TEST COMPLETADO: FIX FUNCIONANDO CORRECTAMENTE")
            print("Los datos están aislados entre contratos")
        else:
            print("TEST FALLIDO: REVISAR IMPLEMENTACIÓN")
            print("El problema de contaminación persiste")
        print("="*70)
        
    except Exception as e:
        print(f"\nERROR DURANTE EL TEST: {e}")
        print("Stack trace:")
        traceback.print_exc()

if __name__ == "__main__":
    main()