# 🌾 Sistema de Inventario Agrícola Inteligente

## 💡 Descripción del Proyecto
El Sistema de Inventario Agrícola Inteligente permite administrar productos agrícolas (semillas, abonos, herbicidas, herramientas), registrar movimientos de entrada y salida, 
gestionar proveedores y generar alertas automáticas cuando el stock se encuentra en niveles críticos.

Este proyecto está dividido en módulos independientes, cada uno representado por una app de Django, desarrollada por diferentes integrantes del equipo bajo un flujo de trabajo Git profesional.

## 🖥️ Aplicaciones del proyecto

1️⃣ Productos
Gestiona el catálogo de productos agrícolas (semillas, abonos, herbicidas, herramientas).
Incluye filtros por categoría, estado y unidad de medida.

2️⃣ Movimientos
Registra entradas y salidas de inventario.
Incluye validación automática de stock (no permite stock negativo).
Cada movimiento actualiza el stock del producto.

3️⃣ Proveedores
Administra la información de proveedores asociados a la compra de productos.

4️⃣ Alertas de Stock
Genera alertas automáticas cuando un producto alcanza un stock mínimo.
Incluye endpoint especial para:
✔ Reporte de productos críticos
✔ Alertas activas e históricas

## 🛠 Requerimientos Técnicos
- Python 
- Django 
- Django REST Framework
- django-environ o python-decouple
- drf-yasg (Swagger)
- Base de datos (SQLite, PostgreSQL o la que el grupo defina)

## 🔌 Instalación y Ejecución del Proyecto
### 1. Clonar el repositorio
```bash
git clone https://github.com/Mariaferrojas/Proyecto_Agricola.git
```
### 2. Crear el entorno virtual
```bash
python -m venv .venv
source .venv/Scripts/activate
```
### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```
### 4. Configurar el archivo .env
```bash
cp .env.example .env
```
### 5. Aplicar migraciones
```bash
python manage.py migrate
```
### 6. Ejecutar el servidor
```bash
python manage.py runserver
```
### 7. Acceder a la documentación 

## 📁 Estructura del Proyecto

```
├── Proyecto_Agricola/
│── .venv
│   ├── Include
│   ├── Lib
│   ├── .gitignore
│   ├── pyvenv.cfg
│
|
├── Alertas/
|    ├── management/Commands
|       ├── crear_configuraciones_iniciales.py
│   ├── _init_.py
│   ├── admin.py
│   ├── apps.py
|   ├── filters.py
│   ├── models.py
│   ├── serializers.py
|   ├── services.py
|   ├── signals.py
|   ├── tests.py
│   ├── urls.py
│   ├── views.py
|
|
├── Productos/
|    ├── management/Commands
|       ├── crear_configuraciones_iniciales.py
│   ├── _init_.py
│   ├── admin.py
│   ├── apps.py
|   ├── filters.py
│   ├── models.py
│   ├── serializers.py
|   ├── signals.py
|   ├── tests.py
│   ├── urls.py
│   ├── views.py
|
|
├── config/
│   ├── _init_.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
|
│
├── movimientos/
│   ├── _init_.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
|   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   
│
├── proveedores/
│   ├── _init_.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
|   ├── tests.py
│   ├── urls.py
│   ├── views.py
│
│
├── staticfiles/
|   ├── admin
|   ├── drf-yasg
|   ├── rest_framework
|
├── .env
├── .env.example
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 🔐 Uso de .env + .env.example

```
DEBUG=
SECRET_KEY=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

## 📘 Diagrama de la base de datos general
```bash
+---------------------+        +----------------------+        +----------------------+
|   CategoriaProducto | 1 ---- |      Producto        | ---- N |     Proveedor        |
+---------------------+        +----------------------+        +----------------------+
| id (PK)             |        | id (PK)              |        | id (PK)              |
| nombre              |        | nombre               |        | nombre               |
| descripcion         |        | categoria_id (FK)    |        | telefono             |
|                     |        | stock_minimo         |        | email                |
|                     |        | stock_maximo         |        | direccion            |
+---------------------+        | stock_actual         |        | ciudad               |
                               | fecha_vencimiento    |        | activo               |
                               +----------------------+        +----------------------+
                                         |
                                         | 1
                                         |
                                         N
                               +----------------------+
                               |     Movimiento       |
                               +----------------------+
                               | id (PK)              |
                               | producto_id (FK)     |
                               | tipo                 |
                               | cantidad             |
                               | fecha                |
                               +----------------------+
                                         |
                                         | 1
                                         |
                                         N
                               +----------------------+
                               |       Alerta         |
                               +----------------------+
                               | id (PK)              |
                               | producto_id (FK)     |
                               | movimiento_id (FK)   |
                               | nivel_stock          |
                               | estado               |
                               | tipo_alerta          |
                               | fecha                |
                               +----------------------+
```
***Explicación del diagrama general***
- El diagrama general muestra cómo se relacionan todas las aplicaciones del sistema. Un producto pertenece a una categoría y puede estar asociado a uno o varios proveedores. A partir de los productos se generan los movimientos (entradas o salidas), y a su vez, las alertas se crean en función del stock o los movimientos registrados. Representa toda la estructura principal del proyecto.

## 📐 Diagrama de la base de datos por aplicacio 

