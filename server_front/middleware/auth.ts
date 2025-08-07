// middleware/auth.ts - НЕ глобальное middleware
import {useAuthStore} from "~/stores/auth";
export default defineNuxtRouteMiddleware(async (to, from) => {
    const auth = useAuthStore()

    if (!auth.user) {
        await auth.checkAuth()
    } else if (!auth.isAuthLoaded) {
        // Если пользователь есть, но токен еще не проверялся, проверяем его
        await auth.checkAuth()
    }

    if (!auth.user) {
        return navigateTo('/login')
    }
})