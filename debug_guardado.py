#!/usr/bin/env python3
"""
Script de depuración para el sistema de guardado
Genera logs detallados para identificar problemas de persistencia
"""

import json
import os
import sys
import hashlib
from datetime import datetime

def calcular_hash_archivo(filepath):
    """Calcula el hash MD5 de un archivo"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return "ERROR"

def leer_json_seguro(filepath):
    """Lee el JSON de forma segura"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ ERROR leyendo JSON: {e}")
        return None

def buscar_plazo_ejecucion(data, nombre_obra):
    """Busca el plazoEjecucion de una obra específica"""
    try:
        for obra in data.get('obras', []):
            if obra.get('nombreObra') == nombre_obra:
                return obra.get('plazoEjecucion', 'NO_ENCONTRADO')
        return 'OBRA_NO_ENCONTRADA'
    except:
        return 'ERROR'

def main():
    """Función principal de depuración"""
    
    json_path = "F:/generador_actas/BaseDatos.json"
    obra_test = "OBRAS DE REPARACIÓN EN LAS INSTALACIONES INTERIORES"
    
    print("SCRIPT DE DEPURACION DEL SISTEMA DE GUARDADO")
    print("=" * 60)
    print(f"Archivo JSON: {json_path}")
    print(f"Obra de prueba: {obra_test}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. VERIFICAR EXISTENCIA Y PERMISOS
    print("1. VERIFICANDO ARCHIVO JSON...")
    if not os.path.exists(json_path):
        print(f"❌ El archivo no existe: {json_path}")
        return
    
    # Permisos
    readable = os.access(json_path, os.R_OK)
    writable = os.access(json_path, os.W_OK)
    print(f"Lectura: {'OK' if readable else 'ERROR'}")
    print(f"Escritura: {'OK' if writable else 'ERROR'}")
    
    # Tamaño y última modificación
    stats = os.stat(json_path)
    size_kb = round(stats.st_size / 1024, 2)
    mod_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    print(f"📏 Tamaño: {size_kb} KB")
    print(f"📅 Última modificación: {mod_time}")
    print()
    
    # 2. LEER CONTENIDO ACTUAL
    print("2️⃣ LEYENDO CONTENIDO ACTUAL...")
    data = leer_json_seguro(json_path)
    if not data:
        return
    
    hash_inicial = calcular_hash_archivo(json_path)
    plazo_inicial = buscar_plazo_ejecucion(data, obra_test)
    
    print(f"🔒 Hash MD5 inicial: {hash_inicial[:8]}...")
    print(f"⏱️  plazoEjecucion actual: {plazo_inicial}")
    print()
    
    # 3. SIMULACIÓN DE CAMBIO
    print("3️⃣ SIMULANDO CAMBIO DE plazoEjecucion...")
    nuevo_valor = "999"  # Valor único para testing
    
    # Buscar y modificar la obra
    obra_encontrada = False
    for obra in data.get('obras', []):
        if obra.get('nombreObra') == obra_test:
            valor_anterior = obra.get('plazoEjecucion', 'N/A')
            obra['plazoEjecucion'] = nuevo_valor
            obra['fechaModificacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            obra_encontrada = True
            print(f"📝 Cambiando plazoEjecucion: '{valor_anterior}' → '{nuevo_valor}'")
            break
    
    if not obra_encontrada:
        print(f"❌ No se encontró la obra: {obra_test}")
        return
    
    # 4. INTENTAR GUARDAR
    print("\n4️⃣ GUARDANDO CAMBIOS...")
    
    backup_path = json_path + ".backup_debug"
    try:
        # Crear backup
        import shutil
        shutil.copy2(json_path, backup_path)
        print(f"💾 Backup creado: {backup_path}")
        
        # Escribir cambios
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ Escritura completada")
        
    except Exception as e:
        print(f"❌ Error en escritura: {e}")
        return
    
    # 5. VERIFICAR PERSISTENCIA
    print("\n5️⃣ VERIFICANDO PERSISTENCIA...")
    
    # Nuevo hash
    hash_final = calcular_hash_archivo(json_path)
    
    # Releer archivo
    data_verificacion = leer_json_seguro(json_path)
    plazo_final = buscar_plazo_ejecucion(data_verificacion, obra_test) if data_verificacion else "ERROR"
    
    print(f"🔒 Hash MD5 final: {hash_final[:8]}...")
    print(f"⏱️  plazoEjecucion verificado: {plazo_final}")
    print(f"🔄 Hash cambió: {'✅' if hash_inicial != hash_final else '❌'}")
    print(f"✅ Valor correcto: {'✅' if plazo_final == nuevo_valor else '❌'}")
    
    # 6. ANÁLISIS DE RESULTADOS
    print("\n6️⃣ ANÁLISIS DE RESULTADOS...")
    if plazo_final == nuevo_valor:
        print("🎉 ÉXITO: El cambio se persistió correctamente")
        print("💡 El problema NO está en el mecanismo de guardado básico")
        print("💡 Revisar el sistema de autoguardado de la aplicación")
    else:
        print("🚨 FALLO: El cambio NO se persistió")
        print("💡 Hay un problema en el sistema de escritura")
        if plazo_final == plazo_inicial:
            print("💡 El archivo no se modificó en absoluto")
        else:
            print(f"💡 El archivo se modificó pero con valor incorrecto: '{plazo_final}'")
    
    # 7. RESTAURAR BACKUP
    print("\n7️⃣ RESTAURANDO BACKUP...")
    try:
        shutil.copy2(backup_path, json_path)
        os.remove(backup_path)
        print("✅ Backup restaurado y eliminado")
    except Exception as e:
        print(f"❌ Error restaurando backup: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 DEPURACIÓN COMPLETADA")

if __name__ == "__main__":
    main()