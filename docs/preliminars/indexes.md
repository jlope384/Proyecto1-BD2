# Preliminar Indexes

## Restaurants

- `{ name: 1 }`
  - Búsqueda rápida por nombre del restaurante.

- `{ avg_rating: -1 }`
  - Ordenamiento por calificación (mejor valorados primero).

- `{ price_range: 1 }`
  - Filtrado por rango de precios.

- `{ name: "text", type_of_food: "text" }`
  - Búsqueda de texto completo por nombre y tipo de comida.

- `{ name: 1, location: 1 }`
  - Búsqueda por nombre dentro de un área específica.

- `{ type_of_food: 1, avg_rating: -1 }`
  - Filtrar por tipo de comida y ordenar por calificación.

- `{ price_range: 1, avg_rating: -1 }`
  - Filtrar por rango de precios y ordenar por calificación.

- `{ type_of_food: 1 }`
  - Índice multikey porque es un arreglo (`string[]`).

- `{ "menu_items.name": 1 }`
  - Búsqueda de ítems del menú por nombre.

- `{ location: "2dsphere" }`
  - Índice geoespacial para consultas:
    - `$near`
    - `$geoWithin`
    - Búsqueda por distancia.

---

## Users

- `{ username: 1 }`
  - Búsqueda rápida para login y validación de usuario único.

---

## Reviews

- `{ from_user: 1 }`
  - Obtener todas las reseñas hechas por un usuario.

- `{ for_restaurant: 1 }`
  - Obtener todas las reseñas de un restaurante.

- `{ for_restaurant: 1, score: -1 }`
  - Obtener reseñas de un restaurante ordenadas por puntuación.

- `{ for_restaurant: 1, from_user: 1 }`
  - Garantizar una reseña por usuario por restaurante.

- `{ photos_url: 1 }`
  - Índice multikey sobre arreglo de URLs de fotos.

- `{ comment: "text" }`
  - Búsqueda de texto completo en comentarios.

---

## Orders (dentro de Users)

- `{ "orders.order_number_per_restaurant": 1 }`
  - Buscar un número de orden específico por restaurante.

- `{ "orders.for_restaurant": 1 }`
  - Obtener órdenes de un usuario para un restaurante específico.

- `{ "orders.payed": 1 }`
  - Filtrar órdenes pagadas / no pagadas.

- `{ "orders.completed": 1 }`
  - Filtrar órdenes completadas / no completadas.

- `{ "orders.for_restaurant": 1, "orders.payed": 1 }`
  - Órdenes por restaurante filtradas por estado de pago.

- `{ "orders.for_restaurant": 1, "orders.completed": 1 }`
  - Órdenes por restaurante filtradas por estado de finalización.

- `{ "orders.menu_items.menu_item_id_from_restaurant": 1 }`
  - Buscar órdenes que contengan un ítem de menú específico.pecific menu item.
