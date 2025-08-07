<script setup lang="ts">
import {onMounted, computed, ref} from 'vue'
import {useAuthStore} from '~/stores/auth'
import {useNotificationStore} from '~/stores/notification'

const notificationStore = useNotificationStore()
const authStore = useAuthStore()
const user = computed(() => authStore.user)
const visible = ref(false);

onMounted(() => {
  // Plugin уже проверил авторизацию при загрузке приложения
  // Уведомления загружаются только если пользователь авторизован
  if (user.value) {
    notificationStore.fetchNotifications()

    // Обновление уведомлений каждые 30 секунд
    const intervalId = setInterval(() => {
      notificationStore.fetchNotifications()
    }, 30000)
    
    // Сохраняем интервал в auth store для управления
    authStore.addNotificationInterval(intervalId)
  }
})


const getInitials = (fullName: string | null | undefined): string => {
  if (!fullName || typeof fullName !== 'string') return 'N';
  const parts = fullName.trim().split(' ');
  const initials = parts.map(p => p.charAt(0).toUpperCase()).join('');
  return initials || 'U';
};

const handleLogout = async () => {
  visible.value = false; // Закрываем drawer
  await authStore.logout();
};

</script>

<template>
  <header class="w-full bg-gray-100 sticky top-0 z-10">
    <div class="max-w-7xl mx-auto flex p-1.25 items-center justify-between gap-10">
      <NuxtLink to="/">
        <Button>
          Файлы
        </Button>
      </NuxtLink>
      <div class="flex gap-4 items-center">
        <NuxtLink v-if="user" to="/file/upload">
          <Button icon="pi pi-plus" label="Загрузить"/>
        </NuxtLink>
        <NuxtLink v-if="user" to="/notification">
          <OverlayBadge v-if="notificationStore.unreadCount > 0" severity="danger"
                        class="badge inline-flex cursor-pointer">
            <Button icon="pi pi-bell"/>
          </OverlayBadge>
          <Button v-else icon="pi pi-bell"/>
        </NuxtLink>
        <div class="flex-auto">
          <div v-if="user">
            <Avatar
                :label="getInitials(user.username)"
                size="large"
                class="cursor-pointer"
                @click="visible = true"
            />
            <Drawer class="flex-col gap-2" v-model:visible="visible" position="right" header="Меню">
              <div  class="p-4" v-if="user.admin == true">
                <i class="pi pi-pencil"></i>
                <NuxtLink class="ml-2" @click="visible = false" to="/admin_panel">Админ панель</NuxtLink>
              </div>
              <div class="p-4">
                <i class="pi pi-user"></i>
                <NuxtLink class="ml-2" @click="visible = false" to="/profile">Профиль</NuxtLink>
              </div>
              <div class="p-4">
                <i class="pi pi-file"></i>
                <NuxtLink class="ml-2" @click="visible = false" to="/file/my">Мои файлы</NuxtLink>
              </div>
              <div class="p-4">
                <i class="pi pi-arrow-down"></i>
                <NuxtLink class="ml-2" @click="visible = false" to="/file/working_files">Назначенные файлы</NuxtLink>
              </div>
              <div v-if="authStore.user" class="p-4 m-auto content-center">
                <Button  @click="handleLogout">Выйти</Button>
              </div>
            </Drawer>
          </div>
          <div v-else>
            <NuxtLink to="/login">
              <Button>Войти</Button>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>