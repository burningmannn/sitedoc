<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({
  middleware: ["auth"],
})

useHead({
  title: 'Загрузка документа - Документооборот',
  meta: [
    { name: 'description', content: 'Загрузка документов' }
  ]
})

const config = useRuntimeConfig()

const toast = useToast()

const file = ref<File | null>(null)
const responsible = ref<{ name: string; id: number } | null>(null)
const docType = ref<{ name: string; id: number } | null>(null)
const validUntil = ref<Date | null>(null)
const uploadedFileUrl = ref<string | null>(null)
const docNumber = ref<string | null>(null)
const permanent = ref(false)

const selectedRoute = ref<any | null>(null)


const services = ref<{ name: string; id: number }[]>([])
const documentTypes = ref<{ name: string; id: number }[]>([])

onMounted(async () => {
  try {
    // Подтягиваем типы документов
    documentTypes.value = await $fetch(`${config.public.apiBase}/api/file/doc-type`, { credentials: 'include' })

    // Подтягиваем департаменты
    services.value = await $fetch(`${config.public.apiBase}/api/admin/department`, { credentials: 'include' })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка загрузки', detail: 'Не удалось загрузить словари или маршруты', life: 3000 })
  }
})

const handleUpload = async () => {
  if (!file.value) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Пожалуйста, выберите файл', life: 3000 })
    return
  }

  const formData = new FormData()
  formData.append('file', file.value)
  if (responsible.value?.id) formData.append('responsible', responsible.value.id.toString())
  if (docType.value?.id) formData.append('doc_type', docType.value.id.toString())
  // if (validUntil.value) formData.append('valid_until', validUntil.value.toISOString().split('T')[0])
  if (validUntil.value) formData.append('valid_until', validUntil.value.toLocaleDateString('en-CA').split('T')[0])
  if (selectedRoute.value?.id) formData.append('route_id', selectedRoute.value.id)
  if (docNumber.value) formData.append('doc_number', docNumber.value.toString())
  if (permanent.value) formData.append('is_permanent', permanent.value.toString())

  try {
    const response = await $fetch(`${config.public.apiBase}/api/file/upload`, {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })

    uploadedFileUrl.value = `/file/${response.id}`
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Документ загружен', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Ошибка загрузки', life: 3000 })
  }
}
</script>


<template>
  <div class="card flex flex-col gap-6 max-w-2xl mx-auto mt-26">
    <Toast />
    <CustomUpload v-model="file" />
    <Dropdown v-model="responsible" :options="services" optionLabel="name" placeholder="Ответственная служба" />
    <Dropdown v-model="docType" :options="documentTypes" optionLabel="name" placeholder="Тип документа" />
    <InputText v-model="docNumber" placeholder="Номер документа" />
<!--    <Dropdown v-model="selectedRoute" :options="availableRoutes" optionLabel="name" placeholder="Выберите ответственных" />-->
    <div class="flex items-center justify-between">
      <div class="flex items-center justify-between">
        <div class="mr-2">Постоянный документ</div>
        <ToggleSwitch v-model="permanent" />
      </div>
      <div>
        <Calendar
            v-model="validUntil"
            dateFormat="yy-mm-dd"
            placeholder="Действителен до"
            :disabled="permanent"
        />
      </div>
    </div>
    <Button label="Загрузить документ" icon="pi pi-upload" @click="handleUpload" />
    <div v-if="uploadedFileUrl" class="text-green-600 text-sm">
      Файл загружен: <a :href="uploadedFileUrl" target="_blank" class="underline">{{ uploadedFileUrl }}</a>
    </div>
  </div>

</template>
