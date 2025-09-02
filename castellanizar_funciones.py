#!/usr/bin/env python3
"""
Script para castellanizar nombres de funciones en toda la aplicación
Identifica funciones en inglés y proporciona sus traducciones
"""

import os
import re
from typing import Dict, List, Tuple

# Diccionario de traducciones de nombres de funciones comunes
TRADUCCIONES = {
    # Métodos comunes
    'to_dict': 'a_diccionario',
    'from_dict': 'desde_diccionario', 
    'from_json': 'desde_json',
    'to_json': 'a_json',
    'get_data': 'obtener_datos',
    'set_data': 'establecer_datos',
    'load_data': 'cargar_datos',
    'save_data': 'guardar_datos',
    'validate_data': 'validar_datos',
    'update_data': 'actualizar_datos',
    'delete_data': 'eliminar_datos',
    'create_backup': 'crear_respaldo',
    'restore_backup': 'restaurar_respaldo',
    'check_dependencies': 'verificar_dependencias',
    'show_message': 'mostrar_mensaje',
    'hide_message': 'ocultar_mensaje',
    'display_error': 'mostrar_error',
    'handle_error': 'manejar_error',
    'process_data': 'procesar_datos',
    'calculate_total': 'calcular_total',
    'calculate_tax': 'calcular_impuesto',
    'validate_email': 'validar_correo',
    'send_email': 'enviar_correo',
    'generate_report': 'generar_informe',
    'export_data': 'exportar_datos',
    'import_data': 'importar_datos',
    'connect_signals': 'conectar_senales',
    'disconnect_signals': 'desconectar_senales',
    'setup_ui': 'configurar_interfaz',
    'initialize_ui': 'inicializar_interfaz',
    'update_ui': 'actualizar_interfaz',
    'refresh_ui': 'refrescar_interfaz',
    'reset_form': 'reiniciar_formulario',
    'clear_form': 'limpiar_formulario',
    'validate_form': 'validar_formulario',
    'submit_form': 'enviar_formulario',
    'cancel_operation': 'cancelar_operacion',
    'confirm_operation': 'confirmar_operacion',
    'execute_query': 'ejecutar_consulta',
    'build_query': 'construir_consulta',
    'parse_response': 'analizar_respuesta',
    'format_output': 'formatear_salida',
    'clean_data': 'limpiar_datos',
    'normalize_data': 'normalizar_datos',
    'filter_data': 'filtrar_datos',
    'sort_data': 'ordenar_datos',
    'search_data': 'buscar_datos',
    'find_item': 'encontrar_elemento',
    'add_item': 'agregar_elemento',
    'remove_item': 'eliminar_elemento',
    'update_item': 'actualizar_elemento',
    'get_item': 'obtener_elemento',
    'set_item': 'establecer_elemento',
    'has_item': 'tiene_elemento',
    'count_items': 'contar_elementos',
    'clear_items': 'limpiar_elementos',
    'reset_items': 'reiniciar_elementos',
    'load_config': 'cargar_configuracion',
    'save_config': 'guardar_configuracion',
    'apply_config': 'aplicar_configuracion',
    'get_settings': 'obtener_configuracion',
    'set_settings': 'establecer_configuracion',
    'update_settings': 'actualizar_configuracion',
    'reset_settings': 'reiniciar_configuracion',
    'check_status': 'verificar_estado',
    'get_status': 'obtener_estado',
    'set_status': 'establecer_estado',
    'update_status': 'actualizar_estado',
    'is_valid': 'es_valido',
    'is_empty': 'esta_vacio',
    'is_ready': 'esta_listo',
    'is_active': 'esta_activo',
    'is_enabled': 'esta_habilitado',
    'is_visible': 'esta_visible',
    'get_value': 'obtener_valor',
    'set_value': 'establecer_valor',
    'has_value': 'tiene_valor',
    'clear_value': 'limpiar_valor',
    'reset_value': 'reiniciar_valor',
    'calculate_value': 'calcular_valor',
    'format_value': 'formatear_valor',
    'validate_value': 'validar_valor',
    'convert_value': 'convertir_valor',
    'parse_value': 'analizar_valor',
    'encode_value': 'codificar_valor',
    'decode_value': 'decodificar_valor',
    'encrypt_value': 'cifrar_valor',
    'decrypt_value': 'descifrar_valor',
    'hash_value': 'hashear_valor',
    'compare_values': 'comparar_valores',
    'merge_values': 'combinar_valores',
    'split_values': 'dividir_valores',
    'join_values': 'unir_valores',
    'create_connection': 'crear_conexion',
    'close_connection': 'cerrar_conexion',
    'test_connection': 'probar_conexion',
    'open_file': 'abrir_archivo',
    'close_file': 'cerrar_archivo',
    'read_file': 'leer_archivo',
    'write_file': 'escribir_archivo',
    'delete_file': 'eliminar_archivo',
    'copy_file': 'copiar_archivo',
    'move_file': 'mover_archivo',
    'rename_file': 'renombrar_archivo',
    'create_folder': 'crear_carpeta',
    'delete_folder': 'eliminar_carpeta',
    'list_files': 'listar_archivos',
    'find_files': 'encontrar_archivos',
    'backup_file': 'respaldar_archivo',
    'restore_file': 'restaurar_archivo',
    'compress_file': 'comprimir_archivo',
    'decompress_file': 'descomprimir_archivo',
    'upload_file': 'subir_archivo',
    'download_file': 'descargar_archivo',
    'print_document': 'imprimir_documento',
    'preview_document': 'previsualizar_documento',
    'generate_document': 'generar_documento',
    'create_document': 'crear_documento',
    'edit_document': 'editar_documento',
    'delete_document': 'eliminar_documento',
    'save_document': 'guardar_documento',
    'load_document': 'cargar_documento',
    'export_document': 'exportar_documento',
    'import_document': 'importar_documento',
    'sign_document': 'firmar_documento',
    'verify_signature': 'verificar_firma',
    'send_notification': 'enviar_notificacion',
    'receive_notification': 'recibir_notificacion',
    'show_notification': 'mostrar_notificacion',
    'hide_notification': 'ocultar_notificacion',
    'log_event': 'registrar_evento',
    'log_error': 'registrar_error',
    'log_info': 'registrar_informacion',
    'log_warning': 'registrar_advertencia',
    'log_debug': 'registrar_depuracion',
    'start_process': 'iniciar_proceso',
    'stop_process': 'detener_proceso',
    'pause_process': 'pausar_proceso',
    'resume_process': 'reanudar_proceso',
    'restart_process': 'reiniciar_proceso',
    'kill_process': 'terminar_proceso',
    'monitor_process': 'monitorear_proceso',
    'get_progress': 'obtener_progreso',
    'set_progress': 'establecer_progreso',
    'update_progress': 'actualizar_progreso',
    'reset_progress': 'reiniciar_progreso',
    'show_progress': 'mostrar_progreso',
    'hide_progress': 'ocultar_progreso',
    'start_timer': 'iniciar_temporizador',
    'stop_timer': 'detener_temporizador',
    'pause_timer': 'pausar_temporizador',
    'reset_timer': 'reiniciar_temporizador',
    'get_time': 'obtener_tiempo',
    'set_time': 'establecer_tiempo',
    'format_time': 'formatear_tiempo',
    'parse_time': 'analizar_tiempo',
    'convert_time': 'convertir_tiempo',
    'validate_time': 'validar_tiempo'
}

