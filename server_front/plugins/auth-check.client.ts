export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  
  // При загрузке приложения проверяем, есть ли сохраненный пользователь
  if (authStore.user && !authStore.isAuthLoaded) {
    try {
      // Проверяем, действителен ли токен
      await authStore.checkAuth()
    } catch (e) {
      // Если токен недействителен, очищаем состояние
      console.log('Токен недействителен, очищаем состояние пользователя')
      authStore.clearUser()
    }
  }
})
