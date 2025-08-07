<template>
  <div class="flex flex-col min-h-screen">
    <main class="flex-1">
      <slot />
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Footer from '~/components/Footer.vue'
</script>