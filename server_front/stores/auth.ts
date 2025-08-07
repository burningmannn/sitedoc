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
        notificationIntervals: [] as NodeJS.Timeout[],
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
                
                // Если ошибка 401, перенаправляем на логин
                if (e?.status === 401 || e?.statusCode === 401) {
                    if (process.client && window.location.pathname !== '/login') {
                        await navigateTo('/login')
                    }
                }
            }
        },
        async logout() {
            const config = useRuntimeConfig()
            
            // Очищаем все интервалы уведомлений
            this.clearNotificationIntervals()
            
            // Очищаем уведомления
            const notificationStore = useNotificationStore()
            notificationStore.clearNotifications()
            
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
            // Также очищаем интервалы при очистке пользователя
            this.clearNotificationIntervals()
        },
        addNotificationInterval(intervalId: NodeJS.Timeout) {
            this.notificationIntervals.push(intervalId)
        },
        clearNotificationIntervals() {
            // Очищаем все активные интервалы
            this.notificationIntervals.forEach(intervalId => {
                clearInterval(intervalId)
            })
            this.notificationIntervals = []
        }
    },
    persist: true
})