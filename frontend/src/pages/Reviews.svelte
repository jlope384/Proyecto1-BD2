<script>
import { onMount } from "svelte";
import { getReviews } from "../api/api";

let reviews = [];

onMount(async () => {
  reviews = await getReviews();
});
</script>

<h1 class="text-2xl font-bold mb-4">Reviews</h1>

<ul class="space-y-2">
  {#each reviews as r}
    <li class="border p-3 rounded bg-white shadow">
      User: {r.from_user} → Restaurant: {r.for_restaurant} <br/>
      Rating: {r.rating || 'N/A'} <br/>
      Comment: {r.comment || 'N/A'}
    </li>
  {/each}
</ul>
