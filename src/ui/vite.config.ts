import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
 
export default defineConfig(async () => {
  // dynamically import the ESM-only plugin
  const { default: tsconfigPaths } = await import('vite-tsconfig-paths');
 
  return {
    base: "/",
    define: {
      'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL)
    },
    plugins: [
      react(),
      tsconfigPaths(),
    ],
    resolve: {
      // ...your aliases (if any)...
    },
    server: {
      historyApiFallback: true,
      port: 3000,
      proxy: { '/api': 'http://localhost:5000' },
    },
    css: {
      preprocessorOptions: {
        scss: {
          //additionalData: `@use "src/styles/variables.scss" as *;`
        }
      }
    }
  };
});