`Productos`
```bash
Tabla: CategoriaProducto
------------------------------------
id (PK)
nombre
descripcion


Tabla: Producto
------------------------------------
id (PK)
nombre
descripcion
categoria_id (FK → CategoriaProducto.id)
unidad_medida
stock_minimo
stock_maximo
stock_actual
precio_compra
precio_venta
fecha_vencimiento
activo
fecha_creacion
fecha_actualizacion


Tabla: HistorialPrecio
------------------------------------
id (PK)
producto_id (FK → Producto.id)
precio_anterior
nuevo_precio
fecha_cambio
```
**Explicación del diagrama Prodcuto**
- El módulo de Productos maneja toda la información relacionada con los insumos agrícolas: categorías, precios, unidades de medida y control de stock. También lleva un historial de precios para registrar cualquier cambio. Es la base del inventario.

`Movimientos`
```bash
Tabla: Movimiento
------------------------------------
id (PK)
producto_id (FK → Producto.id)
tipo  (entrada/salida)
cantidad
fecha
observacion


Tabla: MovimientoExtra
------------------------------------
id (PK)
movimiento_id (FK → Movimiento.id)
usuario_responsable
ubicacion
notas_adicionales
```
***Explicación del diagrama Movimientos***
Este módulo registra todas las entradas y salidas de productos en el inventario. Permite controlar cuántas unidades ingresan o salen y mantiene un registro adicional con información opcional como ubicación o responsable del movimiento.

`Alertas`
```bash
Tabla: Alerta
------------------------------------
id (PK)
producto_id (FK → Producto.id)
movimiento_id (FK → Movimiento.id)
nivel_stock
tipo_alerta
estado
fecha_creacion
fecha_actualizacion
auto_generada
repetible
notas


Tabla: ConfiguracionAlerta
------------------------------------
id (PK)
activo
dias_vencimiento
umbral_stock
notificaciones_email
fecha_actualizacion


Tabla: HistorialAlerta
------------------------------------
id (PK)
alerta_id (FK → Alerta.id)
accion
usuario
fecha
comentario
```
***Explicación del módulo Alertas***
Este módulo administra las alertas del sistema, como stock bajo, vencimiento próximo o movimientos críticos. Incluye una configuración global para automatizar notificaciones y un historial para llevar control de todas las acciones realizadas sobre cada alerta. 

`Provedores`
```bash
Tabla: Proveedor
------------------------------------
id (PK)
nombre
nombre_contacto
telefono
email
direccion
ciudad
activo
fecha_creacion
```
***Explicación del módulo Provedores***
- El módulo de Proveedores almacena los datos de las empresas o personas que suministran los productos agrícolas. Aquí se centraliza la información de contacto, estado y ubicación de cada proveedor.

## 📄 Documentación Swagger
-

## 🧪 Endpoints por Aplicación

1️⃣ `Productos — /api/productos/`

***Categorías***
- /api/productos/categorias/
- /api/productos/categorias/{id}/
- /api/productos/categorias/{id}/productos/

***Productos***
- /api/productos/productos/
- /api/productos/productos/{id}/
- /api/productos/productos/{id}/historial_precios/

***Acciones***
- /api/productos/productos/stock_critico/
- /api/productos/productos/stock_agotado/
- /api/productos/productos/proximos_vencer/
- /api/productos/productos/resumen_inventario/
- /api/productos/productos/exportar_csv/

***Historial de precios***
- /api/productos/historial-precios/
- /api/productos/historial-precios/{id}/

2️⃣ `Movimientos  — /api/movimientos/`
- /api/movimientos/movimientos/
- /api/movimientos/movimientos/{id}/

3️⃣ `Proveedores — /api/proveedores/`
- /api/proveedores/
- /api/proveedores/{id}/

4️⃣ `Alertas de Stock — /api/alertas/`
- /api/alertas/alertas/
- /api/alertas/alertas/{id}/
- /api/alertas/alertas/{id}/marcar_leida/
- /api/alertas/alertas/{id}/marcar_atendida/
- /api/alertas/alertas/{id}/descartar/
- /api/alertas/alertas/{id}/reactivar/
- /api/alertas/alertas/crear_manual/
- /api/alertas/alertas/revisar_automaticas/
- /api/alertas/alertas/resumen/
- /api/alertas/alertas/pendientes_urgentes/
- /api/alertas/alertas/limpiar_antiguas/

***Configuraciones***
- /api/alertas/configuraciones/
- /api/alertas/configuraciones/{id}/
- /api/alertas/configuraciones/resetear_configuraciones/

***Historial***
- /api/alertas/historial/
- /api/alertas/historial/{id}/

5️⃣ `Principal (root)`
- /admin/
- /swagger/
- /redoc/
- /swagger.json
- /swagger.yaml

## 🧭 Flujo de Trabajo con Git
- `Ramas`
- main → Rama estable del proyecto
- feature-nombre-app → Rama por integrante

- `Pasos del flujo`
- Crear rama desde main
- Desarrollar la aplicación individual
- Hacer commits frecuentes
- El líder revisa y aprueba
- Se actualiza main totalmente funcional

## 👥 Roles del Equipo
**Líder - Maria Fernanda Rojas:** configura proyecto base, estructura, CI, revisa PRs

**Integrantes - Hugo Mancera - Angelica Garcia:** desarrollan una app independiente 

**Todos:** pruebas, documentación, control de versiones




