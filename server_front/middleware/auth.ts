// middleware/auth.global.ts
import {useAuthStore} from "~/stores/auth";
export default defineNuxtRouteMiddleware(async (to, from) => {
    const auth = useAuthStore()

    if (!auth.user) {
        await auth.checkAuth()
    }

    if (!auth.user) {
        return navigateTo('/error_page/403')
    }
})