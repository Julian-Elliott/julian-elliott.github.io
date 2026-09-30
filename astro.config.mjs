// @ts-check
import { defineConfig } from 'astro/config';

// Static site for GitHub Pages (user site: served at the root of julian-elliott.github.io).
export default defineConfig({
  site: 'https://julian-elliott.github.io',
  output: 'static',
  build: { format: 'directory' },
});
