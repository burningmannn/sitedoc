<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useAuthStore } from '~/stores/auth'

const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user)
const fileId = route.params.id
const file = ref<any>(null)
const editedFile = ref<any>({})
const newFile = ref<File | null>(null)
const isEditing = ref(false)
const toast = useToast()
const confirm = useConfirm()
const departments = ref([])
const doc_types = ref([])
const permanent = ref(false)


async function fetchFileInfo() {
  try {
    file.value = await $fetch(`${config.public.apiBase}/api/file/info/${fileId}`, {
      credentials: 'include'
    })
    editedFile.value = { ...file.value }
    editedFile.value = {
      ...file.value,
      responsible: file.value.responsible ?? null
    }

    // Если поле permanent в ответе === true, обновляем реактивную переменную
    if (file.value.permanent === true) {
      permanent.value = true
    }
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: `Не удалось загрузить информацию о файле`,
      life: 3000
    })
  }
}

const selectedDepartmentId = ref<number | null>(null)
const selectedDocTypeId = ref<number | null>(null)

watch(() => editedFile.value.responsible, (newVal) => {
  selectedDepartmentId.value = newVal?.id ?? null
}, { immediate: true })

watch(selectedDepartmentId, (newId) => {
  editedFile.value.responsible = departments.value.find(dep => dep.id === newId) ?? null
})

watch(() => editedFile.value.doc_typeId, (newVal) => {
  selectedDocTypeId.value = newVal?.id ?? null
}, { immediate: true })

watch(selectedDocTypeId, (newId) => {
  editedFile.value.doc_type = doc_types.value.find(type => type.id === newId) ?? null
})

async function fetchDocTypes(){
  try {
    const response = await $fetch(`${config.public.apiBase}/api/file/doc-type`, {
      credentials: 'include'
    })
    doc_types.value = [
      { id: null, name: 'Нет типов документа' },
      ...response
    ]
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить типы документа',
      life: 3000
    })
  }
}

async function fetchDepartments() {
  try {
    const response = await $fetch(`${config.public.apiBase}/api/admin/department`, {
      credentials: 'include'
    })

    // Добавляем опцию "Нет ответственного" в начало списка
    departments.value = [
      { id: null, name: 'Нет ответственного' },
      ...response
    ]
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить список служб',
      life: 3000
    })
  }
}

function handleEditClick() {
  if (authStore.user) {
    isEditing.value = true
  } else {
    toast.add({
      severity: 'warn',
      summary: 'Требуется вход',
      detail: 'Пожалуйста, войдите в систему, чтобы редактировать.',
      life: 4000
    })
    navigateTo('/login') // по желанию
  }
}

function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    newFile.value = target.files[0]
  } else {
    newFile.value = null
  }
}

onMounted(async () => {
  await fetchFileInfo();
  await fetchDepartments();
  await fetchDocTypes();
})

async function updateFileInfo() {
  try {
    // Подготавливаем данные для отправки на сервер
    const updateData = {
      original_filename: editedFile.value.original_filename,
      doc_number: editedFile.value.doc_number,
      doc_type_id: selectedDocTypeId.value,
      responsible_id: selectedDepartmentId.value,
      permanent: permanent.value,
      valid_until: editedFile.value.valid_until
    }

    console.log('Отправляем данные:', updateData)

    await $fetch(`${config.public.apiBase}/api/file/update/${fileId}`, {
      method: 'PUT',
      body: updateData,
      credentials: 'include'
    })

    toast.add({ severity: 'success', summary: 'Обновлено', detail: 'Информация обновлена', life: 3000 })
    isEditing.value = false
    await fetchFileInfo();
  } catch (e) {
    console.error('Ошибка при обновлении:', e)
    toast.add({ severity: 'error', summary: 'Ошибка', detail: `Не удалось обновить файл: ${e?.data?.detail || e.message || 'Неизвестная ошибка'}`, life: 4000 })
  }
}

async function cancelUpdateFileInfo() {
  isEditing.value = false
  await fetchFileInfo();
}

const replaceFile = async () => {
  if (!newFile.value) {
    toast.add({ severity: 'warn', summary: 'Файл не выбран', detail: 'Пожалуйста, выберите файл', life: 3000 })
    return
  }

  const formData = new FormData()
  formData.append('file', newFile.value)

  try {
    const response = await fetch(`${config.public.apiBase}/api/file/replace/${fileId}`, {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      toast.add({
        severity: 'error',
        summary: 'Ошибка при замене файла',
        detail: errorData?.detail || 'Не удалось заменить файл',
        life: 4000
      })
      return
    }

    toast.add({ severity: 'success', summary: 'Файл заменён', detail: 'Файл успешно загружен', life: 3000 })
    newFile.value = null
    await fetchFileInfo()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка сети',
      detail: error instanceof Error ? error.message : String(error),
      life: 4000
    })
  }
}

