<script>
import { onMount } from 'svelte';
import { writable } from 'svelte/store';
import { getUsers, createUser, deleteUser } from '../api/api';
import Loading from '../components/Loading.svelte';

let users = [];
let name = '';
const loading = writable(false);

async function load() {
  loading.set(true);
  users = await getUsers();
  loading.set(false);
}

async function add() {
  if(!name) return;
  await createUser({name});
  name = '';
  load();
}

async function remove(id){
  await deleteUser(id);
  load();
}

onMount(load);
</script>

<h1 class="text-3xl font-bold mb-4">Users</h1>

<div class="flex gap-2 mb-4">
  <input bind:value={name} placeholder="Name" class="border rounded p-2 flex-1"/>
  <button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" on:click={add}>Add User</button>
</div>

{#if $loading}
  <Loading />
{:else}
<table class="min-w-full bg-white shadow rounded">
  <thead class="bg-gray-200">
    <tr>
      <th class="p-2 text-left">Name</th>
      <th class="p-2 text-left">Actions</th>
    </tr>
  </thead>
  <tbody>
    {#each users as u}
      <tr class="border-b">
        <td class="p-2">{u.name}</td>
        <td class="p-2">
          <button class="text-red-600 hover:underline" on:click={()=>remove(u._id)}>Delete</button>
        </td>
      </tr>
    {/each}
  </tbody>
</table>
{/if}
