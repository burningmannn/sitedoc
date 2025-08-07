import {defineStore} from 'pinia'

export const useNotificationStore = defineStore('notification', {
    state: () => ({
        notifications: []
    }),

    getters: {
        unreadCount: (state) => {
            return state.notifications.filter(n => !n.is_read).length
        }
    },

    actions: {
        async fetchNotifications() {
            // Проверяем авторизацию перед запросом
            const authStore = useAuthStore()
            if (!authStore.user) {
                // Пользователь не авторизован, очищаем уведомления
                this.notifications = []
                return
            }

            const config = useRuntimeConfig()
            try {
                this.notifications = await $fetch(`${config.public.apiBase}/api/notification/`, {
                    credentials: 'include'
                })
            } catch (err) {
                // Если получили 401, очищаем уведомления и не выводим ошибку в консоль
                if (err.status === 401 || err.statusCode === 401) {
                    this.notifications = []
                    // Очищаем состояние пользователя в auth store
                    authStore.clearUser()
                    
                    // Перенаправляем на логин, если не на странице логина
                    if (process.client && window.location.pathname !== '/login') {
                        await navigateTo('/login')
                    }
                } else {
                    console.error('Ошибка при загрузке уведомлений:', err)
                }
            }
        },

        clearNotifications() {
            this.notifications = []
        }
    }
})
