type User = {
    id: number
    name: string
    email: string
    role: boolean
}

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null as null | {
            id: number
            name: string
            email: string
            role: string
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
            } catch (e) {
                this.user = null
            } finally {
                this.isAuthLoaded = true
            }
        },
        async logout() {
            const config = useRuntimeConfig()
            try {
                await $fetch(`${config.public.apiBase}/api/auth/logout`, {
                    method: 'POST',
                    credentials: 'include'
                })
                this.user = null
                await navigateTo('/login')
            } catch (e) {
                console.error('Logout error', e)
            }
        }
    },
    persist: true
})