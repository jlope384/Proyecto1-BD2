<script>
import { onMount } from "svelte";
import { writable } from "svelte/store";
import { getUsers, createUser, deleteUser,
         getRestaurants, createRestaurant,
         getReviews } from "./api/api";

let users = [];
let restaurants = [];
let reviews = [];

let newUser = "";
let newRestaurant = "";

const loading = writable(false);

async function loadAll() {
    loading.set(true);
    users = await getUsers();
    restaurants = await getRestaurants();
    reviews = await getReviews();
    loading.set(false);
}

async function addUser() {
    if(!newUser) return;
    await createUser({name: newUser});
    newUser = "";
    loadAll();
}

async function addRestaurant() {
    if(!newRestaurant) return;
    await createRestaurant({name: newRestaurant});
    newRestaurant = "";
    loadAll();
}

async function deleteUserById(id) {
    await deleteUser(id);
    loadAll();
}

onMount(loadAll);
</script>

<div class="min-h-screen p-6 bg-gray-100 font-sans">
  <h1 class="text-3xl font-bold mb-6">Restaurant Admin Dashboard</h1>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Users Block -->
    <div class="bg-white shadow rounded p-4 flex flex-col">
      <h2 class="font-bold text-lg mb-2">Users ({users.length})</h2>
      <div class="flex gap-2 mb-2">
        <input type="text" placeholder="New User" bind:value={newUser} class="border p-2 rounded flex-1"/>
        <button class="bg-blue-600 text-white px-3 rounded hover:bg-blue-700" on:click={addUser}>Add</button>
      </div>
      <ul class="flex-1 overflow-auto">
        {#each users as u}
          <li class="flex justify-between items-center p-1 border-b">
            {u.name}
            <button class="text-red-600 hover:underline" on:click={()=>deleteUserById(u._id)}>X</button>
          </li>
        {/each}
      </ul>
    </div>

    <!-- Restaurants Block -->
    <div class="bg-white shadow rounded p-4 flex flex-col">
      <h2 class="font-bold text-lg mb-2">Restaurants ({restaurants.length})</h2>
      <div class="flex gap-2 mb-2">
        <input type="text" placeholder="New Restaurant" bind:value={newRestaurant} class="border p-2 rounded flex-1"/>
        <button class="bg-green-600 text-white px-3 rounded hover:bg-green-700" on:click={addRestaurant}>Add</button>
      </div>
      <ul class="flex-1 overflow-auto">
        {#each restaurants as r}
          <li class="flex justify-between items-center p-1 border-b">
            {r.name}
          </li>
        {/each}
      </ul>
    </div>

    <!-- Reviews Block -->
    <div class="bg-white shadow rounded p-4 flex flex-col">
      <h2 class="font-bold text-lg mb-2">Reviews ({reviews.length})</h2>
      <ul class="flex-1 overflow-auto">
        {#each reviews as rev}
          <li class="border-b p-1">
            <span class="font-semibold">{rev.from_user}</span> → <span>{rev.for_restaurant}</span>
          </li>
        {/each}
      </ul>
    </div>

    <!-- Orders Block (placeholder) -->
    <div class="bg-white shadow rounded p-4 flex flex-col">
      <h2 class="font-bold text-lg mb-2">Orders</h2>
      <p class="text-gray-500">Orders module coming soon...</p>
    </div>
  </div>
</div>
