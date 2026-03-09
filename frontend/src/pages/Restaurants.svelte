<script>
import { onMount } from "svelte";
import { getRestaurants, createRestaurant } from "../api/api";

let restaurants = [];
let name = "";

async function load() {
  restaurants = await getRestaurants();
}

async function add() {
  if (!name) return;
  await createRestaurant({ name });
  name = "";
  load();
}

onMount(load);
</script>

<h1 class="text-2xl font-bold mb-4">Restaurants</h1>

<div class="flex gap-2 mb-4">
  <input bind:value={name} class="border p-2 rounded" placeholder="Restaurant Name"/>
  <button class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700" on:click={add}>
    Add
  </button>
</div>

<ul class="space-y-2">
  {#each restaurants as r}
    <li class="border p-3 rounded bg-white shadow">{r.name}</li>
  {/each}
</ul>
