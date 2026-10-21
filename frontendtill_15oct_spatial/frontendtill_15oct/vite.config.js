// // /** Vite configuration.
// //  * Edit this file when changing the local development server or build settings.
// //  */
// // import { defineConfig } from 'vite';
// // import react from '@vitejs/plugin-react';
// // export default defineConfig({ plugins: [react()] });





// // import { defineConfig } from 'vite';
// // import react from '@vitejs/plugin-react';

// // /**
// //  * Vite configuration.
// //  * Host: allows access from other devices on the same network.
// //  */
// // export default defineConfig({
// //   plugins: [react()],
// //   server: {
// //     host: '0.0.0.0',
// //     port: 5173,
// //   }
// // });






// import { defineConfig } from 'vite';
// import react from '@vitejs/plugin-react';
// import basicSsl from '@vitejs/plugin-basic-ssl';

// /**
//  * Vite configuration with React and basic SSL support.
//  * Host: allows access from other devices on the same network.
//  */
// export default defineConfig({
//   plugins: [react(), basicSsl()],
//   server: {
//     host: '0.0.0.0',
//     port: 5173,
//   },
// });











// // import { defineConfig } from 'vite';
// // import react from '@vitejs/plugin-react';
// // import basicSsl from '@vitejs/plugin-basic-ssl';

// // export default defineConfig({
// //   plugins: [react(), basicSsl()],
// //   server: {
// //     host: '0.0.0.0',
// //     port: 5173,
// //     https: true,
// //     proxy: {
// //       '/medlife': {
// //         target: 'http://localhost:8000',
// //         changeOrigin: true,
// //         secure: false
// //       }
// //     }
// //   }
// // });






// // import { defineConfig } from 'vite';
// // import react from '@vitejs/plugin-react';
// // import { readFileSync } from 'node:fs';

// // export default defineConfig({
// //   plugins: [react()],
// //   server: {
// //     host: '0.0.0.0',
// //     port: 5173,
// //     https: {
// //       key: readFileSync('./certs/dev-key.pem'),
// //       cert: readFileSync('./certs/dev-cert.pem'),
// //     },
// //     proxy: {
// //       '/medlife': {
// //         target: 'http://127.0.0.1:8000',
// //         changeOrigin: true,
// //       },
// //     },
// //   },
// // });





import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/medlife': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});