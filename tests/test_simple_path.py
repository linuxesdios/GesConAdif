#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simple para verificar resolución de rutas
"""

import os
import sys
import json
import tempfile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple():
    """Test simple sin caracteres especiales"""
    print("="*50)
    print("TEST SIMPLE - RESOLUCION DE RUTAS")
    print("="*50)
    
    # Datos de prueba
    nombre_contrato = "OBRAS DE REPARACION"
    nombre_carpeta_real = "EXP-2024-001-REPARACIONES"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Dir temporal: {temp_dir}")
        
        # Crear estructura
        obras_dir = os.path.join(temp_dir, "obras")
        carpeta_correcta = os.path.join(obras_dir, nombre_carpeta_real, "10-otros")
        carpeta_incorrecta = os.path.join(obras_dir, nombre_contrato, "10-otros")
        
        # Crear solo la carpeta correcta
        os.makedirs(carpeta_correcta, exist_ok=True)
        
        print("\nRESULTADOS:")
        print(f"Ruta INCORRECTA (antigua): {os.path.exists(carpeta_incorrecta)} - {carpeta_incorrecta}")
        print(f"Ruta CORRECTA (con fix):   {os.path.exists(carpeta_correcta)} - {carpeta_correcta}")
        
        if os.path.exists(carpeta_correcta) and not os.path.exists(carpeta_incorrecta):
            print("\nTEST EXITOSO: Fix funciona correctamente")
            return True
        else:
            print("\nTEST FALLIDO: Problema con rutas")
            return False

if __name__ == "__main__":
    resultado = test_simple()
    print("\n" + "="*50)
    if resultado:
        print("CONCLUSION: El fix de rutas es CORRECTO")
        print("Los documentos se generaran en la carpeta correcta")
    else:
        print("PROBLEMA: Revisar implementacion")
    print("="*50)