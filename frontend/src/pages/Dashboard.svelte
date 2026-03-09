<script>
  import Card from "../components/Card.svelte";
</script>

<h1 class="text-3xl font-bold mb-6">Dashboard</h1>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card title="Total Users">
    <p class="text-2xl font-bold">—</p>
  </Card>
  <Card title="Total Restaurants">
    <p class="text-2xl font-bold">—</p>
  </Card>
  <Card title="Pending Orders">
    <p class="text-2xl font-bold">—</p>
  </Card>
</div>
