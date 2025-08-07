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

async function check() {
  try {
    const res = await $fetch(`${config.public.apiBase}/api/auth/check_auth`, {
      credentials: 'include'
    })
    user.value = res
  } catch {
    user.value = null
  }
}

console.log(authStore.user)

onMounted(() => {

})
</script>

<template>
  <div class="selection">
    <div class="w-full mx-auto px-20">
      <Table />
      <TestTable />
    </div>  
  </div>
  <div class="selection">
    <div class="max-w-7xl mx-auto">
    </div>
  </div>
</template>

<style scoped>

</style>