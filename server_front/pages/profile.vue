<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

import {onMounted, ref} from 'vue'
import { useNotificationStore } from '~/stores/notification'
import { useToast } from 'primevue/usetoast'

useHead({
  title: 'Профиль - Документооборот',
  meta: [
    { name: 'description', content: 'Информация о пользователе' }
  ]
})

const toast = useToast()
const config = useRuntimeConfig()

const notificationStore = useNotificationStore()
const userData = ref('')

const fetchData = async () => {
  try {
    userData.value = await $fetch(`${config.public.apiBase}/api/auth/user_info`, {
      credentials: 'include'
    })

    console.log(userData.value)
  } catch (error) {
    toast.add({severity: 'error', summary: 'Ошибка', detail: 'Не удалось получить информацию', life: 3000})
  }

}

onMounted(() => {
  // authStore.checkAuth()
  notificationStore.fetchNotifications()
  fetchData()

  setInterval(() => {
    notificationStore.fetchNotifications()
  }, 30000)
})
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <Card class="mb-6">
      <template #title>Профиль пользователя</template>
      <template #content>
        <div class="space-y-2">
          <p><strong>ID:</strong> {{ userData.id || 'Не указано' }}</p>
          <p><strong>Логин:</strong> {{ userData.username || 'Не указано' }}</p>
          <p><strong>ФИО:</strong> {{ userData.name || 'Не указано' }}</p>
          <p><strong>Служба:</strong> {{ userData.department?.name || 'Не указано' }}</p>
          <p><strong>Роль:</strong> {{ userData.admin ? 'Админ' : 'Пользователь' }}</p>
        </div>
      </template>
    </Card>

    <Card>
      <template #title>Уведомления</template>
      <template #content>
        <div v-if="notificationStore.notifications.length === 0">
          Нет новых уведомлений.
        </div>
        <ul v-else class="list-disc list-inside space-y-1">
          <li v-for="n in notificationStore.notifications" :key="n.id">
            {{ n.message }}
          </li>
        </ul>
      </template>
    </Card>
  </div>
</template>
