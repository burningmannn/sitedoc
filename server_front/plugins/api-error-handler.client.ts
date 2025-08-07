export default defineNuxtPlugin(() => {
  const authStore = useAuthStore()
  
  // Слушаем все необработанные ошибки fetch
  if (process.client) {
    // Перехватываем глобальные ошибки для автоматического разлогинивания
    window.addEventListener('unhandledrejection', (event) => {
      const error = event.reason
      
      // Проверяем, является ли это ошибкой 401 от нашего API
      if (error?.response?.status === 401 || error?.status === 401 || error?.statusCode === 401) {
        console.log('Обнаружена ошибка 401 - токен недействителен, выполняется разлогинивание')
        
        // Очищаем состояние пользователя
        authStore.clearUser()
        
        // Перенаправляем на страницу входа, если не на ней
        if (window.location.pathname !== '/login') {
          navigateTo('/login')
        }
        
        // Предотвращаем вывод ошибки в консоль
        event.preventDefault()
      }
    })
  }
})
