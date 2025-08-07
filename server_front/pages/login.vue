<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'
const config = useRuntimeConfig()

const credentials = reactive({
  username: '',
  password: '',
})

useHead({
  title: 'Вход - Документооборот',
  meta: [
    { name: 'description', content: 'Вход в ЛК' }
  ]
})

const toast = useToast()
const authStore = useAuthStore()
const user = useState('user', () => null)

async function login() {
  try {
    const response = await $fetch(`${config.public.apiBase}/api/auth/signin`, {
      method: 'POST',
      body: credentials,
      credentials: 'include'
    })

    if (!response) throw new Error('No user returned')

    authStore.setUser(response) // ✅ Обновляем глобальный user
    toast.add({
      severity: 'success',
      summary: 'Успешный вход',
      detail: `Добро пожаловать, ${response.username || 'пользователь'}!`,
      life: 3000,
    })
    await navigateTo('/')
  } catch (error) {
    console.error(error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка входа',
      detail: error?.data?.message || 'Неверное имя пользователя или пароль',
      life: 4000,
    })
  }
}

onMounted(() => {
  // Страница входа не требует проверки авторизации
})
</script>

<template>
  <div>
    <form @submit.prevent="login" class="flex flex-col gap-4 max-w-sm mx-auto mt-10">
      <input v-model="credentials.username" type="text" placeholder="Логин" class="border p-2 rounded" />
      <input v-model="credentials.password" type="password" placeholder="Пароль" class="border p-2 rounded" />
      <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Войти</button>
    </form>
  </div>
</template>
