#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para diagnosticar problema de guardado
"""
import json

def test_simple():
    print("TEST SIMPLE DE GUARDADO")
    print("=" * 40)
    
    json_path = "H:/generador_actas/BaseDatos.json"
    contrato_nombre = "LIMPIEZA DE ZONAS DE ACCESO ESTACIÓNES DE NUEVOS MINISTERIOS Y P.PIO"
    
    # Leer archivo
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        print("Archivo JSON cargado")
    except Exception as e:
        print(f"Error cargando JSON: {e}")
        return
    
    # Buscar contrato
    contrato_index = None
    for i, obra in enumerate(datos.get('obras', [])):
        if obra.get('nombreObra') == contrato_nombre:
            contrato_index = i
            break
    
    if contrato_index is None:
        print("Contrato no encontrado")
        return
    
    print(f"Contrato encontrado en indice {contrato_index}")
    
    # Verificar campos actuales
    campos_test = ['OrganoSolicitaOfertas', 'regimenPagos', 'organoContratacion', 'organoContratacion2']
    
    print("Estados actuales:")
    for campo in campos_test:
        valor = datos['obras'][contrato_index].get(campo, "NO_EXISTE")
        print(f"  {campo}: '{valor}'")
    
    # Modificar campos
    print("Modificando campos...")
    datos['obras'][contrato_index]['OrganoSolicitaOfertas'] = 'NUEVO_ORGANO'
    datos['obras'][contrato_index]['regimenPagos'] = 'NUEVO_REGIMEN'
    datos['obras'][contrato_index]['organoContratacion'] = 'NUEVO_ORGANO1'
    datos['obras'][contrato_index]['organoContratacion2'] = 'NUEVO_ORGANO2'
    
    # Guardar
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print("Archivo guardado")
    except Exception as e:
        print(f"Error guardando: {e}")
        return
    
    # Verificar
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            datos_verificacion = json.load(f)
        
        contrato_verificacion = datos_verificacion['obras'][contrato_index]
        print("Verificacion tras guardado:")
        
        for campo in campos_test:
            valor = contrato_verificacion.get(campo, "NO_EXISTE")
            print(f"  {campo}: '{valor}'")
            
    except Exception as e:
        print(f"Error en verificacion: {e}")
    
    print("TEST COMPLETADO")

if __name__ == "__main__":
    test_simple()