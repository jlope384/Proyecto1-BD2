<script>
  import { onMount } from "svelte";
  import {
    getUsers,
    createUser,
    deleteUser,
    getRestaurants,
    createRestaurant,
    deleteRestaurant,
    getTopRestaurants,
    searchRestaurants,
    getReviews,
    getHistoricOrders,
    getUserOrders,
    createOrder,
    loginUser,
    createReview,
    getRestaurantReviews,
    uploadFile,
    ping,
    API_BASE_URL,
  } from "./api/api";

  const SESSION_KEY = "restaurant_session";
  const blankMenuItem = () => ({ name: "", quantity: 1, price: "", note: "" });

  let session = null;
  let dashboardLoading = false;
  let userOrdersLoading = false;
  let users = [];
  let restaurants = [];
  let topRestaurants = [];
  let rawReviews = [];
  let historicOrders = [];
  let userOrders = [];
  let selectedUserId = "";
  let notification = null;
  let errorMessage = "";

  let userForm = { name: "", username: "", password: "" };
  let restaurantForm = { name: "", cuisine: "", city: "" };
  let orderForm = {
    userId: "",
    restaurantId: "",
    status: "pending",
    menuItems: [blankMenuItem()],
    customerNote: "",
  };

  let loginForm = { username: "", password: "" };
  let loginLoading = false;
  let loginError = "";
  let backendStatus = { checked: false, ok: false, message: "" };
  let reviewForm = { restaurantId: "", userId: "", rating: 5, comment: "" };
  let restaurantReviews = [];
  let restaurantReviewsLoading = false;
  let uploadState = { file: null };
  let uploadLoading = false;
  let uploadedFiles = [];
  let fileInputEl;
  let restaurantSearchForm = { term: "", minOrders: "", minRating: "" };
  let restaurantSearchResults = [];
  let restaurantSearchLoading = false;
  let restaurantSearchExecuted = false;
  let restaurantSearchError = "";

  const orderStatuses = ["pending", "preparing", "delivered"];
  const statusStyles = {
    pending: "bg-yellow-500/15 text-yellow-200 border border-yellow-500/40",
    preparing: "bg-blue-500/15 text-blue-200 border border-blue-500/40",
    delivered: "bg-emerald-500/15 text-emerald-200 border border-emerald-500/40",
  };

  onMount(() => {
    verifyBackend();
    if (typeof localStorage === "undefined") return;
    const stored = localStorage.getItem(SESSION_KEY);
    if (stored) {
      try {
        session = JSON.parse(stored);
        loadDashboard();
      } catch (error) {
        session = null;
      }
    }
  });

  $: usersById = Object.fromEntries(users.map((user) => [user._id, user]));
  $: restaurantsById = Object.fromEntries(restaurants.map((r) => [r._id, r]));
  $: reviewCards = rawReviews.map((review, index) => ({
    id: `${review.user_id}-${review.restaurant_id}-${index}`,
    userName: usersById[review.user_id]?.name ?? "Cliente",
    restaurantName: restaurantsById[review.restaurant_id]?.name ?? "Restaurante",
    note: review.note ?? "Sin comentarios",
  }));
  $: selectedUser = usersById[selectedUserId];
  $: selectedRestaurant = restaurantsById[reviewForm.restaurantId];
  $: reviewFeed = restaurantReviews.map((review, index) => ({
    id: review._id ?? `${review.for_restaurant}-${index}`,
    userName: usersById[review.from_user]?.name ?? "Cliente",
    rating: review.rating ?? "–",
    comment: review.comment ?? review.note ?? "Sin comentarios",
    created_at: review.created_at,
  }));
  $: totalSpent = userOrders.reduce((sum, order) => sum + (order.total ?? 0), 0);
  $: uniqueCities = Array.from(
    new Set(
      restaurants
        .map((restaurant) => restaurant.city?.trim().toLowerCase())
        .filter(Boolean)
    )
  ).length;
  $: highestTicket = historicOrders.reduce(
    (max, order) => Math.max(max, order.total ?? 0),
    0
  );
  $: stats = [
    { label: "Usuarios activos", value: users.length },
    { label: "Restaurantes", value: restaurants.length },
    { label: "Ciudades", value: uniqueCities },
    { label: "Ticket máximo", value: highestTicket ? formatCurrency(highestTicket) : "—" },
  ];
  $: timelineFeed = historicOrders
    .map((order) => ({
      id: order._id,
      user: order.user?.name ?? order.user ?? "Usuario",
      restaurant: order.restaurant?.name ?? order.restaurant ?? "Restaurante",
      created_at: order.created_at,
      status: order.status ?? "pending",
      total: order.total ?? 0,
    }))
    .sort((a, b) => new Date(b.created_at ?? 0) - new Date(a.created_at ?? 0))
    .slice(0, 6);
  $: menuDiversity = new Set(
    userOrders.flatMap((order) =>
      order.menu_items?.map((item) => item.menu_item ?? item.name ?? "").filter(Boolean) ?? []
    )
  ).size;

  async function loadDashboard() {
    if (!session) return;
    verifyBackend();
    dashboardLoading = true;
    errorMessage = "";
    try {
      const [usersData, restaurantsData, reviewsData, historicData, topRankedData] = await Promise.all([
        getUsers(),
        getRestaurants(),
        getReviews(),
        getHistoricOrders(),
        getTopRestaurants(4),
      ]);

      users = usersData ?? [];
      restaurants = restaurantsData ?? [];
      rawReviews = reviewsData ?? [];
      historicOrders = historicData ?? [];
      topRestaurants = (topRankedData ?? []).map((restaurant) => ({
        id: restaurant._id ?? restaurant.id,
        name: restaurant.name,
        cuisine: restaurant.cuisine ?? "General",
        city: restaurant.city ?? "Ciudad",
        total: restaurant.total_orders ?? restaurant.total ?? 0,
      }));

      const preferredUser = users.find((user) => user._id === session?.userId);
      if (preferredUser) {
        selectedUserId = preferredUser._id;
      } else if (users.length) {
        selectedUserId = users[0]._id;
      } else {
        selectedUserId = "";
      }

      if (selectedUserId) {
        orderForm.userId = selectedUserId;
      } else if (users.length) {
        orderForm.userId = users[0]._id;
      } else {
        orderForm.userId = "";
      }

      if (!reviewForm.userId) {
        reviewForm.userId = selectedUserId || users[0]?._id || "";
      } else if (!users.find((user) => user._id === reviewForm.userId)) {
        reviewForm.userId = users[0]?._id || "";
      }

      if (!orderForm.restaurantId && restaurants.length) {
        orderForm.restaurantId = restaurants[0]._id;
      } else if (
        orderForm.restaurantId &&
        !restaurants.find((restaurant) => restaurant._id === orderForm.restaurantId)
      ) {
        orderForm.restaurantId = restaurants[0]?._id ?? "";
      }

      if (!reviewForm.restaurantId) {
        reviewForm.restaurantId = restaurants[0]?._id ?? "";
      } else if (
        reviewForm.restaurantId &&
        !restaurants.find((restaurant) => restaurant._id === reviewForm.restaurantId)
      ) {
        reviewForm.restaurantId = restaurants[0]?._id ?? "";
      }

      if (selectedUserId) {
        await loadUserOrders(selectedUserId);
      } else {
        userOrders = [];
      }

      await loadRestaurantReviews(reviewForm.restaurantId);
    } catch (error) {
      errorMessage = error.message ?? "No se pudo conectar con el backend.";
    } finally {
      dashboardLoading = false;
    }
  }

  async function loadUserOrders(userId) {
    if (!userId) {
      userOrders = [];
      return;
    }
    userOrdersLoading = true;
    try {
      const data = await getUserOrders(userId);
      userOrders = data.orders ?? [];
    } catch (error) {
      userOrders = [];
      showNotification("error", "No se pudieron cargar las órdenes del usuario.");
    } finally {
      userOrdersLoading = false;
    }
  }

  async function loadRestaurantReviews(restaurantId) {
    if (!restaurantId) {
      restaurantReviews = [];
      return;
    }
    restaurantReviewsLoading = true;
    try {
      const data = await getRestaurantReviews(restaurantId);
      restaurantReviews = Array.isArray(data) ? data : [];
    } catch (error) {
      restaurantReviews = [];
      showNotification("error", "No se pudieron cargar las reseñas del restaurante.");
    } finally {
      restaurantReviewsLoading = false;
    }
  }

  function persistSession(data) {
    if (typeof localStorage === "undefined") return;
    if (!data) {
      localStorage.removeItem(SESSION_KEY);
      return;
    }
    localStorage.setItem(SESSION_KEY, JSON.stringify(data));
  }

  async function handleLogin(event) {
    event?.preventDefault();
    loginError = "";
    const usernameValue = loginForm.username.trim();
    const passwordValue = loginForm.password.trim();

    if (!usernameValue || !passwordValue) {
      loginError = "Ingresa usuario y contraseña.";
      return;
    }

    loginLoading = true;

    try {
      let guardMessage = "";
      try {
        const directory = await getUsers();
        if (Array.isArray(directory)) {
          const normalized = usernameValue.toLowerCase();
          const candidate = directory.find(
            (user) => (user.username ?? "").toLowerCase() === normalized
          );
          if (!candidate) {
            guardMessage = "Ese usuario no existe. Crea una cuenta desde el panel.";
          } else if (!candidate.hashed_password_with_user_sided_salt) {
            guardMessage =
              "El usuario no tiene contraseña configurada. Elíminalo y créalo nuevamente con contraseña.";
          }
        }
      } catch (directoryError) {
        console.warn("No se pudo validar el usuario antes del login", directoryError);
      }

      if (guardMessage) {
        loginError = guardMessage;
        loginLoading = false;
        return;
      }

      const payload = {
        username: usernameValue,
        password: passwordValue,
      };
      const response = await loginUser(payload);
      session = { userId: response.user_id, username: payload.username };
      persistSession(session);
      loginForm = { username: "", password: "" };
      await loadDashboard();
      showNotification("success", "Bienvenido de vuelta.");
    } catch (error) {
      loginError = error.message ?? "Credenciales inválidas.";
    } finally {
      loginLoading = false;
    }
  }

  function logout() {
    session = null;
    persistSession(null);
    users = [];
    restaurants = [];
    rawReviews = [];
    historicOrders = [];
    userOrders = [];
    selectedUserId = "";
    userForm = { name: "", username: "", password: "" };
    restaurantForm = { name: "", cuisine: "", city: "" };
    orderForm = {
      userId: "",
      restaurantId: "",
      status: "pending",
      menuItems: [blankMenuItem()],
      customerNote: "",
    };
    reviewForm = { restaurantId: "", userId: "", rating: 5, comment: "" };
    restaurantReviews = [];
    uploadState = { file: null };
    uploadedFiles = [];
    if (fileInputEl) {
      fileInputEl.value = "";
    }
    restaurantSearchForm = { term: "", minOrders: "", minRating: "" };
    restaurantSearchResults = [];
    restaurantSearchLoading = false;
    restaurantSearchExecuted = false;
    restaurantSearchError = "";
    errorMessage = "";
  }

  function showNotification(type, message) {
    notification = { type, message };
    setTimeout(() => (notification = null), 4000);
  }

  async function verifyBackend() {
    backendStatus = { checked: true, ok: false, message: "Verificando backend…" };
    try {
      await ping();
      backendStatus = { checked: true, ok: true, message: "API en línea" };
    } catch (error) {
      backendStatus = {
        checked: true,
        ok: false,
        message: error.message ?? "No se pudo conectar con el backend.",
      };
    }
  }

  async function handleCreateUser(event) {
    event?.preventDefault();
    if (!userForm.name.trim()) {
      showNotification("error", "Ingresa al menos un nombre visible.");
      return;
    }
    if (!userForm.username.trim()) {
      showNotification("error", "Define el usuario que se usará en el login.");
      return;
    }
    if (!userForm.password.trim()) {
      showNotification("error", "Configura una contraseña para poder iniciar sesión.");
      return;
    }

    const payload = {
      name: userForm.name.trim(),
      username: userForm.username.trim(),
      hashed_password_with_user_sided_salt: userForm.password.trim(),
    };

    try {
      await createUser(payload);
      userForm = { name: "", username: "", password: "" };
      showNotification("success", "Usuario creado correctamente.");
      await loadDashboard();
    } catch (error) {
      showNotification("error", error.message ?? "No se pudo crear el usuario.");
    }
  }

  async function handleDeleteUser(userId) {
    const confirmed = confirm("¿Seguro que deseas eliminar este usuario?");
    if (!confirmed) return;
    try {
      await deleteUser(userId);
      if (selectedUserId === userId) {
        selectedUserId = "";
        orderForm.userId = "";
      }
      showNotification("success", "Usuario eliminado.");
      await loadDashboard();
    } catch (error) {
      showNotification("error", error.message ?? "No se pudo eliminar el usuario.");
    }
  }

  async function handleCreateRestaurant(event) {
    event?.preventDefault();
    if (!restaurantForm.name.trim()) {
      showNotification("error", "Ingresa el nombre del restaurante.");
      return;
    }

    const payload = { name: restaurantForm.name.trim() };
    if (restaurantForm.cuisine.trim()) payload.cuisine = restaurantForm.cuisine.trim();
    if (restaurantForm.city.trim()) payload.city = restaurantForm.city.trim();

    try {
      await createRestaurant(payload);
      restaurantForm = { name: "", cuisine: "", city: "" };
      showNotification("success", "Restaurante registrado.");
      await loadDashboard();
    } catch (error) {
      showNotification(
        "error",
        error.message ?? "No se pudo registrar el restaurante."
      );
    }
  }

  async function handleDeleteRestaurant(id) {
    const confirmed = confirm("¿Eliminar restaurante?");
    if (!confirmed) return;
    try {
      await deleteRestaurant(id);
      if (orderForm.restaurantId === id) {
        orderForm.restaurantId = "";
      }
      showNotification("success", "Restaurante eliminado.");
      await loadDashboard();
    } catch (error) {
      showNotification("error", error.message ?? "No se pudo eliminar el restaurante.");
    }
  }

  async function handleRestaurantSearch(event) {
    event?.preventDefault();
    restaurantSearchExecuted = true;
    restaurantSearchLoading = true;
    restaurantSearchError = "";
    try {
      const params = {
        term: restaurantSearchForm.term.trim(),
        minOrders: Number(restaurantSearchForm.minOrders) || 0,
        minRating: Number(restaurantSearchForm.minRating) || 0,
        limit: 6,
      };
      const results = await searchRestaurants(params);
      restaurantSearchResults = (results ?? []).map((restaurant) => ({
        id: restaurant._id ?? restaurant.id,
        name: restaurant.name,
        cuisine: restaurant.cuisine ?? "General",
        city: restaurant.city ?? "Ciudad",
        total_orders: restaurant.total_orders ?? 0,
        avg_rating: restaurant.avg_rating ?? null,
        rating_count: restaurant.rating_count ?? restaurant.review_count ?? 0,
      }));
    } catch (error) {
      restaurantSearchError = error.message ?? "No se pudo ejecutar la búsqueda.";
      restaurantSearchResults = [];
    } finally {
      restaurantSearchLoading = false;
    }
  }

  function selectUser(userId) {
    selectedUserId = userId;
    orderForm.userId = userId;
    reviewForm.userId = userId;
    loadUserOrders(userId);
  }

  function addMenuItemRow() {
    orderForm.menuItems = [...orderForm.menuItems, blankMenuItem()];
  }

  function removeMenuItemRow(index) {
    if (orderForm.menuItems.length === 1) return;
    orderForm.menuItems = orderForm.menuItems.filter((_, i) => i !== index);
  }

  function updateMenuItem(index, key, value) {
    orderForm.menuItems = orderForm.menuItems.map((item, i) =>
      i === index ? { ...item, [key]: value } : item
    );
  }

  async function handleCreateOrder(event) {
    event?.preventDefault();
    if (!orderForm.userId || !orderForm.restaurantId) {
      showNotification("error", "Selecciona un usuario y un restaurante.");
      return;
    }

    const items = orderForm.menuItems
      .filter((item) => item.name.trim())
      .map((item) => ({
        menu_item: item.name.trim(),
        quantity: Number(item.quantity) || 1,
        price: Number(item.price) || 0,
        menu_note: item.note?.trim(),
      }));

    if (!items.length) {
      showNotification("error", "Agrega al menos un platillo.");
      return;
    }

    const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    const payload = {
      status: orderForm.status,
      note: orderForm.customerNote?.trim(),
      menu_items: items,
      total,
    };

    try {
      await createOrder(orderForm.userId, orderForm.restaurantId, payload);
      showNotification("success", "Orden creada correctamente.");
      orderForm.customerNote = "";
      orderForm.menuItems = [blankMenuItem()];
      orderForm.status = "pending";
      selectedUserId = orderForm.userId;
      await loadDashboard();
    } catch (error) {
      showNotification("error", error.message ?? "No se pudo crear la orden.");
    }
  }

  async function handleCreateReview(event) {
    event?.preventDefault();
    if (!reviewForm.userId || !reviewForm.restaurantId) {
      showNotification("error", "Selecciona usuario y restaurante para la reseña.");
      return;
    }

    if (!reviewForm.comment.trim()) {
      showNotification("error", "Escribe algún comentario para la reseña.");
      return;
    }

    const payload = {
      from_user: reviewForm.userId,
      for_restaurant: reviewForm.restaurantId,
      comment: reviewForm.comment.trim(),
    };

    const ratingValue = Number(reviewForm.rating);
    if (!Number.isNaN(ratingValue) && ratingValue > 0) {
      payload.rating = ratingValue;
    }

    try {
      await createReview(payload);
      showNotification("success", "Reseña registrada correctamente.");
      reviewForm.comment = "";
      await loadRestaurantReviews(reviewForm.restaurantId);
    } catch (error) {
      showNotification("error", error.message ?? "No se pudo guardar la reseña.");
    }
  }

  function handleFileSelection(event) {
    uploadState.file = event?.target?.files?.[0] ?? null;
  }

  async function handleUploadMedia(event) {
    event?.preventDefault();
    if (!uploadState.file) {
      showNotification("error", "Selecciona un archivo antes de subir.");
      return;
    }

    uploadLoading = true;
    try {
      const response = await uploadFile(uploadState.file);
      const descriptor = {
        id: response.file_id,
        name: uploadState.file.name,
        url: `${API_BASE_URL}/files/${response.file_id}`,
      };
      uploadedFiles = [descriptor, ...uploadedFiles].slice(0, 6);
      uploadState.file = null;
      if (fileInputEl) {
        fileInputEl.value = "";
      }
      showNotification("success", "Imagen subida correctamente.");
    } catch (error) {
      showNotification("error", error.message ?? "No se pudo subir el archivo.");
    } finally {
      uploadLoading = false;
    }
  }

  function formatDate(value) {
    if (!value) return "Sin fecha";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
  }

  function formatCurrency(amount) {
    return new Intl.NumberFormat("es-GT", {
      style: "currency",
      currency: "GTQ",
    }).format(amount ?? 0);
  }

  function formatRating(value) {
    if (value === null || value === undefined) return "—";
    const numeric = Number(value);
    if (Number.isNaN(numeric)) return "—";
    return numeric.toFixed(1);
  }

  function statusColor(status) {
    return statusStyles[status] ?? "bg-slate-800 text-slate-100 border border-slate-700";
  }
