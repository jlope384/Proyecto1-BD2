// =====================================================
// SEED MASIVO PARA restaurant_system
// Inserta 50,000 documentos en total:
//   - 3,000 restaurants
//   - 12,000 users
//   - 10,000 reviews
//   - 25,000 orders_historic
// =====================================================

const dbName = "restaurant_system";
const database = db.getSiblingDB(dbName);

print(`Usando base de datos: ${dbName}`);

// -----------------------------
// CONFIGURACION
// -----------------------------
const TOTAL_RESTAURANTS = 3000;
const TOTAL_USERS = 12000;
const TOTAL_REVIEWS = 10000;
const TOTAL_ORDERS_HISTORIC = 25000;
const BATCH_SIZE = 1000;

// -----------------------------
// HELPERS
// -----------------------------
function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randFloat(min, max, decimals = 1) {
  return Number((Math.random() * (max - min) + min).toFixed(decimals));
}

function pickOne(arr) {
  return arr[randInt(0, arr.length - 1)];
}

function pickMany(arr, count) {
  const copy = [...arr];
  const result = [];
  while (result.length < count && copy.length > 0) {
    const idx = randInt(0, copy.length - 1);
    result.push(copy.splice(idx, 1)[0]);
  }
  return result;
}

function randomDate(start, end) {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

function randomUsername(i) {
  return `user_${i}_${randInt(1000, 9999)}`;
}

function randomRestaurantName(i) {
  const prefixes = ["Pizza", "Burger", "Taco", "Sushi", "Pasta", "Grill", "Urban", "Golden", "Happy", "Fresh", "Royal", "Deluxe"];
  const suffixes = ["Place", "House", "Corner", "Hub", "Express", "Kitchen", "Spot", "Bistro", "Station", "Palace"];
  return `${pickOne(prefixes)} ${pickOne(suffixes)} ${i}`;
}

function randomFoodTypes() {
  const foodTypes = [
    "Italian", "Pizza", "Mexican", "Tacos", "American", "Burgers",
    "Japanese", "Sushi", "Chinese", "Desserts", "Fast Food",
    "Seafood", "Grill", "Healthy", "Vegetarian", "Coffee", "Bakery"
  ];
  return pickMany(foodTypes, randInt(1, 3));
}

function randomComment() {
  const comments = [
    "Amazing food!",
    "Quick delivery",
    "Great taste",
    "Would order again",
    "Excellent service",
    "Very fresh",
    "Decent price",
    "Loved the presentation",
    "Portion size was good",
    "Could be better",
    "Hot and delicious",
    "Fast and reliable"
  ];
  return pickOne(comments);
}

function randomOrderNote() {
  const notes = [
    "No onions",
    "Extra cheese",
    "Deliver fast",
    "Call when outside",
    "Spicy please",
    "No sauce",
    "Extra napkins",
    "Leave at the door",
    "Well cooked",
    "Test historic"
  ];
  return pickOne(notes);
}

function randomPhotoUrl() {
  const files = [
    "fotos/bulbasaur.jpg",
    "fotos/charmeleon.jpg",
    "fotos/squirtle.jpg"
  ];
  return pickOne(files);
}

function randomCoordinates() {
  return [
    randFloat(-180, 180, 6), // longitude
    randFloat(-90, 90, 6)    // latitude
  ];
}

function buildMenuItems() {
  const menuNames = [
    "Pepperoni", "Hawaiian", "Cheeseburger", "Double Burger", "Taco Supreme",
    "Veggie Pizza", "Chicken Wings", "Pasta Alfredo", "Sushi Roll", "Fish Taco",
    "Margarita Pizza", "BBQ Burger", "Caesar Salad", "Ramen Bowl", "Fries"
  ];

  const total = randInt(5, 12);
  const items = [];

  for (let i = 0; i < total; i++) {
    items.push({
      _id: new ObjectId(),
      name: `${pickOne(menuNames)} ${i + 1}`,
      price: randInt(5, 30)
    });
  }

  return items;
}

function sampleMenuItems(menuItems) {
  const amount = randInt(1, Math.min(4, menuItems.length));
  const chosen = pickMany(menuItems, amount);

  return chosen.map(item => ({
    quantity: randInt(1, 4),
    menu_item_id_from_restaurant: item._id,
    menu_note: randomOrderNote()
  }));
}

// -----------------------------
// LIMPIEZA OPCIONAL
// -----------------------------
print("Limpiando colecciones...");
database.restaurants.deleteMany({});
database.users.deleteMany({});
database.reviews.deleteMany({});
database.orders_historic.deleteMany({});

// Si quieres limpiar GridFS también, descomenta:
// database.getCollection("fs.files").deleteMany({});
// database.getCollection("fs.chunks").deleteMany({});

// -----------------------------
// 1) RESTAURANTS
// -----------------------------
print(`Insertando ${TOTAL_RESTAURANTS} restaurantes...`);

const restaurantIds = [];
const restaurantData = []; // guardamos info para reutilizar menu_items

let restaurantBatch = [];

for (let i = 1; i <= TOTAL_RESTAURANTS; i++) {
  const _id = new ObjectId();
  const menuItems = buildMenuItems();
  const totalOrdersSeed = randInt(0, 300);

  const doc = {
    _id,
    name: randomRestaurantName(i),
    avg_rating: randFloat(1, 5, 1),
    location: {
      type: "Point",
      coordinates: randomCoordinates()
    },
    type_of_food: randomFoodTypes(),
    price_range: {
      min: randInt(5, 15),
      max: randInt(16, 40)
    },
    menu_items: menuItems,
    total_orders: totalOrdersSeed,
    created_at: randomDate(new Date("2024-01-01"), new Date()),
    active: Math.random() < 0.9,
    updated_at: new Date()
  };

  restaurantBatch.push(doc);
  restaurantIds.push(_id);
  restaurantData.push({
    _id,
    menu_items: menuItems
  });

  if (restaurantBatch.length === BATCH_SIZE) {
    database.restaurants.insertMany(restaurantBatch);
    print(`  Restaurantes insertados: ${i}`);
    restaurantBatch = [];
  }
}

if (restaurantBatch.length > 0) {
  database.restaurants.insertMany(restaurantBatch);
}

// -----------------------------
// 2) USERS
// -----------------------------
print(`Insertando ${TOTAL_USERS} usuarios...`);

const userIds = [];
let userBatch = [];

for (let i = 1; i <= TOTAL_USERS; i++) {
  const _id = new ObjectId();

  const embeddedOrdersCount = randInt(1, 3);
  const embeddedOrders = [];

  for (let j = 0; j < embeddedOrdersCount; j++) {
    const restaurant = pickOne(restaurantData);
    embeddedOrders.push({
      order_number_per_restaurant: j + 1,
      for_restaurant: restaurant._id,
      created_at: randomDate(new Date("2024-01-01"), new Date()),
      menu_items: sampleMenuItems(restaurant.menu_items),
      paid: Math.random() < 0.85,
      total_quantity: randInt(1, 8),
      note: randomOrderNote(),
      completed: Math.random() < 0.7
    });
  }

  const userDoc = {
    _id,
    username: randomUsername(i),
    hashed_password_with_user_sided_salt: `hashed_password_${randInt(100000, 999999)}`,
    created_at: randomDate(new Date("2024-01-01"), new Date()),
    orders: embeddedOrders
  };

  userBatch.push(userDoc);
  userIds.push(_id);

  if (userBatch.length === BATCH_SIZE) {
    database.users.insertMany(userBatch);
    print(`  Usuarios insertados: ${i}`);
    userBatch = [];
  }
}

if (userBatch.length > 0) {
  database.users.insertMany(userBatch);
}

// -----------------------------
// 3) REVIEWS
// -----------------------------
print(`Insertando ${TOTAL_REVIEWS} reviews...`);

let reviewBatch = [];

for (let i = 1; i <= TOTAL_REVIEWS; i++) {
  const reviewDoc = {
    _id: new ObjectId(),
    from_user: pickOne(userIds),
    for_restaurant: pickOne(restaurantIds),
    comment: randomComment(),
    score: randInt(1, 5),
    photos_url: Math.random() < 0.4 ? [randomPhotoUrl()] : [],
    created_at: randomDate(new Date("2024-01-01"), new Date())
  };

  reviewBatch.push(reviewDoc);

  if (reviewBatch.length === BATCH_SIZE) {
  try {
    database.reviews.insertMany(reviewBatch, { ordered: false });
  } catch (e) {
    // Ignora duplicados por índice único
  }
  print(`  Reviews insertadas: ${i}`);
  reviewBatch = [];
}
}

if (reviewBatch.length > 0) {
  try {
    database.reviews.insertMany(reviewBatch, { ordered: false });
  } catch (e) {
    // Ignora duplicados
  }
}

// -----------------------------
// 4) ORDERS_HISTORIC
// -----------------------------
print(`Insertando ${TOTAL_ORDERS_HISTORIC} órdenes históricas...`);

let orderHistoricBatch = [];

// para incrementar total_orders de restaurants según órdenes históricas
const restaurantOrderCounter = {};

for (let i = 1; i <= TOTAL_ORDERS_HISTORIC; i++) {
  const restaurant = pickOne(restaurantData);
  const userId = pickOne(userIds);

  const orderDoc = {
    _id: new ObjectId(),
    from_user: userId,
    archived_at: randomDate(new Date("2025-01-01"), new Date()),
    order_data: {
      order_number_per_restaurant: randInt(1, 5000),
      for_restaurant: restaurant._id,
      created_at: randomDate(new Date("2024-01-01"), new Date()),
      menu_items: sampleMenuItems(restaurant.menu_items),
      paid: Math.random() < 0.9,
      total_quantity: randInt(1, 10),
      note: randomOrderNote(),
      completed: Math.random() < 0.8
    }
  };

  orderHistoricBatch.push(orderDoc);
  restaurantOrderCounter[restaurant._id.valueOf()] = (restaurantOrderCounter[restaurant._id.valueOf()] || 0) + 1;

  if (orderHistoricBatch.length === BATCH_SIZE) {
    database.orders_historic.insertMany(orderHistoricBatch);
    print(`  Órdenes históricas insertadas: ${i}`);
    orderHistoricBatch = [];
  }
}

if (orderHistoricBatch.length > 0) {
  database.orders_historic.insertMany(orderHistoricBatch);
}

// -----------------------------
// 5) ACTUALIZAR total_orders EN RESTAURANTS
// -----------------------------
print("Actualizando total_orders en restaurants...");

const bulkRestaurantUpdates = [];
for (const restaurant of restaurantData) {
  const extraOrders = restaurantOrderCounter[restaurant._id.valueOf()] || 0;

  bulkRestaurantUpdates.push({
    updateOne: {
      filter: { _id: restaurant._id },
      update: {
        $inc: { total_orders: extraOrders },
        $set: { updated_at: new Date() }
      }
    }
  });

  if (bulkRestaurantUpdates.length === BATCH_SIZE) {
    database.restaurants.bulkWrite(bulkRestaurantUpdates);
    bulkRestaurantUpdates.length = 0;
  }
}

if (bulkRestaurantUpdates.length > 0) {
  database.restaurants.bulkWrite(bulkRestaurantUpdates);
}

// -----------------------------
// 6) INDICES RECOMENDADOS
// -----------------------------
print("Creando índices...");

database.restaurants.createIndex({ name: 1 });
database.restaurants.createIndex({ location: "2dsphere" });
database.restaurants.createIndex({ type_of_food: 1 });
database.reviews.createIndex({ from_user: 1 });
database.reviews.createIndex({ for_restaurant: 1 });
database.orders_historic.createIndex({ from_user: 1 });
database.orders_historic.createIndex({ "order_data.for_restaurant": 1 });
database.users.createIndex({ username: 1 }, { unique: true });


