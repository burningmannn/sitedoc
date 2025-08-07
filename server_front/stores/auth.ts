type User = {
    id: number
    name: string
    username: string
    admin: boolean
}

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null as null | {
            id: number
            name: string
            username: string
            admin: boolean
        },
        isAuthLoaded: false,
    }),
    actions: {
        setUser(userData: User) {
            this.user = userData
        },
        async checkAuth() {
            const config = useRuntimeConfig()
            try {
                this.user = await $fetch(`${config.public.apiBase}/api/auth/check_auth`, {
                    credentials: 'include'
                })
                this.isAuthLoaded = true
            } catch (e) {
                // Если проверка не удалась, очищаем состояние пользователя
                this.user = null
                this.isAuthLoaded = false
                console.log('Проверка авторизации не удалась, пользователь не авторизован')
            }
        },
        async logout() {
            const config = useRuntimeConfig()
            try {
                await $fetch(`${config.public.apiBase}/api/auth/logout`, {
                    method: 'POST',
                    credentials: 'include'
                })
            } catch (e) {
                console.error('Logout error:', e)
                // Даже если сервер вернул ошибку, очищаем локальное состояние
            } finally {
                // Всегда очищаем состояние пользователя
                this.user = null
                this.isAuthLoaded = false
                await navigateTo('/login')
            }
        },
        clearUser() {
            this.user = null
            this.isAuthLoaded = false
        }
    },
    persist: true
})