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
|   |  ├── management/Commands
|        ├── crear_configuraciones_iniciales.py
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
|   |  ├── management/Commands
|         ├── crear_configuraciones_iniciales.py
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
|   ├──
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

## 📘 Diagrama de la base de datos general y por aplicación


## 📄 Documentación Swagger
-

## 🧪 Endpoints por Aplicación

1️⃣ Productos
- POST `/api/productos/`
- GET `/api/productos/`
- GET `/api/productos/{id}/`
- PUT `/api/productos/{id}/`
- DELETE `/api/productos/{id}/`
- GET `/api/productos/?categoria=semillas`
- GET `/api/productos/?stock_minimo=true`

2️⃣ Movimientos
- POST `/api/movimientos/`
- GET `/api/movimientos/`
- GET `/api/movimientos/{id}/`
- PUT `/api/movimientos/{id}/`
- DELETE `/api/movimientos/{id}/`
- GET `/api/movimientos/?tipo=entrada`
- GET `/api/movimientos/?fecha_inicio&fecha_fin`
- Endpoint lógico: `/api/movimientos/resumen/`

3️⃣ Proveedores
- POST `/api/proveedores/`
- GET `/api/proveedores/`
- GET `/api/proveedores/{id}/`
- PUT `/api/proveedores/{id}/`
- DELETE `/api/proveedores/{id}/`
- GET `/api/proveedores/?pais=colombia`

4️⃣ Alertas de Stock
- GET `/api/alertas/`
- GET `/api/alertas/activas/`
- GET `/api/alertas/producto/{id}/`
- DELETE `/api/alertas/{id}/`
- Endpoint especial:
`/api/alertas/criticos/` → lista productos con stock crítico
`/api/alertas/generar/` → fuerza generación de alertas

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
**Líder:** configura proyecto base, estructura, CI, revisa PRs

**Integrantes:** desarrollan una app independiente siguiendo requisitos

**Todos:** pruebas, documentación, control de versiones