</script>

{#if !session}
  <div class="login-shell min-h-screen text-gray-100 relative overflow-hidden">
    <div class="login-orb orb-one"></div>
    <div class="login-orb orb-two"></div>
    <div class="login-grid">
      <section class="login-panel">
        <p class="text-xs uppercase tracking-[0.45em] text-red-300">Restaurant System</p>
        <h1 class="text-4xl font-semibold text-white mt-4">Autenticación</h1>
        <p class="text-sm text-gray-400 mt-2">
          Conecta con el backend de FastAPI para administrar usuarios, restaurantes y órdenes en vivo.
        </p>
        <form class="mt-8 space-y-4" on:submit|preventDefault={handleLogin}>
          <label class="flex flex-col gap-2 text-sm">
            <span class="text-gray-400">Usuario</span>
            <input
              class="bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:border-red-400"
              placeholder="admin"
              bind:value={loginForm.username}
            />
          </label>
          <label class="flex flex-col gap-2 text-sm">
            <span class="text-gray-400">Contraseña</span>
            <input
              class="bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:border-red-400"
              type="password"
              placeholder="••••••"
              bind:value={loginForm.password}
            />
          </label>
          {#if loginError}
            <p class="text-xs text-red-300">{loginError}</p>
          {/if}
          <button
            class="w-full bg-gradient-to-r from-red-500 via-pink-500 to-orange-400 py-3 rounded-2xl font-semibold tracking-wide hover:opacity-90"
            type="submit"
          >
            {loginLoading ? "Entrando..." : "Entrar al panel"}
          </button>
        </form>
        <div class="status-pill mt-6">
          <span class={`status-dot ${backendStatus.ok ? "bg-emerald-400" : "bg-red-400"}`}></span>
          <p class="text-xs text-gray-400">
            {backendStatus.message || "Sin verificar conexión"}
          </p>
          <button class="chip" on:click={verifyBackend} type="button">Reintentar</button>
        </div>
      </section>
      <section class="login-hero">
        <div class="login-hero-card">
          <p class="text-xs uppercase tracking-[0.4em] text-red-200">Mongo Observability</p>
          <h2 class="text-3xl font-semibold text-white mt-4">Monitorea cada pedido</h2>
          <p class="text-sm text-pink-100/80 mt-3">
            KPIs en vivo, notas reales de clientes y creación de órdenes sin salir del panel.
          </p>
          <ul class="mt-6 space-y-3 text-sm text-pink-50/80">
            <li class="flex items-center gap-3"><span class="dot"></span>Dashboard en tiempo real</li>
            <li class="flex items-center gap-3"><span class="dot"></span>Sincronizado con FastAPI</li>
            <li class="flex items-center gap-3"><span class="dot"></span>Diseño oscuro cinematográfico</li>
          </ul>
        </div>
      </section>
    </div>
  </div>
{:else}
  <div class="min-h-screen bg-[#030105] text-gray-100 pb-16">
    <header class="px-6 lg:px-12 py-8 border-b border-red-600/40 bg-gradient-to-r from-black via-[#16010b] to-black relative overflow-hidden">
      <div class="header-glow"></div>
      <p class="text-sm uppercase tracking-[0.4em] text-red-400">Restaurant System</p>
      <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mt-4 relative">
        <div>
          <h1 class="text-4xl font-semibold text-white">Panel Operacional</h1>
          <p class="text-gray-400 text-sm">Frontend mejorado conectado a FastAPI + MongoDB</p>
        </div>
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <div class="bg-white/5 border border-white/10 rounded-full px-4 py-2 text-xs uppercase tracking-[0.3em]">
            {session.username}
          </div>
          <div class="flex gap-2">
            <button
              class="border border-red-500 text-sm uppercase tracking-widest text-red-200 px-4 py-2 rounded-full hover:bg-red-600/10"
              on:click={loadDashboard}
              type="button"
            >
              {dashboardLoading ? "Actualizando…" : "Refrescar"}
            </button>
            <button
              class="border border-white/20 text-sm uppercase tracking-widest text-gray-200 px-4 py-2 rounded-full hover:bg-white/10"
              on:click={logout}
              type="button"
            >
              Salir
            </button>
          </div>
          <div class="status-pill">
            <span class={`status-dot ${backendStatus.ok ? "bg-emerald-400" : "bg-red-400"}`}></span>
            <p class="text-[0.65rem] text-gray-400 tracking-[0.2em] uppercase">
              {backendStatus.message || "Sin verificar"}
            </p>
            <button class="chip" type="button" on:click={verifyBackend}>Ping</button>
          </div>
        </div>
      </div>
    </header>

    {#if notification}
      <div
        class={`${notification.type === "error" ? "bg-red-700/80" : "bg-emerald-600/80"} fixed top-4 right-4 px-4 py-2 rounded-lg shadow-xl text-sm z-50`}
      >
        {notification.message}
      </div>
    {/if}

    {#if errorMessage}
      <div class="mx-6 lg:mx-12 mt-6 bg-red-900/60 border border-red-600/60 p-4 rounded-lg text-sm">
        {errorMessage}
      </div>
    {/if}

    <main class="px-6 lg:px-12 space-y-8 mt-8">
      <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {#each stats as stat}
          <article class="bg-[#0b0509] border border-red-800/40 rounded-2xl p-5 shadow-lg relative overflow-hidden">
            <div class="card-glow"></div>
            <p class="text-xs uppercase tracking-widest text-red-300">{stat.label}</p>
            <p class="text-4xl font-semibold mt-2 text-white">{stat.value}</p>
          </article>
        {/each}
      </section>

      <section class="grid gap-6 lg:grid-cols-2">
        <article class="glass-card">
          <header class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Usuarios</h2>
              <p class="text-xs text-gray-400">Crea cuentas y explora sus pedidos</p>
            </div>
          </header>
          <form class="grid gap-3" on:submit|preventDefault={handleCreateUser}>
            <input
              class="field"
              placeholder="Nombre visible*"
              bind:value={userForm.name}
            />
            <input
              class="field"
              placeholder="Usuario para login*"
              bind:value={userForm.username}
            />
            <input
              class="field"
              placeholder="Contraseña (se guarda tal cual)*"
              bind:value={userForm.password}
              type="password"
            />
            <button class="btn-primary" type="submit">Crear usuario</button>
          </form>
          <div class="divider"></div>
          <p class="text-xs uppercase text-gray-400 mb-2">Listado</p>
          <ul class="space-y-2 max-h-64 overflow-y-auto pr-2 text-sm">
            {#if !users.length}
              <li class="text-gray-500">Sin usuarios registrados.</li>
            {/if}
            {#each users as user (user._id)}
              <li class="list-row">
                <div>
                  <p class="font-semibold">{user.name}</p>
                  <p class="text-[0.7rem] text-gray-400">
                    {user.username ?? "sin username"} · {user.orders?.length ?? 0} pedidos
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    class={`chip ${selectedUserId === user._id ? "chip-active" : ""}`}
                    type="button"
                    on:click={() => selectUser(user._id)}
                  >
                    Órdenes
                  </button>
                  <button
                    class="text-xs text-red-300 hover:text-red-100"
                    type="button"
                    on:click={() => handleDeleteUser(user._id)}
                  >
                    ✕
                  </button>
                </div>
              </li>
            {/each}
          </ul>
        </article>

        <article class="glass-card">
          <header class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Restaurantes</h2>
              <p class="text-xs text-gray-400">Registra nuevas cocinas y monitorea su actividad</p>
            </div>
          </header>
          <form class="grid gap-3" on:submit|preventDefault={handleCreateRestaurant}>
            <input class="field" placeholder="Nombre comercial*" bind:value={restaurantForm.name} />
            <input class="field" placeholder="Tipo de cocina" bind:value={restaurantForm.cuisine} />
            <input class="field" placeholder="Ciudad" bind:value={restaurantForm.city} />
            <button class="btn-primary" type="submit">Registrar restaurante</button>
          </form>
          <div class="divider"></div>
          <p class="text-xs uppercase text-gray-400 mb-2">Activos</p>
          <ul class="space-y-2 max-h-64 overflow-y-auto pr-2 text-sm">
            {#if !restaurants.length}
              <li class="text-gray-500">Sin restaurantes registrados.</li>
            {/if}
            {#each restaurants as restaurant (restaurant._id)}
              <li class="list-row">
                <div>
                  <p class="font-semibold">{restaurant.name}</p>
                  <p class="text-[0.7rem] text-gray-400">
                    {restaurant.cuisine ?? "General"} · {restaurant.total_orders ?? 0} órdenes
                  </p>
                </div>
                <button
                  class="text-xs text-red-300 hover:text-red-100"
                  type="button"
                  on:click={() => handleDeleteRestaurant(restaurant._id)}
                >
                  ✕
                </button>
              </li>
            {/each}
          </ul>
        </article>
      </section>

      <section>
        <article class="glass-card space-y-4">
          <header class="flex items-start justify-between">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Búsqueda avanzada</h2>
              <p class="text-xs text-gray-400">Consulta restaurantes por texto, órdenes y rating</p>
            </div>
            <button class="chip" type="button" on:click={handleRestaurantSearch}>
              {restaurantSearchLoading ? "Buscando…" : "Buscar"}
            </button>
          </header>
          <form class="grid gap-3 md:grid-cols-3" on:submit|preventDefault={handleRestaurantSearch}>
            <input
              class="field md:col-span-3"
              placeholder="Nombre, ciudad, cocina o platillo"
              bind:value={restaurantSearchForm.term}
            />
            <input
              class="field"
              type="number"
              min="0"
              placeholder="Órdenes mínimas"
              bind:value={restaurantSearchForm.minOrders}
            />
            <input
              class="field"
              type="number"
              min="0"
              max="5"
              step="0.1"
              placeholder="Rating mínimo"
              bind:value={restaurantSearchForm.minRating}
            />
            <button class="btn-primary" type="submit" disabled={restaurantSearchLoading}>
              {restaurantSearchLoading ? "Buscando…" : "Aplicar filtros"}
            </button>
          </form>
          {#if restaurantSearchError}
            <p class="text-xs text-red-300">{restaurantSearchError}</p>
          {/if}
          <div class="divider"></div>
          <p class="text-xs uppercase text-gray-400">Resultados</p>
          {#if restaurantSearchLoading}
            <p class="text-sm text-gray-400">Ejecutando búsqueda…</p>
          {:else if !restaurantSearchExecuted}
            <p class="text-sm text-gray-500">Define filtros y presiona buscar.</p>
          {:else if !restaurantSearchResults.length}
            <p class="text-sm text-gray-500">No encontramos restaurantes con esos criterios.</p>
          {:else}
            <ul class="space-y-3 max-h-72 overflow-y-auto pr-2 text-sm">
              {#each restaurantSearchResults as restaurant (restaurant.id)}
                <li class="list-row">
                  <div>
                    <p class="font-semibold">{restaurant.name}</p>
                    <p class="text-[0.7rem] text-gray-400">
                      {restaurant.cuisine} · {restaurant.city}
                    </p>
                  </div>
                  <div class="text-right text-xs text-gray-300">
                    <p>{restaurant.total_orders ?? 0} órdenes</p>
                    <p>{formatRating(restaurant.avg_rating)} ★ ({restaurant.rating_count ?? 0})</p>
                  </div>
                </li>
              {/each}
            </ul>
          {/if}
        </article>
      </section>

      <section class="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <article class="glass-card space-y-4">
          <header class="flex items-start justify-between">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Nueva orden</h2>
              <p class="text-xs text-gray-400">Guarda en el usuario y actualiza el restaurante</p>
            </div>
            <span class="text-xs text-gray-400">
              Total estimado:
              {formatCurrency(
                orderForm.menuItems.reduce(
                  (acc, item) => acc + (Number(item.price) || 0) * (Number(item.quantity) || 1),
                  0
                )
              )}
            </span>
          </header>
          <form class="space-y-4" on:submit|preventDefault={handleCreateOrder}>
            <div class="grid md:grid-cols-3 gap-3">
              <select class="field" bind:value={orderForm.userId}>
                <option value="" disabled>Usuario</option>
                {#each users as user}
                  <option value={user._id}>{user.name}</option>
                {/each}
              </select>
              <select class="field" bind:value={orderForm.restaurantId}>
                <option value="" disabled>Restaurante</option>
                {#each restaurants as restaurant}
                  <option value={restaurant._id}>{restaurant.name}</option>
                {/each}
              </select>
              <select class="field" bind:value={orderForm.status}>
                {#each orderStatuses as status}
                  <option value={status}>{status}</option>
                {/each}
              </select>
            </div>

            <div class="space-y-3">
              {#each orderForm.menuItems as item, index}
                <div class="menu-row">
                  <input
                    class="field"
                    placeholder="Platillo"
                    value={item.name}
                    on:input={(event) => updateMenuItem(index, "name", event.target.value)}
                  />
                  <input
                    class="field"
                    type="number"
                    min="1"
                    placeholder="Cant"
                    value={item.quantity}
                    on:input={(event) => updateMenuItem(index, "quantity", event.target.value)}
                  />
                  <input
                    class="field"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Precio"
                    value={item.price}
                    on:input={(event) => updateMenuItem(index, "price", event.target.value)}
                  />
                  <input
                    class="field"
                    placeholder="Nota"
                    value={item.note}
                    on:input={(event) => updateMenuItem(index, "note", event.target.value)}
                  />
                  <button class="text-red-300 text-sm" type="button" on:click={() => removeMenuItemRow(index)}>
                    ✕
                  </button>
                </div>
              {/each}
              <button class="chip" type="button" on:click={addMenuItemRow}>Agregar platillo</button>
            </div>

            <textarea
              class="field"
              rows="3"
              placeholder="Notas generales del cliente"
              bind:value={orderForm.customerNote}
            ></textarea>

            <button class="btn-primary w-full" type="submit">Guardar orden</button>
          </form>
        </article>

        <article class="glass-card space-y-4">
          <header>
            <h2 class="text-xl font-semibold text-red-200">Actividad global</h2>
            <p class="text-xs text-gray-400">Colección orders_historic (últimos 6)</p>
          </header>
          <ul class="space-y-3 text-sm max-h-[420px] overflow-y-auto pr-2">
            {#if !timelineFeed.length}
              <li class="text-gray-500">Sin registros todavía.</li>
            {/if}
            {#each timelineFeed as historic (historic.id)}
              <li class="timeline-row">
                <div class="flex items-center justify-between">
                  <p class="font-semibold text-white">
                    {historic.user}
                    <span class="text-gray-400">→ {historic.restaurant}</span>
                  </p>
                  <span class={`px-2 py-1 rounded-full text-[0.65rem] ${statusColor(historic.status)}`}>
                    {historic.status}
                  </span>
                </div>
                <p class="text-xs text-gray-400 mt-1 flex justify-between">
                  <span>{formatDate(historic.created_at)}</span>
                  <span>{historic.total ? formatCurrency(historic.total) : ""}</span>
                </p>
              </li>
            {/each}
          </ul>
        </article>
      </section>

      <section class="grid gap-6 lg:grid-cols-2">
        <article class="glass-card">
          <header class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Órdenes del usuario</h2>
              <p class="text-xs text-gray-400">{selectedUser ? selectedUser.name : "Selecciona un usuario"}</p>
            </div>
            <div class="text-right text-xs text-gray-400">
              <p>{userOrders.length} órdenes</p>
              <p>Total: {formatCurrency(totalSpent)}</p>
            </div>
          </header>
          {#if !selectedUserId}
            <p class="text-sm text-gray-500">Elige un usuario para cargar sus pedidos.</p>
          {:else if userOrdersLoading}
            <p class="text-sm text-gray-400">Cargando órdenes…</p>
          {:else if !userOrders.length}
            <p class="text-sm text-gray-500">El usuario no tiene pedidos registrados.</p>
          {:else}
            <ul class="space-y-3 max-h-[400px] overflow-y-auto pr-2">
              {#each userOrders as order, index}
                <li class="timeline-row">
                  <div class="flex items-center justify-between text-sm">
                    <span class={`px-2 py-1 rounded-full text-xs ${statusColor(order.status)}`}>
                      {order.status ?? "pending"}
                    </span>
                    <span class="text-xs text-gray-400">{formatDate(order.created_at)}</span>
                  </div>
                  {#if order.menu_items?.length}
                    <ul class="mt-3 space-y-1 text-sm text-gray-300">
                      {#each order.menu_items as item}
                        <li class="flex justify-between">
                          <span>{item.menu_item ?? item.name ?? "Platillo"} × {item.quantity ?? 1}</span>
                          <span>{item.price ? formatCurrency(item.price) : ""}</span>
                        </li>
                      {/each}
                    </ul>
                  {/if}
                  {#if order.note}
                    <p class="text-xs text-gray-400 mt-2">Nota: {order.note}</p>
                  {/if}
                  {#if order.total}
                    <p class="text-xs text-red-200 font-semibold mt-2">Total orden: {formatCurrency(order.total)}</p>
                  {/if}
                </li>
              {/each}
            </ul>
          {/if}
        </article>

        <article class="glass-card">
          <header class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Notas reales de clientes</h2>
              <p class="text-xs text-gray-400">Derivadas de los comentarios en pedidos</p>
            </div>
          </header>
          <ul class="space-y-3 max-h-[420px] overflow-y-auto pr-2 text-sm">
            {#if !reviewCards.length}
              <li class="text-gray-500">Aún no hay notas registradas.</li>
            {/if}
            {#each reviewCards as review}
              <li class="review-card">
                <p class="font-semibold text-white">{review.userName}</p>
                <p class="text-xs text-gray-400 mb-2">Para {review.restaurantName}</p>
                <p class="text-sm text-gray-200">{review.note}</p>
              </li>
            {/each}
          </ul>
        </article>
      </section>

      <section class="grid gap-6 lg:grid-cols-2">
        <article class="glass-card space-y-4">
          <header class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Galería rápida</h2>
              <p class="text-xs text-gray-400">Sube imágenes directo a FastAPI + GridFS</p>
            </div>
            <span class="text-xs text-gray-500">Máx. 6 recientes</span>
          </header>
          <form class="space-y-3" on:submit|preventDefault={handleUploadMedia}>
            <input
              class="field"
              type="file"
              accept="image/*"
              on:change={handleFileSelection}
              bind:this={fileInputEl}
            />
            <button class="btn-primary" type="submit" disabled={uploadLoading}>
              {uploadLoading ? "Subiendo…" : "Subir imagen"}
            </button>
          </form>
          <div class="divider"></div>
          <p class="text-xs uppercase text-gray-400">Últimas cargas (solo sesión actual)</p>
          {#if !uploadedFiles.length}
            <p class="text-sm text-gray-500">Aún no has subido archivos.</p>
          {:else}
            <div class="media-grid">
              {#each uploadedFiles as file (file.id)}
                <div class="media-thumb">
                  <img src={file.url} alt={file.name} loading="lazy" />
                  <div class="media-caption">
                    <p>{file.name}</p>
                    <a href={file.url} target="_blank" rel="noreferrer">Ver</a>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </article>

        <article class="glass-card space-y-4">
          <header class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Reseñas verificadas</h2>
              <p class="text-xs text-gray-400">Solicita comentario y rating</p>
            </div>
            {#if selectedRestaurant}
              <span class="text-xs text-gray-500">{selectedRestaurant.name}</span>
            {/if}
          </header>
          <form class="space-y-3" on:submit|preventDefault={handleCreateReview}>
            <select class="field" bind:value={reviewForm.userId}>
              <option value="" disabled>Usuario que comenta</option>
              {#each users as user}
                <option value={user._id}>{user.name}</option>
              {/each}
            </select>
            <select
              class="field"
              bind:value={reviewForm.restaurantId}
              on:change={() => loadRestaurantReviews(reviewForm.restaurantId)}
            >
              <option value="" disabled>Restaurante</option>
              {#each restaurants as restaurant}
                <option value={restaurant._id}>{restaurant.name}</option>
              {/each}
            </select>
            <div class="grid grid-cols-2 gap-3">
              <input
                class="field"
                type="number"
                min="1"
                max="5"
                step="1"
                placeholder="Rating (1-5)"
                bind:value={reviewForm.rating}
              />
              <button
                class="chip"
                type="button"
                on:click={() => loadRestaurantReviews(reviewForm.restaurantId)}
              >
                Recargar reseñas
              </button>
            </div>
            <textarea
              class="field"
              rows="3"
              placeholder="Comentario del comensal"
              bind:value={reviewForm.comment}
            ></textarea>
            <button class="btn-primary w-full" type="submit">Guardar reseña</button>
          </form>
          <div class="divider"></div>
          <p class="text-xs uppercase text-gray-400">Reseñas recientes</p>
          {#if restaurantReviewsLoading}
            <p class="text-sm text-gray-400">Cargando reseñas…</p>
          {:else if !reviewFeed.length}
            <p class="text-sm text-gray-500">Aún no hay reseñas para este restaurante.</p>
          {:else}
            <ul class="space-y-3 max-h-[360px] overflow-y-auto pr-2">
              {#each reviewFeed as review}
                <li class="review-card">
                  <div class="flex items-center justify-between text-sm">
                    <p class="font-semibold text-white">{review.userName}</p>
                    <span class="chip">{review.rating ?? "—"} ★</span>
                  </div>
                  <p class="text-sm text-gray-200 mt-2">{review.comment}</p>
                  <p class="text-[0.7rem] text-gray-500 mt-1">{formatDate(review.created_at)}</p>
                </li>
              {/each}
            </ul>
          {/if}
        </article>
      </section>

      <section class="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
        <article class="glass-card">
          <header class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-red-200">Insights de restaurantes</h2>
              <p class="text-xs text-gray-400">Ranking por órdenes totales</p>
            </div>
          </header>
          <ul class="mt-4 space-y-4">
            {#if !topRestaurants.length}
              <li class="text-gray-500">Agrega restaurantes para ver tendencias.</li>
            {/if}
            {#each topRestaurants as restaurant, index}
              <li>
                <div class="flex items-center justify-between text-sm">
                  <div>
                    <p class="text-white font-semibold">#{index + 1} {restaurant.name}</p>
                    <p class="text-xs text-gray-400">{restaurant.cuisine} · {restaurant.city}</p>
                  </div>
                  <span class="text-xs text-red-200">{restaurant.total} órdenes</span>
                </div>
                <div class="h-2 bg-white/5 rounded-full mt-2 overflow-hidden">
                  <div
                    class={`h-full rounded-full insight-bar`}
                    style={`width: ${restaurant.total ? Math.min(100, restaurant.total * 5) : 6}%`}
                  ></div>
                </div>
              </li>
            {/each}
          </ul>
        </article>

        <article class="glass-card space-y-4">
          <header>
            <h2 class="text-xl font-semibold text-red-200">Pulso del menú</h2>
            <p class="text-xs text-gray-400">Diversidad y cobertura</p>
          </header>
          <div class="pulse-grid">
            <div>
              <p class="text-3xl font-semibold text-white">{menuDiversity}</p>
              <p class="text-xs text-gray-400">Platillos únicos en pedidos recientes</p>
            </div>
            <div>
              <p class="text-3xl font-semibold text-white">{uniqueCities}</p>
              <p class="text-xs text-gray-400">Ciudades con presencia activa</p>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="chip chip-active">Pedidos recurrentes</span>
            <span class="chip">Cobertura multi-ciudad</span>
            <span class="chip">Notas positivas</span>
          </div>
        </article>
      </section>
    </main>
  </div>
{/if}