#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir print statements a logging en archivos de controladores.
Convierte automáticamente los patrones más comunes.
"""

import re
import os
from pathlib import Path


def convert_prints_to_logging(file_path):
    """
    Convierte print statements a logging en un archivo.
    
    Args:
        file_path: Ruta del archivo a procesar
        
    Returns:
        tuple: (conversiones_realizadas, archivo_modificado)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        conversiones = 0
        
        # Patrones de conversión basados en el contenido de los print statements
        patterns = [
            # Errores críticos (❌)
            (r'print\(f"\[(\w+)\] ❌ ([^"]+)"\)', r'logger.error(f"[\1] \2")'),
            (r'print\(f"\[(\w+)\] ❌ ([^"]+): \{([^}]+)\}"\)', r'logger.error(f"[\1] \2: {\3}")'),
            
            # Mensajes informativos (✅, ℹ️, 📊, etc.)
            (r'print\(f"\[(\w+)\] ✅ ([^"]+)"\)', r'logger.info(f"[\1] \2")'),
            (r'print\(f"\[(\w+)\] ℹ️ ([^"]+)"\)', r'logger.info(f"[\1] \2")'),
            (r'print\(f"\[(\w+)\] 📊 ([^"]+)"\)', r'logger.info(f"[\1] \2")'),
            (r'print\(f"\[(\w+)\] 🔄 ([^"]+)"\)', r'logger.info(f"[\1] \2")'),
            (r'print\(f"\[(\w+)\] 🏢 ([^"]+)"\)', r'logger.info(f"[\1] \2")'),
            
            # Debug y advertencias (⚠️, 🔍, 📄, etc.)
            (r'print\(f"\[(\w+)\] ⚠️ ([^"]+)"\)', r'logger.warning(f"[\1] \2")'),
            (r'print\(f"\[(\w+)\] 🔍 ([^"]+)"\)', r'logger.debug(f"[\1] \2")'),
            (r'print\(f"\[(\w+)\] 📄 ([^"]+)"\)', r'logger.debug(f"[\1] \2")'),
            
            # Prints simples con etiquetas
            (r'print\("\[(\w+)\] ([^"]+)"\)', r'logger.info("[\1] \2")'),
            (r'print\(f"\[(\w+)\] ([^"]+)"\)', r'logger.info(f"[\1] \2")'),
            
            # Prints de ERROR específicos
            (r'print\(f"\[(\w+)\] ERROR ([^"]+): \{([^}]+)\}"\)', r'logger.error(f"[\1] ERROR \2: {\3}")'),
            (r'print\(f"\[(\w+)\] ERROR ([^"]+)"\)', r'logger.error(f"[\1] ERROR \2")'),
            
            # Prints de OK específicos
            (r'print\("\[(\w+)\] OK ([^"]+)"\)', r'logger.info("[\1] OK \2")'),
            
            # Traceback prints
            (r'traceback\.print_exc\(\)', r'logger.exception("Error completo:")'),
        ]
        
        # Aplicar patrones de conversión
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                conversiones += len(matches)
        
        # Agregar import si se hicieron conversiones y no existe
        if conversiones > 0 and 'from utils.logger import get_logger' not in content:
            # Buscar líneas de import existentes
            lines = content.split('\n')
            import_line_inserted = False
            
            for i, line in enumerate(lines):
                # Insertar después de los imports existentes
                if line.startswith('import ') or line.startswith('from '):
                    continue
                elif not import_line_inserted and (line.strip() == '' or not line.startswith(('#', 'import', 'from'))):
                    lines.insert(i, 'from utils.logger import get_logger')
                    import_line_inserted = True
                    break
            
            if not import_line_inserted:
                # Si no encontramos lugar, añadir al inicio después de docstring
                lines.insert(1, 'from utils.logger import get_logger')
            
            content = '\n'.join(lines)
        
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return conversiones, True
        
        return conversiones, False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return 0, False


def main():
    """Procesa todos los archivos de controladores."""
    controladores_dir = Path("controladores")
    
    if not controladores_dir.exists():
        print("Directorio 'controladores' no encontrado")
        return
    
    total_conversiones = 0
    archivos_procesados = 0
    archivos_modificados = 0
    
    # Procesar todos los archivos .py en controladores
    for archivo in controladores_dir.glob("*.py"):
        print(f"Procesando: {archivo}")
        
        conversiones, modificado = convert_prints_to_logging(archivo)
        
        total_conversiones += conversiones
        archivos_procesados += 1
        
        if modificado:
            archivos_modificados += 1
            print(f"  OK: {conversiones} conversiones realizadas")
        else:
            print(f"  Sin cambios")
    
    print(f"\nRESUMEN:")
    print(f"Archivos procesados: {archivos_procesados}")
    print(f"Archivos modificados: {archivos_modificados}")
    print(f"Total conversiones: {total_conversiones}")


if __name__ == "__main__":
    main()