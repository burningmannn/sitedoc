import {defineStore} from 'pinia'

const config = useRuntimeConfig()

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
