const API = "http://0.0.0.0:8000";

// USERS
export async function getUsers() {
  const res = await fetch(`${API}/users/`);
  return res.json();
}
export async function createUser(data) {
  const res = await fetch(`${API}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}
export async function deleteUser(id) {
  return fetch(`${API}/users/${id}`, { method: "DELETE" });
}

export async function getRestaurants() {
  const res = await fetch(`${API}/restaurants/`);
  return res.json();
}
export async function createRestaurant(data) {
  const res = await fetch(`${API}/restaurants/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}

// REVIEWS
export async function getReviews() {
  const res = await fetch(`${API}/reviews/`);
  return res.json();
}
export async function createReview(data) {
  const res = await fetch(`${API}/reviews/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}

// ORDERS
export async function getOrders() {
  const res = await fetch(`${API}/orders/`);
  return res.json();
}

export async function getHistoricOrders() {
  const res = await fetch(`${API}/orders-historic/`);
  return res.json();
}

export async function createOrder(data) {
  const res = await fetch(`${API}/orders/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}