def encontrar_funciones_python(ruta_archivo: str) -> List[Tuple[str, int, str]]:
    """Encuentra todas las definiciones de funciones en un archivo Python"""
    funciones = []
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
            
        for num_linea, linea in enumerate(lineas, 1):
            # Buscar definiciones de función
            match = re.search(r'^\s*def\s+(\w+)\s*\(', linea)
            if match:
                nombre_funcion = match.group(1)
                if not nombre_funcion.startswith('__'):  # Excluir métodos especiales
                    funciones.append((nombre_funcion, num_linea, linea.strip()))
                    
    except Exception as e:
        print(f"Error leyendo {ruta_archivo}: {e}")
    
    return funciones

def analizar_aplicacion(ruta_base: str) -> Dict[str, List[Tuple[str, int, str]]]:
    """Analiza todos los archivos Python de la aplicación"""
    resultados = {}
    
    for root, dirs, files in os.walk(ruta_base):
        # Excluir carpetas específicas
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'dist', '.git', 'venv', 'env']]
        
        for archivo in files:
            if archivo.endswith('.py'):
                ruta_completa = os.path.join(root, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_base)
                
                funciones = encontrar_funciones_python(ruta_completa)
                if funciones:
                    resultados[ruta_relativa] = funciones
    
    return resultados

