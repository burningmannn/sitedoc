<template>
  <div class="card p-14 mx-auto">
    <DataTable
        :value="documents"
        v-model:filters="filters"
        :paginator="true"
        :rows="10"
        :rowsPerPageOptions="[5, 10, 20]"
        dataKey="id"
        filterDisplay="menu"
        :globalFilterFields="['original_filename', 'doc_type', 'responsible']"
        :loading="loading"
        showGridlines
    >
      <template #header>
        <div class="flex justify-between items-center">
          <Button icon="pi pi-filter-slash" label="Сбросить" @click="clearFilters" outlined />
          <IconField>
            <InputIcon>
              <i class="pi pi-search" />
            </InputIcon>
            <InputText v-model="filters['global'].value" placeholder="Поиск..." />
          </IconField>
        </div>
      </template>

      <template #empty>Нет данных</template>
      <template #loading>Загрузка данных...</template>

      <Column field="original_filename" header="Название" style="min-width: 14rem">
        <template #body="{ data }">
          <NuxtLink target="_blank" :to="`/file/${data.id}`" class="text-blue-600 underline">
            {{ data.original_filename }}
          </NuxtLink>
        </template>
        <template #filter="{ filterModel }">
          <InputText v-model="filterModel.value" placeholder="Фильтр по названию" />
        </template>
      </Column>

      <Column field="doc_type_name" header="Тип документа" style="min-width: 12rem">
        <template #filter="{ filterModel }">
          <InputText v-model="filterModel.value" placeholder="Фильтр по типу" />
        </template>
      </Column>

      <Column field="responsible" header="Ответственная служба" style="min-width: 12rem">
        <template #body="{ data }">{{ data.responsible?.name }}</template>
        <template #filter="{ filterModel }">
          <InputText v-model="filterModel.value" placeholder="Фильтр по службе" />
        </template>
      </Column>

      <Column field="valid_until" header="Действителен до" style="min-width: 10rem">
        <template #body="{ data }">
          {{
            data.valid_until && !isNaN(new Date(data.valid_until).getTime())
                ? new Date(data.valid_until).toLocaleDateString('ru-RU')
                : "-"
          }}
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FilterMatchMode } from '@primevue/core/api';

const config = useRuntimeConfig()

const documents = ref([])
const loading = ref(false)

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
  original_filename: { value: null, matchMode: FilterMatchMode.CONTAINS },
  doc_type_name: { value: null, matchMode: FilterMatchMode.CONTAINS },
  responsible: { value: null, matchMode: FilterMatchMode.CONTAINS }
})

const clearFilters = () => {
  filters.value = {
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    original_filename: { value: null, matchMode: FilterMatchMode.CONTAINS },
    doc_type: { value: null, matchMode: FilterMatchMode.CONTAINS },
    responsible: { value: null, matchMode: FilterMatchMode.CONTAINS }
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/api/file/inwork`, {
      credentials: 'include'
    })

    // Добавляем плоское поле doc_type_name для фильтрации
    documents.value = response.map((doc) => ({
      ...doc,
      doc_type_name: doc.doc_type?.name || ''
    }))
  } catch (err) {
    console.error('Ошибка при получении данных:', err)
  } finally {
    loading.value = false
  }
})
</script>
