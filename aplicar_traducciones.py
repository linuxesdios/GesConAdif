#!/usr/bin/env python3
"""
Script para aplicar traducciones automáticamente a funciones identificadas
"""

import os
import re
from typing import Dict, List, Tuple

# Traducciones más importantes a aplicar
TRADUCCIONES_CRITICAS = {
    'to_dict': 'a_diccionario',
    'from_dict': 'desde_diccionario',
    'setup_ui': 'configurar_interfaz',
    'get_data': 'obtener_datos',
    'set_data': 'establecer_datos',
    'load_data': 'cargar_datos',
    'save_data': 'guardar_datos',
    'update_data': 'actualizar_datos',
    'check_dependencies': 'verificar_dependencias',
    'show_message': 'mostrar_mensaje',
    'handle_error': 'manejar_error',
    'validate_data': 'validar_datos',
    'process_data': 'procesar_datos'
}

def aplicar_traducciones_archivo(ruta_archivo: str, traducciones: Dict[str, str]) -> int:
    """Aplica traducciones a un archivo específico"""
    cambios_realizados = 0
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
        
        contenido_original = contenido
        
        # Aplicar cada traducción
        for funcion_original, funcion_traducida in traducciones.items():
            # Reemplazar definiciones de función
            patron_def = rf'\bdef\s+{re.escape(funcion_original)}\s*\('
            reemplazo_def = f'def {funcion_traducida}('
            
            if re.search(patron_def, contenido):
                contenido = re.sub(patron_def, reemplazo_def, contenido)
                cambios_realizados += 1
                print(f"  OK {funcion_original} -> {funcion_traducida} (definicion)")
        
        # Solo escribir si hubo cambios
        if contenido != contenido_original:
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write(contenido)
            print(f"  Guardado: {cambios_realizados} cambios en {ruta_archivo}")
    
    except Exception as e:
        print(f"  Error procesando {ruta_archivo}: {e}")
    
    return cambios_realizados

def aplicar_traducciones_aplicacion(ruta_base: str):
    """Aplica traducciones a toda la aplicación"""
    print("Aplicando traducciones críticas...")
    print("=" * 60)
    
    total_cambios = 0
    archivos_procesados = 0
    
    for root, dirs, files in os.walk(ruta_base):
        # Excluir carpetas específicas
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'dist', '.git', 'venv', 'env']]
        
        for archivo in files:
            if archivo.endswith('.py') and not archivo.startswith('test_'):
                ruta_completa = os.path.join(root, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_base)
                
                print(f"\nProcesando: {ruta_relativa}")
                
                cambios = aplicar_traducciones_archivo(ruta_completa, TRADUCCIONES_CRITICAS)
                
                if cambios > 0:
                    total_cambios += cambios
                    archivos_procesados += 1
                else:
                    print("  (Sin cambios)")
    
    print(f"\n" + "=" * 60)
    print(f"RESUMEN:")
    print(f"Archivos procesados con cambios: {archivos_procesados}")
    print(f"Total de traducciones aplicadas: {total_cambios}")
    print("=" * 60)

def main():
    """Función principal"""
    print("Iniciando aplicación de traducciones...")
    ruta_aplicacion = "."
    aplicar_traducciones_aplicacion(ruta_aplicacion)
    print("Proceso completado.")

if __name__ == "__main__":
    main()