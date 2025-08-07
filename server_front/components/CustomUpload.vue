<template>
  <div
      class="flex flex-col items-center justify-center w-full border-2 border-dashed border-gray-300 rounded-2xl p-6 hover:border-blue-400 transition cursor-pointer bg-white"
      @dragover.prevent
      @drop.prevent="handleDrop"
  >
    <label for="file-upload" class="flex flex-col items-center justify-center w-full cursor-pointer">
      <svg
          class="w-10 h-10 mb-3 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M7 16V4m0 0l-4 4m4-4l4 4M17 16V4m0 0l-4 4m4-4l4 4M3 20h18"/>
      </svg>
      <p class="text-sm text-gray-500">
        <span class="font-medium">Нажмите или перетащите</span> файл
      </p>
      <input
          id="file-upload"
          type="file"
          class="hidden"
          accept=".pdf,.doc,.docx,.jpeg,.jpg,.png"
          @change="handleFileChange"
      />
    </label>

    <div v-if="modelValue" class="mt-4 w-full text-center">
      <div v-if="isImage(modelValue)" class="flex flex-col items-center gap-2">
        <img :src="previewUrl" alt="Preview" class="max-h-40 rounded-xl shadow" />
        <p class="text-sm text-gray-600">{{ modelValue.name }}</p>
      </div>
      <div v-else class="flex flex-col items-center gap-2">
        <div class="w-12 h-12 flex items-center justify-center rounded-full bg-blue-100 text-blue-600">
          <i class="pi pi-file" />
        </div>
        <p class="text-sm text-gray-600">{{ modelValue.name }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  modelValue: File | null
}

interface Emits {
  (e: 'update:modelValue', value: File | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const previewUrl = ref<string | null>(null)

watch(() => props.modelValue, (file) => {
  if (file && isImage(file)) {
    previewUrl.value = URL.createObjectURL(file)
  } else {
    previewUrl.value = null
  }
})

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files?.[0]) {
    emit('update:modelValue', target.files[0])
  }
}

const handleDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files?.[0]) {
    emit('update:modelValue', e.dataTransfer.files[0])
  }
}

const isImage = (f: File) => f.type.startsWith('image/')
</script>

<style scoped>
</style>
