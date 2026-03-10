import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('vite').UserConfig} */
export default {
  preprocess: vitePreprocess(),
  compilerOptions: {
    compatibility: { componentApi: 5 }
  }
};
