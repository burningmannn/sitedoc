<script setup lang="js">
import {onMounted} from "vue";
import {useAuthStore} from "~/stores/auth.js";

const config = useRuntimeConfig()
const authStore = useAuthStore()

useHead({
  title: 'Главная - Документооборот',
  meta: [
    { name: 'description', content: 'Все файлы' }
  ]
})

// НЕ проверяем авторизацию автоматически на главной странице
onMounted(() => {
  // Главная страница доступна всем
})
</script>

<template>
  <div class="selection">
    <div class="w-full mx-auto px-20">
      <Table />
    </div>  
  </div>
  <div class="selection">
    <div class="max-w-7xl mx-auto">
    </div>
  </div>
</template>

<style scoped>

</style>