# 📋 Generador de Actas ADIF

**Sistema integral de gestión de contratos y generación automática de documentos oficiales para ADIF**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-Propietario-red.svg)
![Version](https://img.shields.io/badge/Version-3.2-orange.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Producción-brightgreen.svg)

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
- 🖥️ **Interfaz Moderna**: UI intuitiva con splash screen profesional e iconos ADIF
- 🎨 **Diseño Profesional**: Logo ADIF integrado y tema corporativo
- ⚡ **Arranque Optimizado**: Carga rápida con lazy loading para EXE
- 📱 **Responsive**: Adaptación automática de tamaños y resoluciones

## 🚀 Instalación

### Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.8 o superior
- **Memoria RAM**: 4GB mínimo (8GB recomendado)
- **Espacio en Disco**: 500MB para la aplicación + espacio para proyectos

### Instalación desde Ejecutable (Recomendado)

1. **Descargar la última versión**: `generador_actas_v3.2.exe`
2. **Ejecutar el instalador** siguiendo las instrucciones
3. **Lanzar aplicación**: Doble clic en el icono del escritorio o desde el menú inicio
4. **Primera ejecución**: La aplicación creará automáticamente la estructura de carpetas

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

# Ejecutar la aplicación (desarrollo)
python main_py.py

# Compilar a EXE (opcional)
python compilar_mejorado.py
```

### Compilación a EXE

Para crear el ejecutable optimizado:

```bash
# Ejecutar compilador mejorado
python compilar_mejorado.py

# El EXE se generará en:
dist/generador_actas/generador_actas.exe

# Características del EXE:
# ✅ Splash screen con logo ADIF
# ✅ Icono en barra de tareas
# ✅ Logs organizados en _internal/
# ✅ Arranque optimizado (lazy loading)
# ✅ Todas las plantillas incluidas
```

### Dependencias Principales

```
PyQt5>=5.15.0
python-docx>=0.8.11
docx2pdf>=0.1.8
openpyxl>=3.0.9
Pillow>=8.3.2
```

## 📖 Guía Completa de Uso

### 🏁 Inicio Rápido

1. **Ejecutar la aplicación**: 
   - Desarrollo: `python main_py.py`
   - EXE compilado: `dist/generador_actas/generador_actas.exe`
2. **Splash screen**: Aparece el logo ADIF durante la carga
3. **Ventana principal**: Interfaz con pestañas organizadas
4. **Primer uso**: La aplicación creará automáticamente la estructura de carpetas

### 🖥️ Interfaz de Usuario

#### Panel Principal
La aplicación se organiza en **5 pestañas principales**:

1. **📋 Proyecto**: Gestión de contratos y empresas
2. **💰 Facturas Directas**: Sistema de facturación independiente  
3. **📊 Resumen**: Dashboard y seguimiento visual
4. **🔄 Actuaciones**: Histórico de acciones y documentos
5. **⚙️ Configuración**: Ajustes y preferencias

#### Barra de Herramientas Superior
- **Nuevo Proyecto**: Crear contrato desde cero
- **Abrir Proyecto**: Cargar contrato existente
- **Guardar**: Guardar cambios actuales
- **Importar/Exportar**: Intercambio de datos con Excel
- **Configuración**: Acceso a firmantes y ajustes

### 🏁 Comenzando con un Nuevo Contrato

#### Paso 1: Crear Proyecto
1. **Clic en "Nuevo"** o `Ctrl+N`
2. **Completar formulario inicial**:
   ```
   Nombre del Proyecto: OBRAS DE REPARACIÓN EN LAS INSTALACIONES
   Expediente: EXP-2024-001
   Tipo de Contrato: [Obras/Servicios/Mantenimiento]
   Presupuesto Base: 50.000,00 €
   Plazo de Ejecución: 60 días
   ```
3. **Confirmar**: Se crea automáticamente la estructura de carpetas

#### Paso 2: Estructura de Carpetas Automática
```
obras/[NOMBRE_PROYECTO]/
├── 01-proyecto/                    # Documentos de proyecto
├── 02-documentacion-finales/      # Versiones finales
├── 03-cartas-invitacion/          # Invitaciones a licitadores
├── 04-ofertas-recibidas/          # Ofertas de empresas
├── 05-actas-adjudicacion/         # Documentos de adjudicación
├── 06-contratos/                  # Contratos firmados
├── 07-seguimiento/                # Control de ejecución
├── 08-liquidacion/                # Documentos de liquidación
└── 9_Guardado_seguridad/          # Respaldos automáticos
```

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

### 📄 Sistema de Generación de Documentos

El sistema automatiza la creación de **documentos oficiales ADIF** utilizando plantillas profesionales y datos del contrato.

#### 📋 Documentos Disponibles

##### 🏗️ **Documentos de Obras**

| Documento | Descripción | Cuándo Usar | Ubicación |
|-----------|-------------|-------------|-----------|
| **🟢 Acta de Inicio** | Inicio formal del contrato de obra | Al comenzar los trabajos físicos | `07-seguimiento/` |
| **📧 Cartas de Invitación** | Invitación oficial a licitadores | Proceso de licitación pública | `03-cartas-invitacion/` |
| **📋 Acta de Adjudicación** | Resolución oficial de adjudicación | Tras evaluar y seleccionar ofertas | `05-actas-adjudicacion/` |
| **✉️ Cartas de Adjudicación** | Notificación a empresas participantes | Comunicar resultado a todos | `05-actas-adjudicacion/` |
| **💰 Acta de Liquidación** | Cierre económico del contrato | Finalización y pago final | `08-liquidacion/` |
| **📐 Acta de Replanteo** | Replanteo técnico de la obra | Obras con componente técnico | `07-seguimiento/` |
| **✅ Acta de Recepción** | Recepción de trabajos realizados | Finalización satisfactoria | `07-seguimiento/` |
| **👷 Nombramiento Director** | Designación de director de obra | Al inicio de obras complejas | `06-contratos/` |
| **📄 Contrato de Obra** | Documento contractual oficial | Tras adjudicación definitiva | `06-contratos/` |

##### 🔧 **Documentos de Servicios**

| Documento | Descripción | Cuándo Usar | Ubicación |
|-----------|-------------|-------------|-----------|
| **🟢 Acta de Inicio de Servicio** | Inicio formal del servicio | Al comenzar la prestación | `07-seguimiento/` |
| **📧 Invitación a Servicios** | Invitación específica para servicios | Licitación de servicios técnicos | `03-cartas-invitacion/` |
| **📋 Adjudicación de Servicio** | Adjudicación de servicio técnico | Selección de proveedor | `05-actas-adjudicacion/` |
| **📄 Contrato de Servicio** | Contrato específico de servicio | Formalización del servicio | `06-contratos/` |

#### 🎯 **Proceso Detallado de Generación**

##### Paso 1: Preparar Datos del Contrato
```
✅ Datos Básicos Completos:
   • Nombre del proyecto
   • Número de expediente  
   • Presupuesto base
   • Plazo de ejecución
   • Fechas clave (licitación, adjudicación)

✅ Empresas y Ofertas:
   • Lista de empresas invitadas
   • Ofertas económicas recibidas
   • Empresa adjudicataria seleccionada

✅ Firmantes Configurados:
   • Jefe de Proyecto
   • Responsable técnico
   • Cargos y representaciones
```

##### Paso 2: Seleccionar Documento a Generar

**En la Pestaña "Proyecto":**
1. **Scroll hacia abajo** hasta la sección "Generación de Documentos"
2. **Botones disponibles por fase**:

   ```
   🔄 FASE DE LICITACIÓN:
   ┌─────────────────────────┐
   │ [Generar Invitación]    │ ← Cartas a empresas
   └─────────────────────────┘
   
   📋 FASE DE ADJUDICACIÓN:
   ┌─────────────────────────┐
   │ [Generar Acta Adj]      │ ← Acta de adjudicación
   │ [Generar Carta Adj]     │ ← Cartas resultado
   └─────────────────────────┘
   
   🏗️ FASE DE EJECUCIÓN:
   ┌─────────────────────────┐
   │ [Generar Acta Inicio]   │ ← Inicio de trabajos
   │ [Generar Replanteo]     │ ← Solo obras
   │ [Generar Director]      │ ← Nombramiento
   │ [Generar Contrato]      │ ← Documento oficial
   └─────────────────────────┘
   
   ✅ FASE DE FINALIZACIÓN:
   ┌─────────────────────────┐
   │ [Generar Recepción]     │ ← Recepción trabajos
   │ [Generar Acta Liq]      │ ← Liquidación final
   └─────────────────────────┘
   ```

##### Paso 3: Generación Automática

1. **Clic en botón** del documento deseado
2. **Validación automática**: El sistema verifica datos requeridos
3. **Selección de plantilla**: Automática según tipo de contrato
4. **Sustitución de variables**: Reemplazo de marcadores en plantilla
5. **Generación de Word**: Documento .docx creado
6. **Conversión a PDF**: Automática si está disponible
7. **Guardado en carpeta**: Ubicación según tipo de documento

#### 🔧 **Variables de Plantilla Disponibles**

Las plantillas utilizan **marcadores automáticos** que se reemplazan por datos reales:

##### Variables de Contrato:
```
@nombreProyecto@          → Nombre completo del proyecto
@expediente@              → Número de expediente oficial  
@presupuestoBase@         → Presupuesto base (formato: 50.000,00 €)
@presupuestoBaseIVA@      → Presupuesto con IVA incluido
@plazoEjecucion@          → Plazo en días
@fechaContrato@           → Fecha del contrato (dd/mm/aaaa)
@fechaInicio@             → Fecha de inicio de trabajos
@fechaFinalizacion@       → Fecha prevista de finalización
@tipoContrato@            → Obra/Servicio/Mantenimiento
```

##### Variables de Empresa:
```
@empresaAdjudicataria@    → Nombre de la empresa seleccionada
@cifEmpresa@              → CIF de la empresa adjudicataria
@contactoEmpresa@         → Persona de contacto
@emailEmpresa@            → Email de contacto
@importeAdjudicacion@     → Importe de la oferta ganadora
@importeAdjudicacionIVA@  → Importe con IVA incluido
```

##### Variables de Firmantes:
```
@firmanteConforme@        → Nombre del jefe de proyecto
@cargoConforme@           → Cargo del firmante
@fechaFirma@              → Fecha de firma del documento
@lugarFirma@              → Lugar de firma (Madrid, por defecto)
```

##### Variables Especiales:
```
@listaEmpresas@           → Lista completa de empresas invitadas
@tablaOfertas@            → Tabla comparativa de ofertas
@resumenLiquidacion@      → Resumen económico de liquidación
@observaciones@           → Observaciones específicas del proyecto
```

#### 📁 **Ubicación de Documentos Generados**

Cada documento se guarda automáticamente en su carpeta correspondiente:

```
obras/[PROYECTO]/
├── 03-cartas-invitacion/
│   ├── Invitacion_[EMPRESA1].docx
│   ├── Invitacion_[EMPRESA1].pdf
│   └── ...
├── 05-actas-adjudicacion/
│   ├── Acta_Adjudicacion_[FECHA].docx
│   ├── Acta_Adjudicacion_[FECHA].pdf
│   ├── Carta_Adjudicacion_[EMPRESA_GANADORA].docx
│   └── Carta_No_Adjudicacion_[EMPRESA_X].docx
├── 06-contratos/
│   ├── Contrato_[EXPEDIENTE].docx
│   ├── Contrato_[EXPEDIENTE].pdf
│   └── Nombramiento_Director.docx
├── 07-seguimiento/
│   ├── Acta_Inicio_[FECHA].docx
│   ├── Acta_Replanteo_[FECHA].docx
│   └── Acta_Recepcion_[FECHA].docx
└── 08-liquidacion/
    ├── Acta_Liquidacion_[FECHA].docx
    └── Resumen_Economico.pdf
```

#### ⚠️ **Validaciones Automáticas**

Antes de generar cualquier documento, el sistema verifica:

✅ **Datos Obligatorios Completos**
✅ **Empresas con Ofertas Válidas** (para docs de adjudicación)
✅ **Fechas Coherentes** (inicio < fin)
✅ **Importes Numéricos Correctos**
✅ **Firmantes Configurados**
✅ **Plantillas Disponibles**

❌ **Si falta algún dato crítico**, se mostrará un mensaje específico:
```
⚠️ No se puede generar el documento
Faltan los siguientes datos obligatorios:
• Fecha de contrato
• Empresa adjudicataria
• Importe de adjudicación
```

### 💰 Sistema de Facturas Directas

El **sistema de facturas directas** es un módulo independiente para gestionar **contrataciones menores** y **servicios urgentes** que no requieren proceso de licitación pública.

#### 🎯 **¿Cuándo Usar Facturas Directas?**

✅ **Casos Apropiados:**
- **Servicios de urgencia** (reparaciones inmediatas)
- **Contrataciones menores** (por debajo del umbral de licitación)
- **Servicios especializados únicos** (empresa específica requerida)
- **Trabajos de mantenimiento rutinario**
- **Suministros menores** (materiales básicos)

❌ **No Usar Para:**
- Contratos que superen los umbrales legales
- Obras o servicios que requieren licitación pública
- Contratos con múltiples oferentes disponibles

#### 🖥️ **Acceso al Sistema**

**Pestaña "💰 Facturas Directas"** en la ventana principal:

```
┌─────────────────────────────────────────┐
│  💰 FACTURAS DIRECTAS                   │
│                                         │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ [Nueva Factura] │  │ [Buscar]        │ │
│  └─────────────────┘  └─────────────────┘ │
│                                         │
│  📋 LISTA DE FACTURAS:                  │
│  ┌─────────────────────────────────────┐ │
│  │ Estado │ Fecha │ Empresa │ Importe │ │
│  │   🟢   │01/03  │ ABC S.L.│ 1.250 € │ │
│  │   🟡   │15/03  │ XYZ LTD │ 2.800 € │ │
│  │   🔴   │20/03  │ UVW INC │   890 € │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

#### 📝 **Crear Nueva Factura Directa**

##### Paso 1: Datos Básicos
```
┌────────────── NUEVA FACTURA DIRECTA ──────────────┐
│                                                   │
│ 🏷️  Descripción del Servicio:                     │
│     ┌─────────────────────────────────────────┐   │
│     │ Reparación urgente sistema eléctrico   │   │
│     └─────────────────────────────────────────┘   │
│                                                   │
│ 🏢  Empresa Contratista:                          │
│     ┌─────────────────────────────────────────┐   │
│     │ Electricidad Industrial S.L.           │   │
│     └─────────────────────────────────────────┘   │
│                                                   │
│ 🆔  NIF/CIF de la Empresa:                        │
│     ┌─────────────────────────────────────────┐   │
│     │ B-12345678                              │   │
│     └─────────────────────────────────────────┘   │
│                                                   │
│ 💰  Importe Sin IVA:                              │
│     ┌─────────────────────────────────────────┐   │
│     │ 2.500,00 €                              │   │
│     └─────────────────────────────────────────┘   │
│                                                   │
│ 📅  Fecha de Solicitud:                           │
│     ┌─────────────────────────────────────────┐   │
│     │ 15/03/2024                              │   │
│     └─────────────────────────────────────────┘   │
│                                                   │
│ 🎯  Categoría de Servicio:                        │
│     ┌─────────────────────────────────────────┐   │
│     │ [Mantenimiento] [Obras] [Suministros]  │   │
│     └─────────────────────────────────────────┘   │
│                                                   │
│        [Guardar]  [Cancelar]  [Vista Previa]      │
└───────────────────────────────────────────────────┘
```

##### Paso 2: Información Adicional
```
┌──────── DETALLES ADICIONALES ────────┐
│                                       │
│ 📍 Ubicación del Trabajo:             │
│   ┌─────────────────────────────────┐ │
│   │ Estación Central - Andén 3     │ │
│   └─────────────────────────────────┘ │
│                                       │
│ ⏱️  Plazo de Ejecución:                │
│   ┌─────────────────────────────────┐ │
│   │ 5 días laborables              │ │
│   └─────────────────────────────────┘ │
│                                       │
│ 📧 Email de Contacto:                 │
│   ┌─────────────────────────────────┐ │
│   │ contacto@electricidad.com      │ │
│   └─────────────────────────────────┘ │
│                                       │
│ 📝 Observaciones:                     │
│   ┌─────────────────────────────────┐ │
│   │ Trabajo nocturno requerido     │ │
│   │ Certificaciones necesarias     │ │
│   └─────────────────────────────────┘ │
└───────────────────────────────────────┘
```

#### 🎛️ **Estados de Factura Directa**

El sistema gestiona **5 estados principales**:

| Estado | Icono | Descripción | Acciones Disponibles |
|--------|--------|-------------|---------------------|
| **🟢 Activa** | 🟢 | Factura en proceso de ejecución | Editar, Cerrar, Generar Orden |
| **🟡 Pendiente** | 🟡 | Esperando aprobación o inicio | Editar, Aprobar, Rechazar |
| **🔵 En Ejecución** | 🔵 | Trabajo en curso | Ver Progreso, Comunicar |
| **✅ Finalizada** | ✅ | Trabajo completado satisfactoriamente | Ver Resumen, Archivar |
| **🔴 Anulada** | 🔴 | Factura cancelada o rechazada | Ver Motivo, Archivar |

#### 💼 **Gestión de Límites y Controles**

##### Límites Automáticos por Tipo:
```
📊 LÍMITES DE CONTRATACIÓN DIRECTA:
┌─────────────────────────────────┐
│ 🏗️ OBRAS:           ≤ 40.000 € │
│ 🔧 SERVICIOS:       ≤ 15.000 € │
│ 📦 SUMINISTROS:     ≤ 15.000 € │
│ ⚡ URGENCIAS:       ≤ 60.000 € │
└─────────────────────────────────┘

⚠️ El sistema alertará automáticamente si
   se superan estos límites.
```

##### Controles de Acumulación:
```
🔍 CONTROL POR EMPRESA Y PERÍODO:
• Máximo 3 facturas/mes por empresa
• Límite acumulado anual por proveedor  
• Alerta si se supera el 80% del límite
• Informe automático de concentración
```

#### 📊 **Dashboard de Facturas**

**Vista Principal de la Pestaña:**

```
╔═══════════════════ DASHBOARD FACTURAS DIRECTAS ═══════════════════╗
║                                                                    ║
║ 📈 RESUMEN MENSUAL:                    📋 ACCIONES RÁPIDAS:        ║
║ ┌─────────────────────────────┐       ┌─────────────────────────┐  ║
║ │ Total Mes:      15.670,00 € │       │ [Nueva Factura]         │  ║
║ │ Pendientes:      3.200,00 € │       │ [Buscar Empresa]        │  ║
║ │ En Ejecución:    8.900,00 € │       │ [Informe Mensual]       │  ║
║ │ Finalizadas:     3.570,00 € │       │ [Exportar Excel]        │  ║
║ └─────────────────────────────┘       └─────────────────────────┘  ║
║                                                                    ║
║ 🎯 FILTROS Y BÚSQUEDA:                                             ║
║ Estado: [Todas▼] Mes: [Marzo 2024▼] Empresa: [Todas las empresas▼] ║
║                                                                    ║
║ 📋 LISTA DETALLADA:                                                ║
║ ┌──────────────────────────────────────────────────────────────┐   ║
║ │ Estado│Fecha    │ Empresa          │Descripción    │ Importe │   ║
║ │  🟢   │15/03/24 │ElectroServ S.L.  │Reparación LED │1.250,00€│   ║
║ │  🟡   │18/03/24 │Limpieza Pro      │Limpieza Urgent│  890,50€│   ║
║ │  🔵   │20/03/24 │Fontanería ADIF   │Fuga Tubería   │2.100,00€│   ║
║ │  ✅   │22/03/24 │Jardinería Verde  │Poda Arboles   │  750,00€│   ║
║ └──────────────────────────────────────────────────────────────┘   ║
╚════════════════════════════════════════════════════════════════════╝
```

#### 📄 **Documentos Generados**

##### Órdenes de Trabajo:
```
📋 ORDEN DE TRABAJO Nº: FD-2024-0047
════════════════════════════════════════
🏢 EMPRESA: Electricidad Industrial S.L.
🆔 NIF: B-12345678
📧 CONTACTO: contacto@electricidad.com

📋 DESCRIPCIÓN DEL TRABAJO:
Reparación urgente del sistema eléctrico
en Estación Central - Andén 3

💰 IMPORTE:
- Base imponible:    2.500,00 €
- IVA (21%):          525,00 €  
- TOTAL:            3.025,00 €

⏱️ PLAZO: 5 días laborables
📅 FECHA LÍMITE: 20/03/2024

📝 CONDICIONES ESPECIALES:
• Trabajo nocturno autorizado
• Certificaciones técnicas requeridas
• Coordinación con Jefe de Estación

👤 RESPONSABLE ADIF: Juan Pérez
📧 EMAIL: juan.perez@adif.es
☎️ TELÉFONO: 912 345 678
```

##### Justificación de Contratación Directa:
```
📋 JUSTIFICACIÓN CONTRATACIÓN DIRECTA
═══════════════════════════════════════

🎯 MOTIVO DE URGENCIA:
Fallo en sistema eléctrico que afecta
a la operatividad de la estación.

⚖️ JUSTIFICACIÓN LEGAL:
Artículo 120 de la Ley 9/2017, de 8 de
noviembre, de Contratos del Sector Público.

💰 LÍMITE RESPETADO:
Importe: 2.500,00 € < 15.000,00 €
(Límite servicios contratación directa)

✅ AUTORIZACIÓN:
Jefe de Proyecto: Juan Pérez Martín
Fecha: 15/03/2024
```

#### 🔍 **Búsqueda y Filtrado Avanzado**

**Panel de Filtros Disponibles:**

```
┌─────────── BÚSQUEDA AVANZADA ───────────┐
│                                         │
│ 🗓️ Rango de Fechas:                     │
│   Desde: [01/03/2024] Hasta: [31/03/24] │
│                                         │  
│ 🏢 Empresa:                             │
│   [Todas] [ElectroServ] [Limpieza Pro]  │
│                                         │
│ 💰 Rango de Importes:                   │
│   Mínimo: [0 €] Máximo: [5.000 €]      │
│                                         │
│ 🎯 Categoría:                           │
│   [Todas] [Mantenimiento] [Urgencias]  │
│                                         │
│ 📍 Ubicación:                           │
│   ┌─────────────────────────────────┐   │
│   │ Estación Central               │   │
│   └─────────────────────────────────┘   │
│                                         │
│ 📝 Texto en Descripción:                │
│   ┌─────────────────────────────────┐   │
│   │ eléctrico                      │   │
│   └─────────────────────────────────┘   │
│                                         │
│    [Buscar] [Limpiar] [Exportar]        │
└─────────────────────────────────────────┘
```

#### 📈 **Informes y Estadísticas**

##### Informe Mensual Automático:
```
📊 INFORME FACTURAS DIRECTAS - MARZO 2024
═══════════════════════════════════════════

📈 RESUMEN EJECUTIVO:
• Total Facturas: 12
• Importe Total: 28.450,00 €
• Promedio por Factura: 2.370,83 €
• Facturas Finalizadas: 8 (66,7%)

🏢 TOP 5 EMPRESAS:
1. ElectroServ S.L.      8.950,00 € (5 facturas)
2. Limpieza Professional 4.200,00 € (3 facturas)  
3. Fontanería ADIF       3.890,00 € (2 facturas)
4. Jardinería Verde      2.100,00 € (1 factura)
5. Carpintería Moderna   1.750,00 € (1 factura)

📊 POR CATEGORÍA:
• Mantenimiento:    45% (12.802,50 €)
• Urgencias:        30% ( 8.535,00 €)
• Suministros:      15% ( 4.267,50 €)
• Obras Menores:    10% ( 2.845,00 €)

⚠️ ALERTAS Y RECOMENDACIONES:
• ElectroServ S.L. supera 50% del límite mensual
• Considerar licitación para trabajos eléctricos
• 3 facturas pendientes requieren seguimiento
```

#### 🔐 **Control de Acceso y Permisos**

```
👤 ROLES Y PERMISOS:
┌─────────────────────────────────────┐
│ 👨‍💼 JEFE DE PROYECTO:                  │
│    ✅ Crear facturas hasta 15.000€   │
│    ✅ Aprobar todas las facturas     │
│    ✅ Ver informes completos         │
│    ✅ Exportar datos                 │
│                                     │
│ 👩‍🔧 TÉCNICO RESPONSABLE:              │
│    ✅ Crear facturas hasta 5.000€    │
│    ⏸️ Aprobar pendiente superior     │
│    ✅ Ver facturas propias           │
│    ❌ Acceso restringido informes    │
│                                     │
│ 👨‍💻 ADMINISTRATIVO:                   │
│    ⏸️ Solo lectura                   │
│    ✅ Generar informes básicos       │
│    ✅ Contactar con empresas         │
│    ❌ Modificar importes             │
└─────────────────────────────────────┘
```

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

### Versión 3.2 (Actual) ✅
- [x] **Splash screen profesional** con logo ADIF
- [x] **Iconos en barra de tareas** y ventanas
- [x] **Optimización de arranque** con lazy loading
- [x] **Logs organizados** en _internal/ para EXE
- [x] **Sistema de facturas directas** completamente funcional
- [x] **Dashboard avanzado** con estadísticas
- [x] **Compilación optimizada** para distribución
- [x] **Interfaz mejorada** con tema corporativo

### Versión 3.3 (Próxima)
- [ ] **Integración con sistemas ADIF** corporativos
- [ ] **Notificaciones automáticas** por email
- [ ] **Dashboard ejecutivo** con KPIs
- [ ] **API REST** para integraciones externas
- [ ] **Workflow automatizado** de aprobaciones
- [ ] **Firma digital** integrada

### Versión 4.0 (Futuro)
- [ ] **Módulo de reporting avanzado** con BI
- [ ] **App móvil complementaria** para supervisión
- [ ] **Integración con ERP ADIF**
- [ ] **Módulo de planificación** de recursos
- [ ] **Sistema de alertas** predictivas
- [ ] **Dashboard en tiempo real**

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

## 📊 Estadísticas del Proyecto

- **📅 Última actualización**: Septiembre 2024
- **📝 Versión README**: 2.0 (Completamente expandido)
- **⚡ Líneas de código**: +15.000 líneas Python
- **📁 Archivos proyecto**: +50 módulos organizados
- **🏗️ Documentos generados**: +15 tipos diferentes
- **💼 Empresas gestionadas**: Sin límite
- **📋 Contratos activos**: Capacidad ilimitada
- **🔧 Tiempo desarrollo**: +6 meses de desarrollo activo
- **✅ Estado**: **Producción estable v3.2**

---

*📋 README completamente expandido con guías detalladas de uso*  
*🎯 Incluye: interfaz, documentos, facturas directas, y todas las funcionalidades*  
*⚡ Optimizado para nuevos usuarios y administradores del sistema*