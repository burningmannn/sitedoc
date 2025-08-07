<script setup lang="ts">
useHead({
  title: '403 - Документооборот',
  meta: [
    { name: 'description', content: 'Нет прав у пользователя' }
  ]
})
</script>

<template>
  <div class="w-full flex-row items-center mx-auto mt-32">
    <p class="text-4xl items-center text-center h-12">Недостаточно прав</p>
    <p class="text-xl items-center text-center h-12 text-gray-700">У вас нет прав для просмотра данной старницы</p>
    <div class="flex flex-wrap justify-around items-center">
      <NuxtLink to="/">
        <Button label="На главную"/>
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>

</style>