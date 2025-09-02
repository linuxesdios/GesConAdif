# 📋 Generador de Actas ADIF

**Sistema integral de gestión de contratos y generación automática de documentos oficiales para ADIF**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-Propietario-red.svg)
![Version](https://img.shields.io/badge/Version-3.0-orange.svg)

## 🎯 Descripción

**GesConAdif** es una aplicación de escritorio desarrollada para **ADIF (Administrador de Infraestructuras Ferroviarias)** que automatiza la gestión completa de contratos de obras y servicios, desde la licitación hasta la liquidación final.

### ✨ Características Principales

- 🏗️ **Gestión de Contratos**: Obras y servicios con control completo del ciclo de vida
- 📄 **Generación Automática**: Documentos oficiales (actas, cartas, contratos)
- 💰 **Control Financiero**: Seguimiento de ofertas, adjudicaciones y facturación
- 📊 **Facturas Directas**: Sistema especializado para facturación directa
- 🔄 **Seguimiento**: Cronograma visual y control de estados
- 📁 **Organización**: Estructura automática de carpetas por proyecto
- 💾 **Respaldos**: Sistema automático de copias de seguridad
- 🖥️ **Interfaz Moderna**: UI intuitiva con pestañas organizadas

## 🚀 Instalación

### Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.8 o superior
- **Memoria RAM**: 4GB mínimo (8GB recomendado)
- **Espacio en Disco**: 500MB para la aplicación + espacio para proyectos

### Instalación desde Código Fuente

```bash
# Clonar el repositorio
git clone [URL_DEL_REPOSITORIO]
cd GesConAdif

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main_py.py
```

### Dependencias Principales

```
PyQt5>=5.15.0
python-docx>=0.8.11
docx2pdf>=0.1.8
openpyxl>=3.0.9
Pillow>=8.3.2
```

## 📖 Guía de Uso

### 🏁 Inicio Rápido

1. **Ejecutar la aplicación**: `python main_py.py`
2. **Crear nuevo contrato**: Menú → Crear Proyecto
3. **Seleccionar tipo**: Obras, Servicios, o Mantenimiento
4. **Completar datos**: Información básica del contrato
5. **Gestionar empresas**: Agregar licitadores y ofertas
6. **Generar documentos**: Usar botones de generación

### 🏢 Gestión de Contratos

#### Crear Nuevo Contrato
- **Menú**: `Archivo → Crear Proyecto`
- **Datos requeridos**: Nombre, expediente, tipo, presupuesto
- **Estructura automática**: Se crean carpetas organizadas

#### Tipos de Contrato Soportados
- **🏗️ Obras**: Construcción y reformas
- **🔧 Servicios**: Mantenimiento y servicios técnicos
- **⚡ Mantenimiento**: Contratos de mantenimiento especializado
- **💰 Facturas Directas**: Facturación sin licitación

### 📋 Gestión de Empresas y Ofertas

#### Agregar Empresas Licitadoras
1. Pestaña **"Proyecto"**
2. Tabla de **Empresas**
3. Completar: Nombre, NIF, Email, Contacto
4. Las ofertas se sincronizan automáticamente

#### Control de Ofertas
- **Validación automática**: Números y formatos
- **Comparación**: Ordenamiento por importe
- **Estado**: Presentada, adjudicada, rechazada

### 📄 Generación de Documentos

#### Documentos Disponibles

| Documento | Descripción | Cuándo Usar |
|-----------|-------------|-------------|
| **Acta de Inicio** | Inicio formal del contrato | Al comenzar trabajos |
| **Cartas de Invitación** | Invitación a licitadores | Proceso de licitación |
| **Acta de Adjudicación** | Resolución de adjudicación | Tras evaluar ofertas |
| **Cartas de Adjudicación** | Notificación a empresas | Comunicar resultado |
| **Acta de Liquidación** | Cierre económico | Finalización del contrato |
| **Acta de Replanteo** | Replanteo de obra | Obras específicas |
| **Acta de Recepción** | Recepción de trabajos | Finalización satisfactoria |

#### Proceso de Generación
1. **Completar datos** del contrato
2. **Seleccionar plantilla** apropiada
3. **Hacer clic** en botón de generación
4. **Revisar documento** generado
5. **Conversión automática** a PDF

### 💰 Facturas Directas

Sistema especializado para contratos sin licitación:

- **Gestión independiente**: Separada de contratos normales
- **Control de importes**: Límites automáticos
- **Seguimiento**: Estado y fechas
- **Informes**: Generación de reportes

### 📊 Sistema de Seguimiento

#### Cronograma Visual
- **Estados del contrato**: Progreso visual
- **Fechas clave**: Hitos importantes
- **Alertas**: Vencimientos próximos

#### Tabla de Seguimiento
- **Fases completadas**: Control de avance
- **Documentos generados**: Historial
- **Pendientes**: Tareas por realizar

## 🏗️ Arquitectura del Sistema

### 📁 Estructura del Proyecto

```
GesConAdif/
├── 📁 controladores/          # Lógica de negocio
│   ├── controlador_grafica.py      # Controlador principal UI
│   ├── controlador_json.py         # Gestión de datos
│   ├── controlador_documentos.py   # Generación documentos
│   ├── controlador_calculos.py     # Cálculos financieros
│   └── ...
├── 📁 ui/                     # Interfaces de usuario
│   └── actas.ui                    # Diseño principal
├── 📁 plantillas/             # Plantillas de documentos
│   ├── plantilla_acta_inicio_obra.docx
│   ├── plantilla_cartas_invitacion.docx
│   └── ...
├── 📁 utils/                  # Utilidades
│   ├── archivos.py                 # Gestión de archivos
│   ├── fechas.py                   # Utilidades de fechas
│   └── ...
├── 📁 tests/                  # Pruebas unitarias
├── 📁 obras/                  # Proyectos de contratos
└── 📄 main_py.py             # Punto de entrada
```

### 🔧 Componentes Principales

#### Controladores
- **ControladorGrafica**: Interfaz principal y coordinación
- **ControladorJson**: Persistencia de datos
- **ControladorDocumentos**: Generación de documentos
- **ControladorCalculos**: Operaciones financieras
- **ControladorTablas**: Gestión de tablas de datos

#### Modelos de Datos
- **Proyecto**: Contenedor principal del contrato
- **DatosContrato**: Información contractual
- **Empresa**: Datos de licitadores
- **Oferta**: Ofertas económicas
- **DatosLiquidacion**: Información de cierre

### 🗄️ Gestión de Datos

#### Almacenamiento
- **Formato**: JSON para máxima compatibilidad
- **Estructura**: Jerárquica y normalizada
- **Ubicación**: `BaseDatos.json` principal + archivos por proyecto

#### Respaldos Automáticos
- **Frecuencia**: Cada modificación importante
- **Ubicación**: Carpeta `9_Guardado_seguridad`
- **Rotación**: Mantiene últimas 5 copias

## 🧪 Testing

### Ejecutar Pruebas

```bash
# Todas las pruebas
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Solo pruebas unitarias
pytest -m unit

# Solo pruebas críticas
pytest -m critical
```

### Cobertura de Código
- **Objetivo**: 85% mínimo
- **Reporte**: Generado en `htmlcov/`
- **Áreas críticas**: 100% cobertura requerida

## 📋 Configuración

### Archivos de Configuración

#### `BaseDatos.json`
```json
{
  "contratos": {},
  "firmantes": {
    "firmanteConforme": "Nombre del firmante",
    "cargoConforme": "Cargo"
  },
  "configuracion": {
    "version": "3.0",
    "ultima_actualizacion": "2024-01-01"
  }
}
```

#### Plantillas de Documentos
- **Ubicación**: Carpeta `plantillas/`
- **Formato**: Microsoft Word (.docx)
- **Variables**: Marcadores automáticos `{variable}`

### Personalización

#### Firmantes
- **Acceso**: Menú → Editar Firmantes
- **Campos**: Nombre, cargo, representación
- **Aplicación**: Automática en documentos

#### Plantillas
- **Modificación**: Editar archivos .docx
- **Variables disponibles**: Ver documentación técnica
- **Respaldo**: Mantener copias originales

## 🚨 Solución de Problemas

### Problemas Comunes

#### Error al Generar PDF
```
Error: No se puede convertir a PDF
```
**Solución**: Verificar que Microsoft Word esté instalado y cerrar documentos abiertos.

#### Datos No Se Guardan
```
Error: No se pueden guardar los cambios
```
**Solución**: Verificar permisos de escritura en la carpeta del proyecto.

#### Plantilla No Encontrada
```
Error: Plantilla no encontrada
```
**Solución**: Verificar que existan los archivos en la carpeta `plantillas/`.

### Logs y Depuración

#### Archivos de Log
- **Ubicación**: `controladores/adif_actas.log`
- **Nivel**: INFO, WARNING, ERROR
- **Rotación**: Automática por tamaño

#### Modo Debug
```bash
# Ejecutar con logs detallados
python main_py.py --debug
```

## 🔒 Seguridad y Respaldos

### Respaldos Automáticos
- **Frecuencia**: Cada guardado importante
- **Ubicación**: `obras/[proyecto]/9_Guardado_seguridad/`
- **Retención**: 5 copias más recientes

### Integridad de Datos
- **Validación**: Automática en cada operación
- **Recuperación**: Desde respaldos automáticos
- **Verificación**: Checksums en archivos críticos

## 🤝 Contribución

### Desarrollo

```bash
# Configurar entorno de desarrollo
git clone [REPO]
cd GesConAdif
python -m venv venv
venv\Scripts\activate
pip install -r requirements-test.txt

# Ejecutar pruebas antes de commit
pytest
```

### Estándares de Código
- **Estilo**: PEP 8
- **Documentación**: Docstrings obligatorios
- **Testing**: Cobertura mínima 85%
- **Commits**: Mensajes descriptivos

## 📞 Soporte

### Información de Contacto
- **Desarrollador**: Pablo Martín Fernández
- **Cargo**: Ingeniero Industrial
- **Departamento**: Patrimonio y Urbanismo
- **Organización**: ADIF

### Reportar Problemas
1. **Descripción detallada** del problema
2. **Pasos para reproducir** el error
3. **Archivos de log** relevantes
4. **Versión** de la aplicación

## 📄 Licencia

Este software es propiedad de **ADIF (Administrador de Infraestructuras Ferroviarias)** y está destinado exclusivamente para uso interno de la organización.

**Restricciones**:
- ❌ No se permite distribución externa
- ❌ No se permite uso comercial por terceros
- ❌ No se permite modificación sin autorización
- ✅ Uso interno en ADIF autorizado

## 📈 Roadmap

### Versión 3.1 (Próxima)
- [ ] Integración con sistemas ADIF
- [ ] Notificaciones automáticas
- [ ] Dashboard ejecutivo
- [ ] API REST para integraciones

### Versión 3.2 (Futuro)
- [ ] Módulo de reporting avanzado
- [ ] Integración con firma digital
- [ ] Workflow automatizado
- [ ] App móvil complementaria

---

## 🏆 Reconocimientos

Desarrollado con ❤️ para optimizar los procesos de contratación en **ADIF**.

**Tecnologías utilizadas**:
- 🐍 Python 3.8+
- 🖥️ PyQt5 para la interfaz
- 📄 python-docx para documentos
- 📊 openpyxl para Excel
- 🧪 pytest para testing

---

*Última actualización: Enero 2024*
*Versión del README: 1.0*