export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  
  // При загрузке приложения проверяем, есть ли сохраненный пользователь
  if (authStore.user && !authStore.isAuthLoaded) {
    try {
      // Проверяем, действителен ли токен
      await authStore.checkAuth()
    } catch (e) {
      // Если токен недействителен, очищаем состояние
      console.log('Токен недействителен при загрузке приложения, очищаем состояние пользователя')
      authStore.clearUser()
      
      // Если мы не на странице логина, перенаправляем туда
      if (process.client && window.location.pathname !== '/login') {
        await navigateTo('/login')
      }
    }
  }
})
