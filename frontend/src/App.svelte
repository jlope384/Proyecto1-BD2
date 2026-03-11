<script>
  import { onMount } from "svelte";
  import {
    getUsers,
    createUser,
    deleteUser,
    getRestaurants,
    createRestaurant,
    deleteRestaurant,
    getReviews,
    getHistoricOrders,
    getUserOrders,
    createOrder,
  } from "./api/api";

  const blankMenuItem = () => ({ name: "", quantity: 1, price: "", note: "" });

  let dashboardLoading = true;
  let userOrdersLoading = false;
  let users = [];
  let restaurants = [];
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

  const orderStatuses = ["pending", "preparing", "delivered"];

  const statusStyles = {
    pending: "bg-yellow-500/15 text-yellow-200 border border-yellow-500/40",
    preparing: "bg-blue-500/15 text-blue-200 border border-blue-500/40",
    delivered: "bg-emerald-500/15 text-emerald-200 border border-emerald-500/40",
  };

  onMount(() => {
    loadDashboard();
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
  $: totalSpent = userOrders.reduce((sum, order) => sum + (order.total ?? 0), 0);
  $: historicSummary = historicOrders.slice(0, 5);
  $: stats = [
    { label: "Usuarios", value: users.length },
    { label: "Restaurantes", value: restaurants.length },
    { label: "Notas de clientes", value: reviewCards.length },
    { label: "Pedidos históricos", value: historicOrders.length },
  ];

  async function loadDashboard() {
    dashboardLoading = true;
    errorMessage = "";
    try {
      const [usersData, restaurantsData, reviewsData, historicData] = await Promise.all([
        getUsers(),
        getRestaurants(),
        getReviews(),
        getHistoricOrders(),
      ]);

      users = usersData ?? [];
      restaurants = restaurantsData ?? [];
      rawReviews = reviewsData ?? [];
      historicOrders = historicData ?? [];

      if (!selectedUserId && users.length) {
        selectedUserId = users[0]._id;
      } else if (selectedUserId && !users.find((u) => u._id === selectedUserId)) {
        selectedUserId = users[0]?._id ?? "";
      }

      if (!orderForm.userId && users.length) {
        orderForm.userId = users[0]._id;
      } else if (orderForm.userId && !users.find((u) => u._id === orderForm.userId)) {
        orderForm.userId = users[0]?._id ?? "";
      }

      if (!orderForm.restaurantId && restaurants.length) {
        orderForm.restaurantId = restaurants[0]._id;
      } else if (
        orderForm.restaurantId &&
        !restaurants.find((r) => r._id === orderForm.restaurantId)
      ) {
        orderForm.restaurantId = restaurants[0]?._id ?? "";
      }

      if (selectedUserId) {
        await loadUserOrders(selectedUserId);
      } else {
        userOrders = [];
      }
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

  function showNotification(type, message) {
    notification = { type, message };
    setTimeout(() => (notification = null), 4000);
  }

  async function handleCreateUser(event) {
    event?.preventDefault();
    if (!userForm.name.trim()) {
      showNotification("error", "Ingresa al menos un nombre de usuario.");
      return;
    }

    const payload = { name: userForm.name.trim() };
    if (userForm.username.trim()) payload.username = userForm.username.trim();
    if (userForm.password.trim())
      payload.hashed_password_with_user_sided_salt = userForm.password.trim();

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

  function selectUser(userId) {
    selectedUserId = userId;
    orderForm.userId = userId;
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

  function statusColor(status) {
    return statusStyles[status] ?? "bg-slate-800 text-slate-100 border border-slate-700";
  }
</script>

<div class="min-h-screen bg-[#040205] text-gray-100 pb-16">
  <header class="px-6 lg:px-12 py-8 border-b border-red-600/40 bg-gradient-to-r from-black via-[#13020c] to-black">
    <p class="text-sm uppercase tracking-[0.4em] text-red-400">Restaurant System</p>
    <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mt-4">
      <div>
        <h1 class="text-4xl font-semibold text-white">Panel Operacional</h1>
        <p class="text-gray-400 text-sm">Frontend conectado al backend de FastAPI + MongoDB</p>
      </div>
      <button
        class="self-start border border-red-500 text-sm uppercase tracking-widest text-red-200 px-4 py-2 rounded-full hover:bg-red-600/10"
        on:click={loadDashboard}
      >
        {dashboardLoading ? "Actualizando…" : "Refrescar datos"}
      </button>
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
        <article class="bg-[#0b0509] border border-red-800/40 rounded-2xl p-5 shadow-lg">
          <p class="text-xs uppercase tracking-widest text-red-300">{stat.label}</p>
          <p class="text-4xl font-semibold mt-2 text-white">{stat.value}</p>
        </article>
      {/each}
    </section>

    <section class="grid gap-6 lg:grid-cols-2">
      <article class="bg-[#09030a] border border-red-900/40 rounded-2xl p-6 flex flex-col gap-4">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-red-200">Usuarios</h2>
            <p class="text-xs text-gray-400">Crea cuentas y explora sus pedidos</p>
          </div>
        </header>
        <form class="grid gap-3" on:submit|preventDefault={handleCreateUser}>
          <input
            class="bg-black/50 border border-red-900/50 rounded-lg px-3 py-2 text-sm focus:border-red-500"
            placeholder="Nombre visible*"
            bind:value={userForm.name}
          />
          <input
            class="bg-black/50 border border-red-900/50 rounded-lg px-3 py-2 text-sm focus:border-red-500"
            placeholder="Usuario (opcional)"
            bind:value={userForm.username}
          />
          <input
            class="bg-black/50 border border-red-900/50 rounded-lg px-3 py-2 text-sm focus:border-red-500"
            placeholder="Contraseña simple (se guarda tal cual)"
            bind:value={userForm.password}
            type="password"
          />
          <button
            class="mt-2 bg-red-600/80 hover:bg-red-600 px-3 py-2 rounded-lg text-sm font-semibold"
            type="submit"
          >
            Crear usuario
          </button>
        </form>
        <div class="border-t border-red-900/40 pt-4">
          <p class="text-xs uppercase text-gray-400 mb-2">Listado</p>
          <ul class="space-y-2 max-h-64 overflow-y-auto pr-2 text-sm">
            {#if !users.length}
              <li class="text-gray-500">Sin usuarios registrados.</li>
            {/if}
            {#each users as user (user._id)}
              <li class="flex items-center justify-between gap-3 bg-black/40 border border-white/5 rounded-lg px-3 py-2">
                <div>
                  <p class="font-semibold">{user.name}</p>
                  <p class="text-[0.7rem] text-gray-400">
                    {user.username ?? "sin username"} · {user.orders?.length ?? 0} pedidos
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    class={`text-xs px-2 py-1 rounded-md border border-red-500/50 ${selectedUserId === user._id ? "bg-red-600/40" : "hover:bg-red-600/20"}`}
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
        </div>
      </article>

      <article class="bg-[#09030a] border border-red-900/40 rounded-2xl p-6 flex flex-col gap-4">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-red-200">Restaurantes</h2>
            <p class="text-xs text-gray-400">Registra nuevas cocinas y monitorea su actividad</p>
          </div>
        </header>
        <form class="grid gap-3" on:submit|preventDefault={handleCreateRestaurant}>
          <input
            class="bg-black/50 border border-red-900/50 rounded-lg px-3 py-2 text-sm focus:border-red-500"
            placeholder="Nombre comercial*"
            bind:value={restaurantForm.name}
          />
          <input
            class="bg-black/50 border border-red-900/50 rounded-lg px-3 py-2 text-sm focus:border-red-500"
            placeholder="Tipo de cocina"
            bind:value={restaurantForm.cuisine}
          />
          <input
            class="bg-black/50 border border-red-900/50 rounded-lg px-3 py-2 text-sm focus:border-red-500"
            placeholder="Ciudad"
            bind:value={restaurantForm.city}
          />
          <button
            class="mt-2 bg-red-600/80 hover:bg-red-600 px-3 py-2 rounded-lg text-sm font-semibold"
            type="submit"
          >
            Registrar restaurante
          </button>
        </form>
        <div class="border-t border-red-900/40 pt-4">
          <p class="text-xs uppercase text-gray-400 mb-2">Activos</p>
          <ul class="space-y-2 max-h-64 overflow-y-auto pr-2 text-sm">
            {#if !restaurants.length}
              <li class="text-gray-500">Sin restaurantes registrados.</li>
            {/if}
            {#each restaurants as restaurant (restaurant._id)}
              <li class="flex items-center justify-between gap-3 bg-black/40 border border-white/5 rounded-lg px-3 py-2">
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
        </div>
      </article>
    </section>

    <section class="grid gap-6 xl:grid-cols-[2fr_1fr]">
      <article class="bg-[#070207] border border-red-900/40 rounded-2xl p-6 space-y-4">
        <header class="flex items-start justify-between">
          <div>
            <h2 class="text-xl font-semibold text-red-200">Nueva orden</h2>
            <p class="text-xs text-gray-400">El pedido se guarda dentro del usuario y actualiza al restaurante</p>
          </div>
          <span class="text-xs text-gray-400">
            Total estimado: {formatCurrency(orderForm.menuItems.reduce((acc, item) => acc + (Number(item.price) || 0) * (Number(item.quantity) || 1), 0))}
          </span>
        </header>
        <form class="space-y-4" on:submit|preventDefault={handleCreateOrder}>
          <div class="grid md:grid-cols-3 gap-3">
            <select
              class="bg-black/40 border border-red-900/40 rounded-lg px-3 py-2 text-sm"
              bind:value={orderForm.userId}
            >
              <option value="" disabled>Usuario</option>
              {#each users as user}
                <option value={user._id}>{user.name}</option>
              {/each}
            </select>
            <select
              class="bg-black/40 border border-red-900/40 rounded-lg px-3 py-2 text-sm"
              bind:value={orderForm.restaurantId}
            >
              <option value="" disabled>Restaurante</option>
              {#each restaurants as restaurant}
                <option value={restaurant._id}>{restaurant.name}</option>
              {/each}
            </select>
            <select
              class="bg-black/40 border border-red-900/40 rounded-lg px-3 py-2 text-sm"
              bind:value={orderForm.status}
            >
              {#each orderStatuses as status}
                <option value={status}>{status}</option>
              {/each}
            </select>
          </div>

          <div class="space-y-3">
            {#each orderForm.menuItems as item, index}
              <div class="grid gap-3 md:grid-cols-[1.2fr,0.5fr,0.5fr,1fr,auto] bg-black/30 border border-white/5 rounded-xl px-3 py-3 items-center">
                <input
                  class="bg-transparent border border-white/10 rounded-lg px-3 py-2 text-sm"
                  placeholder="Platillo"
                  bind:value={item.name}
                  on:input={(event) => updateMenuItem(index, "name", event.target.value)}
                />
                <input
                  class="bg-transparent border border-white/10 rounded-lg px-3 py-2 text-sm"
                  type="number"
                  min="1"
                  placeholder="Cant"
                  bind:value={item.quantity}
                  on:input={(event) => updateMenuItem(index, "quantity", event.target.value)}
                />
                <input
                  class="bg-transparent border border-white/10 rounded-lg px-3 py-2 text-sm"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="Precio"
                  bind:value={item.price}
                  on:input={(event) => updateMenuItem(index, "price", event.target.value)}
                />
                <input
                  class="bg-transparent border border-white/10 rounded-lg px-3 py-2 text-sm"
                  placeholder="Nota"
                  bind:value={item.note}
                  on:input={(event) => updateMenuItem(index, "note", event.target.value)}
                />
                <button
                  class="text-red-300 text-sm"
                  type="button"
                  on:click={() => removeMenuItemRow(index)}
                >
                  ✕
                </button>
              </div>
            {/each}
            <button
              class="text-xs uppercase tracking-widest text-red-300 border border-dashed border-red-400/60 rounded-full px-3 py-1"
              type="button"
              on:click={addMenuItemRow}
            >
              Agregar platillo
            </button>
          </div>

          <textarea
            class="w-full bg-black/30 border border-white/5 rounded-xl px-3 py-3 text-sm"
            rows="3"
            placeholder="Notas generales del cliente"
            bind:value={orderForm.customerNote}
          ></textarea>

          <button
            class="w-full bg-red-600/80 hover:bg-red-600 transition py-3 rounded-xl font-semibold"
            type="submit"
          >
            Guardar orden
          </button>
        </form>
      </article>

      <article class="bg-[#070207] border border-red-900/40 rounded-2xl p-6 space-y-4">
        <header>
          <h2 class="text-xl font-semibold text-red-200">Histórico (últimos 5)</h2>
          <p class="text-xs text-gray-400">Colección orders_historic</p>
        </header>
        <ul class="space-y-3 text-sm max-h-[420px] overflow-y-auto pr-2">
          {#if !historicSummary.length}
            <li class="text-gray-500">Sin registros todavía.</li>
          {/if}
          {#each historicSummary as historic (historic._id)}
            <li class="p-3 bg-black/30 border border-white/5 rounded-xl">
              <p class="font-semibold text-white">
                {historic.user?.name ?? historic.user ?? "Usuario"}
                <span class="text-gray-400">→ {historic.restaurant?.name ?? historic.restaurant ?? "Restaurante"}</span>
              </p>
              <p class="text-xs text-gray-400 mt-1">
                {historic.status ?? "sin estado"} · {historic.total ? formatCurrency(historic.total) : "sin total"}
              </p>
              {#if historic.created_at}
                <p class="text-[0.65rem] text-gray-500">{formatDate(historic.created_at)}</p>
              {/if}
            </li>
          {/each}
        </ul>
      </article>
    </section>

    <section class="grid gap-6 lg:grid-cols-2">
      <article class="bg-[#060107] border border-red-900/40 rounded-2xl p-6">
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
          <p class="text-sm text-gray-500">Elige un usuario en la sección superior para cargar sus pedidos.</p>
        {:else if userOrdersLoading}
          <p class="text-sm text-gray-400">Cargando órdenes…</p>
        {:else if !userOrders.length}
          <p class="text-sm text-gray-500">El usuario no tiene pedidos registrados.</p>
        {:else}
          <ul class="space-y-3 max-h-[400px] overflow-y-auto pr-2">
            {#each userOrders as order, index}
              <li class="p-4 bg-black/30 border border-white/5 rounded-xl">
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

      <article class="bg-[#060107] border border-red-900/40 rounded-2xl p-6">
        <header class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-semibold text-red-200">Notas reales de clientes</h2>
            <p class="text-xs text-gray-400">Derivadas de los comentarios en pedidos</p>
          </div>
        </header>
        <ul class="space-y-3 max-h-[420px] overflow-y-auto pr-2 text-sm">
          {#if !reviewCards.length}
            <li class="text-gray-500">Aún no hay notas registradas en los pedidos.</li>
          {/if}
          {#each reviewCards as review}
            <li class="bg-black/30 border border-white/5 rounded-xl p-4">
              <p class="font-semibold text-white">{review.userName}</p>
              <p class="text-xs text-gray-400 mb-2">Para {review.restaurantName}</p>
              <p class="text-sm text-gray-200">{review.note}</p>
            </li>
          {/each}
        </ul>
      </article>
    </section>
  </main>
</div>
