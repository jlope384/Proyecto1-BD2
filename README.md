# Restaurant System API

API REST para administrar un ecosistema de restaurantes, usuarios, reseñas, pedidos e historial de órdenes. El backend está construido con FastAPI y MongoDB (con GridFS para archivos) y está listo para ejecutarse tanto en local como en Docker.

## Características principales

- CRUD completo de `users`, `restaurants` y `reviews`.
- Registro de pedidos activos por usuario y actualización de métricas del restaurante.
- Consulta de histórico de órdenes consolidado.
- Gestión de archivos binarios mediante GridFS (`/files`).
- Endpoint de salud `/ping` para monitoreo rápido.

## Stack tecnológico

- **Framework:** FastAPI + Uvicorn.
- **Base de datos:** MongoDB Atlas (o cualquier instancia compatible).
- **Almacenamiento de archivos:** GridFS.
- **Infraestructura opcional:** Docker Compose para empaquetar el servicio.

## Estructura de carpetas

```
Proyecto1-BD2/
├─ backend/
│  ├─ main.py              # Punto de entrada FastAPI
│  ├─ database.py          # Conexión a MongoDB y GridFS
│  ├─ routers/             # Endpoints agrupados por dominio
│  ├─ utils/utils.py       # Serialización de ObjectId
│  ├─ requirements.txt     # Dependencias
│  └─ docker-compose.yml   # Orquestación opcional
└─ docs/preliminars/       # Documentación adicional del curso
```

## Variables de entorno

Crea un archivo `backend/.env` con al menos las siguientes claves (muestra tomada del repositorio):

```
MONGO_URI=mongodb+srv://<usuario>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=restaurant_system
```

## Puesta en marcha (local)

1. Crear y activar un entorno virtual (opcional pero recomendado).
2. Instalar dependencias:
	```bash
	cd backend
	pip install -r requirements.txt
	```
3. Ejecutar el servidor:
	```bash
	uvicorn main:app --reload --port 8000
	```
4. Visitar `http://localhost:8000/docs` para probar los endpoints desde la interfaz interactiva de Swagger.

## Puesta en marcha con Docker

```
cd backend
docker compose up --build
```

El servicio quedará expuesto en `http://localhost:8000` y usará el mismo archivo `.env` definido anteriormente.

## Endpoints disponibles

### Usuarios (`/users`)

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/users/` | Crea un usuario con campo `orders` vacío. |
| GET | `/users/` | Lista todos los usuarios. |
| GET | `/users/{user_id}` | Recupera un usuario por su `ObjectId`. |
| DELETE | `/users/{user_id}` | Elimina un usuario. |

### Restaurantes (`/restaurants`)

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/restaurants/` | Crea un restaurante con `total_orders` en cero. |
| GET | `/restaurants/` | Lista todos los restaurantes. |
| GET | `/restaurants/{restaurant_id}` | Obtiene la información de un restaurante. |
| DELETE | `/restaurants/{restaurant_id}` | Elimina un restaurante. |

### Reseñas (`/reviews`)

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/reviews/` | Crea una reseña (requiere `from_user` y `for_restaurant`). |
| GET | `/reviews/` | Lista todas las reseñas. |
| GET | `/reviews/restaurant/{restaurant_id}` | Reseñas por restaurante. |
| DELETE | `/reviews/{review_id}` | Elimina una reseña. |

### Pedidos (`/orders`)

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/orders/` | Crea un pedido y lo agrega al usuario indicado, actualizando `total_orders`. |
| GET | `/orders/user/{user_id}` | Lista los pedidos asociados a un usuario. |

### Histórico de pedidos (`/orders-historic`)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/orders-historic/` | Devuelve el historial consolidado de órdenes. |

### Archivos (`/files`)

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/files/upload` | Sube un archivo binario a GridFS y devuelve el `file_id`. |
| GET | `/files/{file_id}` | Descarga el archivo almacenado. |

## Utilidades

- Serialización consistente de documentos Mongo (`utils/utils.py`).
- `database.py` expone las colecciones y la instancia de GridFS para su uso en los routers.

## Referencias adicionales

- Documentación del curso / entregables: revisa la carpeta `docs/preliminars/` para diagramas e índices.
- Para validar conectividad rápidamente, usa `GET /ping`.

¡Listo! Con esto deberías poder levantar el servicio y extenderlo según las necesidades del proyecto.