function confirmDeleteFile() {
  confirm.require({
    message: 'Вы уверены, что хотите удалить файл?',
    header: 'Подтверждение удаления',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Отмена',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Удалить',
      severity: 'danger'
    },
    accept: async () => {
      try {
        await $fetch(`${config.public.apiBase}/api/file/delete/${fileId}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        toast.add({ severity: 'success', summary: 'Удалено', detail: 'Файл удалён', life: 3000 })
        await router.push('/')
      } catch (e) {
        console.error(e)
        toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось удалить файл', life: 3000 })
      }
    }
  })
}

function downloadFile() {
  window.open(`${config.public.apiBase}/api/file/download/${fileId}`, '_blank')
}
</script>

<template>
  <ConfirmDialog />
  <div class="max-w-3xl mx-auto p-6 bg-white shadow rounded mt-26 space-y-4">
    <ConfirmDialog group="templating">
      <template #message="slotProps">
        <div class="flex flex-col items-center w-full gap-4 border-b border-surface-200 dark:border-surface-700">
          <i :class="slotProps.message.icon" class="!text-6xl text-primary-500"></i>
          <p>{{ slotProps.message.message }}</p>
        </div>
      </template>
    </ConfirmDialog>

    <div class="flex justify-between">
      <h1 class="text-2xl font-semibold">Информация о файле</h1>
      <div class="flex gap-2 mb-4">
        <div v-if="user">
          <Button label="Редактировать" icon="pi pi-pencil" @click="handleEditClick" />
        </div>
        <Button label="Скачать" icon="pi pi-download" @click="downloadFile" />
      </div>
    </div>


    <div v-if="file">
      <div class="space-y-2">
        <label class="block">
          <span>Название</span>
          <InputText v-model="editedFile.original_filename" class="w-full" :disabled="!isEditing" />
        </label>
        <label class="block">
          <span>Тип</span>
          <Dropdown
              v-model="selectedDocTypeId"
              :options="doc_types"
              optionLabel="name"
              optionValue="id"
              placeholder="Выберите тип документа"
              class="w-full"
              :disabled="!isEditing"
          />
        </label>
        <label class="block">
          <span>Номер</span>
          <InputText v-model="editedFile.doc_number" class="w-full" :disabled="!isEditing" />
        </label>
        <label class="block">
          <span>Ответственная служба</span>
          <Dropdown
              v-model="selectedDepartmentId"
              :options="departments"
              optionLabel="name"
              optionValue="id"
              placeholder="Выберите службу"
              class="w-full"
              :disabled="!isEditing"
          />
        </label>

        <div class="flex items-center justify-between mt-4">
          <div class="flex items-center justify-between">
            <div class="mr-2">Постоянный документ</div>
            <ToggleSwitch v-model="permanent" :disabled="!isEditing" />
          </div>
          <div>
            <Calendar
                v-model="editedFile.valid_until"
                dateFormat="yy-mm-dd"
                placeholder="Действителен до"
                :disabled="permanent || !isEditing"
            />
          </div>
        </div>


        <div class="flex gap-2">
          <div v-if="isEditing">
            <Button label="Сохранить изменения" icon="pi pi-check" @click="updateFileInfo" class="mt-2" />
          </div>
          <div v-if="isEditing">
            <Button severity="warn" label="Отменить" icon="pi pi-times" @click="cancelUpdateFileInfo" class="mt-2" />
          </div>
        </div>

      </div>

      <div class="mt-10" v-if="user">
        <div class="">
          <h2 class="text-2xl font-semibold mb-4 text-gray-800 flex items-center gap-2">
            <i class="pi pi-refresh text-primary" />
            Заменить файл
          </h2>

          <label for="fileUpload" class="block text-sm font-medium text-gray-700 mb-1">
            Выберите новый файл:
          </label>
          <input
              id="fileUpload"
              type="file"
              class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-primary focus:outline-none"
              @change="onFileSelected"
          />

          <div v-if="newFile" class="mt-2 text-sm text-gray-600">
            <span class="font-medium text-gray-800">Выбран файл:</span> {{ newFile?.name }}
          </div>

          <div class="flex gap-4 mt-4">
            <Button
                icon="pi pi-undo"
                label="Заменить файл"
                @click="replaceFile"
                class="w-full"
            />
            <Button
                label="Удалить файл"
                icon="pi pi-trash"
                @click="confirmDeleteFile"
                severity="danger"
                class="w-full"
            />
          </div>
        </div>
      </div>


    </div>
  </div>
</template>
