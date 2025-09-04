# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_py_optimized.py'],
    pathex=[],
    binaries=[],
    datas=[('basedatos/BaseDatos.json', '.'), ('controladores', 'controladores'), ('ui', 'ui'), ('plantillas', 'plantillas'), ('images', 'images'), ('firmas.py', '.')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'PyQt5.uic', 'PyQt5.QtGraphicsView', 'openpyxl', 'lxml', 'docx2pdf', 'PyPDF2', 'platform', 'subprocess', 'controladores.controlador_grafica', 'controladores.controlador_json', 'controladores.controlador_documentos', 'controladores.controlador_pdf_unificado', 'controladores.controlador_backup', 'controladores.controlador_routes', 'controladores.Controlador_selector', 'controladores.controlador_actuaciones_facturas', 'controladores.controlador_facturas_directas', 'controladores.controlador_resumen', 'controladores.controlador_contratos', 'controladores.controlador_tablas', 'controladores.controlador_calculos', 'controladores.controlador_eventos_ui', 'controladores.controlador_autosave', 'controladores.controlador_fases_documentos', 'controladores.controlador_archivos_unificado', 'controladores.ventana_doble_tabla', 'controladores.dialogo_actuaciones_especiales', 'controladores.dialogo_gestionar_contratos', 'modelos_py', 'helpers_py', 'firmas'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'jupyter', 'IPython', 'notebook', 'PySide6', 'PySide2', 'PyQt6'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    exclude_binaries=True,
    name='generador_actas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['images\\icono.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='generador_actas',
)
