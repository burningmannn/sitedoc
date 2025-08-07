// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
import Aura from '@primeuix/themes/aura';

export default defineNuxtConfig({
    ssr: false,
    $development: undefined, $env: undefined, $meta: undefined, $production: undefined, $test: undefined,
    compatibilityDate: '2025-05-16',
    devtools: {enabled: true},
    css: ['~/assets/css/main.css'],
    modules: ['@primevue/nuxt-module', '@pinia/nuxt'],
    vite: {
        plugins: [
            tailwindcss(),
        ],
    },
    runtimeConfig: {
        public: {
            apiBase: 'http://localhost:8000' // IP-backend. ip для сервера 192.168.2.4
        }
    },
    pinia: {
        storesDirs: ['./stores/**'],
    },
    primevue: {
        options: {
            theme: {
                preset: Aura,
                options: {
                    darkModeSelector: '.white',
                }
            }
        },
        components: {
            include: '*'
        }
    }
})