def generar_informe_traducciones(resultados: Dict[str, List[Tuple[str, int, str]]]):
    """Genera un informe de las funciones que se pueden traducir"""
    print("=" * 80)
    print("INFORME DE FUNCIONES A CASTELLANIZAR")
    print("=" * 80)
    
    total_funciones = 0
    funciones_traducibles = 0
    
    for archivo, funciones in resultados.items():
        print(f"\nArchivo: {archivo}")
        print("-" * 50)
        
        for nombre, linea, codigo in funciones:
            total_funciones += 1
            
            if nombre in TRADUCCIONES:
                funciones_traducibles += 1
                print(f"  OK {nombre} -> {TRADUCCIONES[nombre]} (linea {linea})")
            else:
                # Verificar si parece estar en inglés
                if any(palabra in nombre.lower() for palabra in ['get', 'set', 'load', 'save', 'create', 'delete', 'update', 'show', 'hide', 'check', 'validate', 'process', 'handle', 'execute', 'build', 'parse', 'format', 'clean', 'filter', 'search', 'find', 'add', 'remove', 'clear', 'reset', 'apply', 'convert', 'encode', 'decode', 'compress', 'upload', 'download', 'export', 'import', 'send', 'receive', 'start', 'stop', 'pause', 'resume', 'restart', 'kill', 'monitor']):
                    print(f"  >> {nombre} (linea {linea}) - NECESITA TRADUCCION MANUAL")
                else:
                    print(f"  -- {nombre} (linea {linea}) - Ya en espanol o nombre especifico")
    
    print(f"\n" + "=" * 80)
    print(f"RESUMEN:")
    print(f"Total de funciones encontradas: {total_funciones}")
    print(f"Funciones con traducción automática disponible: {funciones_traducibles}")
    print(f"Funciones que necesitan traducción manual: {total_funciones - funciones_traducibles}")
    print("=" * 80)

def main():
    """Función principal"""
    ruta_aplicacion = "."
    
    print("Analizando aplicacion para encontrar funciones...")
    resultados = analizar_aplicacion(ruta_aplicacion)
    
    if resultados:
        generar_informe_traducciones(resultados)
        
        # Guardar resultados en archivo
        with open("informe_funciones.txt", "w", encoding="utf-8") as f:
            f.write("INFORME DE FUNCIONES A CASTELLANIZAR\n")
            f.write("=" * 80 + "\n\n")
            
            for archivo, funciones in resultados.items():
                f.write(f"📁 {archivo}\n")
                f.write("-" * 50 + "\n")
                
                for nombre, linea, codigo in funciones:
                    if nombre in TRADUCCIONES:
                        f.write(f"  ✅ {nombre} -> {TRADUCCIONES[nombre]} (línea {linea})\n")
                    else:
                        f.write(f"  ℹ️  {nombre} (línea {linea})\n")
                f.write("\n")
        
        print(f"\nInforme guardado en: informe_funciones.txt")
    else:
        print("No se encontraron archivos Python en la aplicacion")

if __name__ == "__main__":
    main()