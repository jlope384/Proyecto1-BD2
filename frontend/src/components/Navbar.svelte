<script>
  export let page;
</script>

<nav class="bg-gray-900 text-white p-4 flex gap-4">
  <button on:click={() => page.set("dashboard")} class="hover:underline">Dashboard</button>
  <button on:click={() => page.set("users")} class="hover:underline">Users</button>
  <button on:click={() => page.set("restaurants")} class="hover:underline">Restaurants</button>
  <button on:click={() => page.set("reviews")} class="hover:underline">Reviews</button>
  <button on:click={() => page.set("orders")} class="hover:underline">Orders</button>
</nav>
