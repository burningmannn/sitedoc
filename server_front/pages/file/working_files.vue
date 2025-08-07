<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
})

useHead({
  title: 'Файлы в работе - Документооборот',
  meta: [
    { name: 'description', content: 'Файлы назанченные пользователю' }
  ]
})
</script>

<template>
  <MiniTableInWorkFiles/>
</template>

<style scoped>

</style>