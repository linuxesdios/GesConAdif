#!/usr/bin/env python3
"""
Script para convertir print statements a logging en todos los archivos de controladores
"""
import os
import re
import logging

# Configurar logging para el script
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def convert_print_to_logging(content, filename):
    """Convierte print statements a logging apropiado"""
    lines = content.split('\n')
    converted_lines = []
    imports_added = False
    
    for i, line in enumerate(lines):
        # Agregar import de logging al inicio del archivo si no existe
        if not imports_added and (line.startswith('import ') or line.startswith('from ')):
            if 'import logging' not in content and 'from logging import' not in content:
                # Buscar la mejor posición para insertar el import
                if i == 0 or (i > 0 and not lines[i-1].startswith(('import ', 'from '))):
                    converted_lines.append('import logging')
                    converted_lines.append('')
                    imports_added = True
        
        # Detectar y convertir print statements
        print_match = re.match(r'^(\s*)print\(f?"([^"]*)".*\)$', line)
        if print_match:
            indent = print_match.group(1)
            message = print_match.group(2)
            
            # Determinar el nivel de logging basado en el contenido
            if any(marker in message for marker in ['❌', 'ERROR', 'Error', 'CRÍTICO', 'CRITICAL']):
                log_level = 'error'
            elif any(marker in message for marker in ['⚠️', 'WARNING', 'Warning', 'WARN']):
                log_level = 'warning'
            elif any(marker in message for marker in ['ℹ️', 'INFO', 'Info']):
                log_level = 'info'
            elif any(marker in message for marker in ['🔧', 'DEBUG', 'Debug']):
                log_level = 'debug'
            else:
                # Por defecto usar info para mensajes normales
                log_level = 'info'
            
            # Extraer el logger name del mensaje si tiene formato [ComponentName]
            logger_match = re.search(r'\[([^\]]+)\]', message)
            if logger_match:
                component = logger_match.group(1)
                logger_name = f"logger = logging.getLogger('{component}')"
                # Reemplazar el print con logging
                converted_line = f"{indent}logger.{log_level}(f\"{message}\")"
            else:
                # Usar logger genérico
                converted_line = f"{indent}logging.{log_level}(f\"{message}\")"
            
            converted_lines.append(converted_line)
        else:
            # Manejar prints más complejos con múltiples líneas o parámetros
            complex_print_match = re.match(r'^(\s*)print\((.+)\)$', line)
            if complex_print_match and 'print(' in line:
                indent = complex_print_match.group(1)
                content_part = complex_print_match.group(2)
                
                # Determinar nivel basado en contenido
                if any(marker in content_part for marker in ['❌', 'ERROR', 'Error']):
                    log_level = 'error'
                elif any(marker in content_part for marker in ['⚠️', 'WARNING', 'Warning']):
                    log_level = 'warning'
                else:
                    log_level = 'info'
                
                converted_line = f"{indent}logging.{log_level}({content_part})"
                converted_lines.append(converted_line)
            else:
                converted_lines.append(line)
    
    # Si no se agregó el import al inicio, agregarlo después de los imports existentes
    if not imports_added and 'import logging' not in content:
        # Encontrar la última línea de import
        last_import_line = -1
        for i, line in enumerate(converted_lines):
            if line.startswith(('import ', 'from ')) and 'import logging' not in line:
                last_import_line = i
        
        if last_import_line >= 0:
            converted_lines.insert(last_import_line + 1, 'import logging')
            converted_lines.insert(last_import_line + 2, '')
    
    return '\n'.join(converted_lines)

def process_file(filepath):
    """Procesa un archivo individual"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Solo procesar si tiene print statements
        if 'print(' in content:
            logger.info(f"Procesando: {filepath}")
            converted_content = convert_print_to_logging(content, filepath)
            
            # Crear backup
            backup_path = filepath + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Escribir contenido convertido
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            
            logger.info(f"✅ Convertido: {filepath}")
            return True
        else:
            logger.info(f"⏭️ Sin prints: {filepath}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error procesando {filepath}: {e}")
        return False

def main():
    """Función principal"""
    controladores_dir = "controladores"
    
    if not os.path.exists(controladores_dir):
        logger.error(f"❌ Directorio no encontrado: {controladores_dir}")
        return
    
    files_processed = 0
    files_converted = 0
    
    # Procesar todos los archivos .py en controladores
    for filename in os.listdir(controladores_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(controladores_dir, filename)
            files_processed += 1
            
            if process_file(filepath):
                files_converted += 1
    
    logger.info(f"📊 Resumen: {files_converted}/{files_processed} archivos convertidos")

if __name__ == "__main__":
    main()