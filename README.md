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

## 📘 Diagrama de la base de datos general y por aplicación


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
**Líder-Maria Fernanda Rojas:** configura proyecto base, estructura, CI, revisa PRs

**Integrantes-Hugo Mancera, Angelica Garcia:** desarrollan una app independiente 

**Todos:** pruebas, documentación, control de versiones




