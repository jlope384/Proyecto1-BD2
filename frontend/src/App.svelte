<script>
  import { onMount } from "svelte";
  import { writable } from "svelte/store";
  import {
    getUsers,
    createUser,
    deleteUser,
    getRestaurants,
    createRestaurant,
    getReviews,
    getOrders,
    getHistoricOrders,
  } from "./api/api";
  let users = [];
  let restaurants = [];
  let reviews = [];
  let orders = [];
  let historicOrders = [];
  let newUser = "";
  let newRestaurant = "";
  const loading = writable(false);
  async function loadAll() {
    loading.set(true);
    users = await getUsers();
    restaurants = await getRestaurants();
    reviews = await getReviews();
    orders = await getOrders();
    historicOrders = await getHistoricOrders();
    loading.set(false);
  }
  async function addUser() {
    if (!newUser) return;
    await createUser({ name: newUser });
    newUser = "";
    loadAll();
  }
  async function addRestaurant() {
    if (!newRestaurant) return;
    await createRestaurant({ name: newRestaurant });
    newRestaurant = "";
    loadAll();
  }
  async function deleteUserById(id) {
    await deleteUser(id);
    loadAll();
  }
  function statusColor(status) {
    if (!status) return "bg-yellow-200 text-yellow-900";
    if (status === "preparing") return "bg-blue-200 text-blue-900";
    if (status === "delivered") return "bg-green-200 text-green-900";
    return "bg-gray-200 text-gray-800";
  }
  onMount(() => {
    loadAll();
    console.log(restaurants);
  });

  $effect(() => {
    loadAll();
  });
</script>

<div class="min-h-screen bg-[#0d0a0a] text-gray-200 p-8">
  <div class="mb-10 border-b border-red-700 pb-4">
    <h1 class="text-4xl font-bold text-red-400">Crud Restaurants</h1>
    <p class="text-red-300 text-sm">Admin Control Panel</p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
    <div class="border border-red-700 bg-black p-6 rounded-xl">
      <p class="text-red-400 text-xs uppercase">Users</p>
      <p class="text-3xl font-bold">{users.length}</p>
    </div>
    <div class="border border-red-700 bg-black p-6 rounded-xl">
      <p class="text-red-400 text-xs uppercase">Restaurants</p>
      <p class="text-3xl font-bold">{restaurants.length}</p>
    </div>
    <div class="border border-red-700 bg-black p-6 rounded-xl">
      <p class="text-red-400 text-xs uppercase">Reviews</p>
      <p class="text-3xl font-bold">{reviews.length}</p>
    </div>
    <div class="border border-red-700 bg-black p-6 rounded-xl">
      <p class="text-red-400 text-xs uppercase">Orders</p>
      <p class="text-3xl font-bold">{orders.length}</p>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
    <div class="border border-red-700 bg-[#0a0a0a] rounded-xl overflow-hidden">
      <div
        class="flex justify-between items-center bg-red-700 px-3 py-1 text-sm font-bold rounded-t-xl"
      >
        <span>Users.exe</span> <span class="space-x-2">— □ ✕</span>
      </div>
      <div class="p-4">
        <div class="flex gap-2 mb-4">
          <input
            bind:value={newUser}
            placeholder="New user"
            class="bg-black border border-red-700 p-2 w-full text-sm rounded-md"
          />
          <button
            on:click={addUser}
            class="bg-red-700 px-4 text-sm hover:bg-red-600 rounded-md"
          >
            Add
          </button>
        </div>
        <ul class="space-y-2 max-h-56 overflow-auto text-sm">
          {#each users as u}
            <li class="flex justify-between border-b border-red-800 pb-1">
              {u.name}
              <button
                class="text-red-400 hover:text-red-300"
                on:click={() => deleteUserById(u._id)}
              >
                delete
              </button>
            </li>
          {/each}
        </ul>
      </div>
    </div>

    <div class="border border-red-700 bg-[#0a0a0a] rounded-xl overflow-hidden">
      <div
        class="flex justify-between items-center bg-red-700 px-3 py-1 text-sm font-bold rounded-t-xl"
      >
        <span>Restaurants.exe</span> <span>— □ ✕</span>
      </div>
      <div class="p-4">
        <div class="flex gap-2 mb-4">
          <input
            bind:value={newRestaurant}
            placeholder="New restaurant"
            class="bg-black border border-red-700 p-2 w-full text-sm rounded-md"
          />
          <button
            on:click={addRestaurant}
            class="bg-red-700 px-4 text-sm hover:bg-red-600 rounded-md"
          >
            Add
          </button>
        </div>
        <ul class="space-y-2 max-h-56 overflow-auto text-sm">
          {#each restaurants as r}
            <li class="border-b border-red-800 pb-1">{r.name}</li>
          {/each}
        </ul>
      </div>
    </div>

    <div class="border border-red-700 bg-[#0a0a0a] rounded-xl overflow-hidden">
      <div
        class="flex justify-between items-center bg-red-700 px-3 py-1 text-sm font-bold rounded-t-xl"
      >
        <span>Reviews.exe</span> <span>— □ ✕</span>
      </div>
      <div class="p-4 max-h-64 overflow-auto text-sm">
        {#each reviews as rev}
          <div class="border-b border-red-800 pb-2 mb-2">
            <p class="font-semibold text-red-300">
              {rev.from_user} → {rev.for_restaurant}
            </p>
            <p class="text-xs text-gray-400">Rating: {rev.rating || "N/A"}</p>
            <p class="text-xs">{rev.comment || ""}</p>
          </div>
        {/each}
      </div>
    </div>

    <div class="border border-red-700 bg-[#0a0a0a] rounded-xl overflow-hidden">
      <div
        class="flex justify-between items-center bg-red-700 px-3 py-1 text-sm font-bold rounded-t-xl"
      >
        <span>Orders.exe</span> <span>— □ ✕</span>
      </div>
      <div class="p-4">
        <ul class="space-y-2 max-h-40 overflow-auto text-sm mb-6">
          {#each orders as o}
            <li class="flex justify-between border-b border-red-800 pb-1">
              <span> {o.user} → {o.restaurant} </span>
              <span
                class="text-xs px-2 py-1 rounded-md {statusColor(o.status)}"
              >
                {o.status || "pending"}
              </span>
            </li>
          {/each}
        </ul>
        <h3 class="text-red-400 text-xs uppercase mb-2">Historic Orders</h3>
        <ul class="space-y-1 text-xs max-h-32 overflow-auto">
          {#each historicOrders as o}
            <li class="text-gray-400">{o.user} → {o.restaurant}</li>
          {/each}
        </ul>
      </div>
    </div>
  </div>
</div>
