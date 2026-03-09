<script>
  export let page;
  const items = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'users', label: 'Users' },
    { id: 'restaurants', label: 'Restaurants' },
    { id: 'reviews', label: 'Reviews' },
    { id: 'orders', label: 'Orders' }
  ];
</script>

<aside class="bg-gray-800 text-white w-60 min-h-screen p-4 flex flex-col">
  <div class="text-2xl font-bold mb-8">Restaurant Admin</div>
  {#each items as item}
    <button
      class="mb-2 p-2 rounded hover:bg-gray-700 text-left w-full
             { $page === item.id ? 'bg-gray-700 font-semibold' : '' }"
      on:click={() => page.set(item.id)}
    >
      {item.label}
    </button>
  {/each}
</aside>
