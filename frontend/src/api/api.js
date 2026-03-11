const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const API_BASE_URL = API_BASE;

async function request(path, { method = "GET", body, headers = {}, ...rest } = {}) {
  const init = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    ...rest,
  };

  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;

  if (body !== undefined) {
    if (isFormData) {
      init.body = body;
    } else {
      init.body = typeof body === "string" ? body : JSON.stringify(body);
    }
  } else {
    delete init.headers["Content-Type"];
  }

  if (isFormData) {
    delete init.headers["Content-Type"];
  }

  const response = await fetch(`${API_BASE}${path}`, init);

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail ?? payload.message ?? message;
    } catch (error) {
      // ignore parse errors
    }
    throw new Error(message);
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

// HEALTH
export const ping = () => request("/ping");

// USERS
export const getUsers = () => request("/users/");
export const createUser = (data) => request("/users/", { method: "POST", body: data });
export const deleteUser = (id) => request(`/users/${id}`, { method: "DELETE" });
export const loginUser = (credentials) =>
  request("/users/login", { method: "POST", body: credentials });

// RESTAURANTS
export const getRestaurants = () => request("/restaurants/");
export const createRestaurant = (data) => request("/restaurants/", { method: "POST", body: data });
export const deleteRestaurant = (id) => request(`/restaurants/${id}`, { method: "DELETE" });

// REVIEWS
export const getReviews = () => request("/reviews/");
export const createReview = (data) => request("/reviews/", { method: "POST", body: data });
export const getRestaurantReviews = (restaurantId) => request(`/reviews/restaurant/${restaurantId}`);

// ORDERS
export const getUserOrders = (userId) => request(`/orders/user/${userId}`);
export const createOrder = (userId, restaurantId, data) =>
  request(`/orders/?user_id=${userId}&restaurant_id=${restaurantId}`, {
    method: "POST",
    body: data,
  });

// HISTORIC ORDERS
export const getHistoricOrders = () => request("/orders-historic/");

// FILES
export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return request("/files/upload", { method: "POST", body: formData });
};
