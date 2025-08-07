<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

useHead({
  title: 'Мои документы - Документооборот',
  meta: [
    { name: 'description', content: 'Уведомления пользователя' }
  ]
})
</script>

<template>
 <MiniTableMyFiles/>
</template>

<style scoped>

</style>