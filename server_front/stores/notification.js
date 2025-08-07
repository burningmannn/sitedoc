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
            const config = useRuntimeConfig()
            try {
                this.notifications = await $fetch(`${config.public.apiBase}/api/notification/`, {
                    credentials: 'include'
                })
            } catch (err) {
                console.error('Ошибка при загрузке уведомлений:', err)
            }
        }
    }
})
