#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que los campos problemáticos se guardan correctamente
"""
import json
import time

def verificar_guardado():
    print("VERIFICADOR DE GUARDADO DE CAMPOS")
    print("=" * 50)
    
    json_path = "H:/generador_actas/BaseDatos.json"
    contrato_nombre = "LIMPIEZA DE ZONAS DE ACCESO ESTACIÓNES DE NUEVOS MINISTERIOS Y P.PIO"
    
    campos_test = ['OrganoSolicitaOfertas', 'regimenPagos', 'organoContratacion', 'organoContratacion2']
    
    print(f"Contrato: {contrato_nombre}")
    print(f"Campos a verificar: {campos_test}")
    print()
    
    try:
        # Leer estado actual
        with open(json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Buscar contrato
        contrato = None
        for obra in datos.get('obras', []):
            if obra.get('nombreObra') == contrato_nombre:
                contrato = obra
                break
        
        if not contrato:
            print("ERROR: Contrato no encontrado")
            return
        
        print("ESTADO ACTUAL:")
        for campo in campos_test:
            valor = contrato.get(campo, "NO_EXISTE")
            print(f"  {campo}: '{valor}'")
        
        print()
        print("INSTRUCCIONES:")
        print("1. Abre la aplicación PyQt5")
        print("2. Selecciona el contrato mencionado arriba") 
        print("3. Modifica los campos problemáticos en la interfaz")
        print("4. Ejecuta este script de nuevo para verificar cambios")
        print()
        print("Si los campos se guardan automáticamente, verás los nuevos valores")
        print("Si NO se guardan, seguirán mostrando los valores antiguos")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verificar_guardado()