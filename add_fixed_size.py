#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para añadir setFixedSize a todos los widgets de actas.ui
"""
import xml.etree.ElementTree as ET
import os
import shutil
from datetime import datetime

def add_fixed_size_to_widgets(ui_file_path):
    """
    Añade la propiedad setFixedSize a todos los widgets que tengan geometry
    """
    # Hacer backup del archivo original
    backup_path = f"{ui_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(ui_file_path, backup_path)
    print(f"Backup creado: {backup_path}")
    
    # Leer el archivo XML
    tree = ET.parse(ui_file_path)
    root = tree.getroot()
    
    widgets_modificados = 0
    
    # Buscar todos los elementos 'widget'
    for widget in root.iter('widget'):
        # Verificar si el widget tiene una propiedad 'geometry'
        geometry_prop = None
        for prop in widget.findall('property'):
            if prop.get('name') == 'geometry':
                geometry_prop = prop
                break
        
        if geometry_prop is not None:
            # Verificar si ya tiene setFixedSize
            has_fixed_size = False
            for prop in widget.findall('property'):
                if prop.get('name') == 'setFixedSize':
                    has_fixed_size = True
                    break
            
            if not has_fixed_size:
                # Obtener width y height del geometry
                rect = geometry_prop.find('rect')
                if rect is not None:
                    width_elem = rect.find('width')
                    height_elem = rect.find('height')
                    
                    if width_elem is not None and height_elem is not None:
                        width = width_elem.text
                        height = height_elem.text
                        
                        # Crear la nueva propiedad setFixedSize
                        fixed_size_prop = ET.Element('property', name='setFixedSize')
                        size_elem = ET.SubElement(fixed_size_prop, 'size')
                        width_new = ET.SubElement(size_elem, 'width')
                        height_new = ET.SubElement(size_elem, 'height')
                        width_new.text = width
                        height_new.text = height
                        
                        # Insertar después de geometry
                        geometry_index = list(widget).index(geometry_prop)
                        widget.insert(geometry_index + 1, fixed_size_prop)
                        
                        widgets_modificados += 1
                        widget_name = widget.get('name', 'Sin nombre')
                        widget_class = widget.get('class', 'Sin clase')
                        print(f"OK Añadido setFixedSize a {widget_class} '{widget_name}': {width}x{height}")
    
    # Guardar el archivo modificado
    tree.write(ui_file_path, encoding='utf-8', xml_declaration=True)
    print(f"\nProceso completado: {widgets_modificados} widgets modificados")
    print(f"Archivo actualizado: {ui_file_path}")
    print(f"Backup disponible en: {backup_path}")

def main():
    ui_file = "C:/Users/pablo/Desktop/generador_actas/ui/actas.ui"
    
    if not os.path.exists(ui_file):
        print(f"Error: No se encuentra el archivo {ui_file}")
        return
    
    print("Iniciando proceso de añadir setFixedSize a todos los widgets...")
    print(f"Archivo: {ui_file}")
    
    try:
        add_fixed_size_to_widgets(ui_file)
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()