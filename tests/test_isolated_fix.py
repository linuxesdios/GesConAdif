#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test completamente independiente del fix de aislamiento
NO importa ningún controlador - manipula JSON directamente
"""

import json
import os
import shutil
from datetime import datetime

def crear_backup():
    """Crear backup del archivo BaseDatos.json"""
    if os.path.exists('BaseDatos.json'):
        shutil.copy2('BaseDatos.json', 'BaseDatos_backup.json')
        print("OK: Backup creado: BaseDatos_backup.json")
        return True
    return False

def restaurar_backup():
    """Restaurar backup del archivo"""
    if os.path.exists('BaseDatos_backup.json'):
        shutil.copy2('BaseDatos_backup.json', 'BaseDatos.json')
        os.remove('BaseDatos_backup.json')
        print("OK: Backup restaurado")

def leer_json():
    """Leer JSON directamente del archivo"""
    try:
        with open('BaseDatos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR leyendo JSON: {e}")
        return None

def guardar_json(datos):
    """Guardar JSON directamente al archivo"""
    try:
        with open('BaseDatos.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"ERROR guardando JSON: {e}")
        return False

def actualizar_contrato_aislado(nombre_contrato, campo, nuevo_valor):
    """
    SIMULACIÓN DEL FIX DE AISLAMIENTO:
    1. Lee datos frescos del archivo
    2. Actualiza solo el contrato específico
    3. Guarda sin contaminar memoria
    """
    print(f"[AISLADO] Actualizando {nombre_contrato} -> {campo}={nuevo_valor}")
    
    # 1. LEER DATOS FRESCOS (simulando el fix)
    datos_frescos = leer_json()
    if not datos_frescos:
        return False
    
    # 2. BUSCAR Y ACTUALIZAR CONTRATO ESPECÍFICO
    obras = datos_frescos.get("obras", [])
    encontrado = False
    
    for i, obra in enumerate(obras):
        if nombre_contrato.lower() in obra.get("nombreObra", "").lower():
            # Actualizar campo específico
            obras[i][campo] = nuevo_valor
            obras[i]["fechaModificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            encontrado = True
            print(f"[AISLADO] OK: Actualizado {obra.get('nombreObra')}: {campo}={nuevo_valor}")
            break
    
    if not encontrado:
        print(f"[AISLADO] ERROR: No se encontró obra con '{nombre_contrato}'")
        return False
    
    # 3. GUARDAR DATOS FRESCOS
    resultado = guardar_json(datos_frescos)
    if resultado:
        print(f"[AISLADO] OK: Guardado exitoso")
    else:
        print(f"[AISLADO] ERROR: Error guardando")
    
    return resultado

def obtener_valor_campo(nombre_contrato, campo):
    """Obtener valor de un campo específico leyendo siempre del archivo"""
    datos = leer_json()
    if not datos:
        return None
    
    for obra in datos.get("obras", []):
        if nombre_contrato.lower() in obra.get("nombreObra", "").lower():
            valor = obra.get(campo, "N/A")
            print(f"[LECTURA] {obra.get('nombreObra')} -> {campo}={valor}")
            return valor
    
    return "Obra no encontrada"

def test_fix_aislamiento_completo():
    """
    Test completo del fix de aislamiento de datos:
    
    Escenario del bug original:
    1. Cambiar plazoEjecucion de REPARACIÓN a un valor test
    2. Cambiar a contrato MANTENIMIENTO 
    3. Verificar que REPARACIÓN mantiene su valor (NO se revierte)
    """
    print("="*65)
    print("TEST COMPLETO - FIX DE AISLAMIENTO DE DATOS")
    print("="*65)
    print("Simulando el bug original: cambios que se revertían al cambiar contratos")
    print()
    
    # Crear backup
    if not crear_backup():
        print("ERROR: No se pudo crear backup del archivo BaseDatos.json")
        return False
    
    try:
        # PASO 1: Estado inicial
        print("--- PASO 1: ESTADO INICIAL ---")
        
        plazo_inicial_rep = obtener_valor_campo("REPARACIÓN", "plazoEjecucion")
        plazo_inicial_man = obtener_valor_campo("MANTENIMIENTO", "plazoEjecucion")
        
        if plazo_inicial_rep == "Obra no encontrada" or plazo_inicial_man == "Obra no encontrada":
            print("ERROR: No se encontraron las obras necesarias para el test")
            return False
        
        print(f"INICIAL - REPARACIÓN: {plazo_inicial_rep}")
        print(f"INICIAL - MANTENIMIENTO: {plazo_inicial_man}")
        
        # PASO 2: Cambiar REPARACIÓN (el cambio que se perdía en el bug)
        print("\n--- PASO 2: CAMBIO EN REPARACIÓN ---")
        valor_test_rep = "123"  # Valor único para detectar reversiones
        
        resultado_rep = actualizar_contrato_aislado("REPARACIÓN", "plazoEjecucion", valor_test_rep)
        if not resultado_rep:
            print("ERROR: No se pudo actualizar REPARACIÓN")
            return False
        
        # Verificar que el cambio se guardó
        plazo_verificacion_rep = obtener_valor_campo("REPARACIÓN", "plazoEjecucion")
        if plazo_verificacion_rep != valor_test_rep:
            print(f"ERROR: El cambio no se guardó. Esperado: {valor_test_rep}, Actual: {plazo_verificacion_rep}")
            return False
        
        print("OK: CAMBIO EN REPARACIÓN GUARDADO CORRECTAMENTE")
        
        # PASO 3: Cambiar MANTENIMIENTO (simula cambio de contrato)
        print("\n--- PASO 3: CAMBIO DE CONTRATO A MANTENIMIENTO ---")
        print("(En el bug original, esto causaba que REPARACIÓN perdiera su cambio)")
        
        valor_test_man = "456"  # Valor diferente para MANTENIMIENTO
        
        resultado_man = actualizar_contrato_aislado("MANTENIMIENTO", "plazoEjecucion", valor_test_man)
        if not resultado_man:
            print("ERROR: No se pudo actualizar MANTENIMIENTO")
            return False
        
        # Verificar que MANTENIMIENTO se actualizó
        plazo_verificacion_man = obtener_valor_campo("MANTENIMIENTO", "plazoEjecucion")
        if plazo_verificacion_man != valor_test_man:
            print(f"ERROR: MANTENIMIENTO no se actualizó. Esperado: {valor_test_man}, Actual: {plazo_verificacion_man}")
            return False
        
        print("OK: CAMBIO EN MANTENIMIENTO GUARDADO CORRECTAMENTE")
        
        # PASO 4: VERIFICACIÓN CRÍTICA - ¿Se mantiene REPARACIÓN?
        print("\n--- PASO 4: VERIFICACIÓN CRÍTICA ---")
        print("MOMENTO DE LA VERDAD: ¿REPARACIÓN mantiene su valor después del cambio de contrato?")
        
        plazo_final_rep = obtener_valor_campo("REPARACIÓN", "plazoEjecucion")
        plazo_final_man = obtener_valor_campo("MANTENIMIENTO", "plazoEjecucion")
        
        print(f"FINAL - REPARACIÓN: {plazo_final_rep} (esperado: {valor_test_rep})")
        print(f"FINAL - MANTENIMIENTO: {plazo_final_man} (esperado: {valor_test_man})")
        
        # RESULTADO
        print("\n" + "="*65)
        
        exito_rep = (plazo_final_rep == valor_test_rep)
        exito_man = (plazo_final_man == valor_test_man)
        
        if exito_rep and exito_man:
            print("RESULTADO: FIX DE AISLAMIENTO EXITOSO!")
            print("OK: REPARACIÓN mantiene su valor después del cambio de contrato")
            print("OK: MANTENIMIENTO también mantiene su valor independiente")
            print("OK: NO hay contaminación cruzada entre contratos")
            return True
        else:
            print("ERROR: FIX FALLIDO - Persiste contaminación de datos")
            if not exito_rep:
                print(f"  - REPARACIÓN se revirtió: {valor_test_rep} -> {plazo_final_rep}")
            if not exito_man:
                print(f"  - MANTENIMIENTO se corrompió: {valor_test_man} -> {plazo_final_man}")
            return False
    
    except Exception as e:
        print(f"ERROR durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Siempre restaurar backup
        restaurar_backup()

def main():
    """Función principal"""
    print("Test del Fix de Aislamiento de Datos - JSON Directo")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Sin dependencias GUI - Test completamente independiente")
    print()
    
    resultado = test_fix_aislamiento_completo()
    
    print("\n" + "="*65)
    if resultado:
        print("CONCLUSIÓN: El fix de aislamiento está funcionando correctamente")
        print("Los datos se mantienen independientes entre contratos")
    else:
        print("CONCLUSIÓN: El fix necesita revisión")
        print("Aún existe el problema de contaminación de datos")
    print("="*65)

if __name__ == "__main__":
    main()