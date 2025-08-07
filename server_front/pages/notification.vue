<script setup lang="ts">
import { onMounted } from 'vue'
import { useNotificationStore } from '~/stores/notification'
import { useAuthStore } from '~/stores/auth'
import Card from 'primevue/card'
import {useToast} from "primevue/usetoast";
definePageMeta({
  middleware: ["auth"],
})
const config = useRuntimeConfig()
const notificationStore = useNotificationStore()
const toast = useToast()

useHead({
  title: 'Уведомления - Документооборот',
  meta: [
    { name: 'description', content: 'Уведомления пользователя' }
  ]
})

onMounted(() => {
  notificationStore.fetchNotifications()
})

const markAsRead = async (id: number) => {
  try {
    await $fetch(`${config.public.apiBase}/api/notification/${id}/read`, {
      method: 'PATCH',
      credentials: 'include'
    })
    await notificationStore.fetchNotifications()
    toast.add({severity: 'success', summary: 'Уведомление прочитано', life: 3000})
  } catch (err) {
    toast.add({severity: 'error', summary: 'Ошибка', detail: err, life: 3000})
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto p-6">
    <h2 class="text-2xl font-bold mb-6">Уведомления</h2>

    <div v-if="notificationStore.notifications.length === 0">
      <p class="text-gray-500">Нет новых уведомлений.</p>
    </div>

    <div v-else class="space-y-4">
      <Card
          v-for="notification in notificationStore.notifications"
          :key="notification.id"
      >
        <template #title>
          <div class="flex justify-between items-center">
            <span>📄 Уведомление по файлу ID {{ notification.file_id }}</span>
            <span class="text-sm text-gray-400">{{ new Date(notification.created_at).toLocaleString() }}</span>
          </div>
        </template>
        <template #content>
          <p>{{ notification.message || 'Файл был обновлен или загружен' }}</p>

        </template>
        <template #footer>
          <NuxtLink :to="`http://localhost:3000/file/${notification.file_id}`">
            <Button class="mr-4" icon="pi pi-arrow-right" label="Перейти к файлу"/>
          </NuxtLink>
          <Button icon="pi pi-check" label="Прочитать" @click="markAsRead(notification.id)"/>
        </template>
      </Card>
    </div>
  </div>
</template>

