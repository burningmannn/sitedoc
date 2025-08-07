<script setup lang="ts">
import {ref, onMounted} from 'vue'
import {FilterMatchMode, FilterOperator, FilterService} from '@primevue/core/api'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Column from "primevue/column";

type FilterCallback = (value: any, filter: any) => boolean
const config = useRuntimeConfig()
const files = ref([])
const isLoading = ref(true)
const docTypes = ref<string[]>([])
const department = ref<string[]>([])
const permanent = ref([
  {label: 'Постоянный', value: true},
  {label: 'Срочный', value: false}
])

const customDateFilter: FilterCallback = (value: string, filter: [Date, Date] | null) => {

  if (!filter || filter.length !== 2 || !filter[0] || !filter[1]) return true;

  const valueDate = new Date(value);
  if (isNaN(valueDate.getTime())) return false;

  const start = new Date(filter[0]);
  start.setHours(0, 0, 0, 0);

  const end = new Date(filter[1]);
  end.setHours(23, 59, 59, 999);

  return valueDate >= start && valueDate <= end;
};


const filters = ref<any>({
  global: {value: null, matchMode: FilterMatchMode.CONTAINS},
  original_filename: {value: null, matchMode: FilterMatchMode.CONTAINS},
  'doc_type.name': {value: null, matchMode: FilterMatchMode.EQUALS},
  responsible: {value: null, matchMode: FilterMatchMode.EQUALS},
  file_number: {value: null, matchMode: FilterMatchMode.CONTAINS},
  uploaded_at: {value: null,matchMode: 'custom'},
  valid_until: {value: null,matchMode: 'custom'},
  permanent: {value: null, matchMode: FilterMatchMode.EQUALS},
})

const resetFilters = () => {
  filters.value = {
    global: {value: null, matchMode: FilterMatchMode.CONTAINS},
    original_filename: {value: null, matchMode: FilterMatchMode.CONTAINS},
    'doc_type.name': {value: null, matchMode: FilterMatchMode.EQUALS},
    responsible: {value: null, matchMode: FilterMatchMode.EQUALS},
    file_number: {value: null, matchMode: FilterMatchMode.CONTAINS},
    uploaded_at: {value: null,matchMode: 'custom'},
    valid_until: {value: null,matchMode: 'custom'},
    permanent: {value: null, matchMode: FilterMatchMode.EQUALS},
  }
}

onMounted(async () => {
  try {
    // Получение и сохранение списка отделов
    const departmentData = await $fetch(`${config.public.apiBase}/api/admin/department`)
    department.value = departmentData.map((d: any) => d.name)

    // Получение и преобразование списка файлов
    const data = await $fetch(`${config.public.apiBase}/api/file/all`, {
      credentials: 'include'
    })

    files.value = data.map((item: any) => ({
      ...item,
      uploaded_at: item.uploaded_at ? new Date(item.uploaded_at) : null,
      valid_until: item.valid_until ? new Date(item.valid_until) : null
    }))


    // Получение и сохранение списка типов документов
    const docTypesData = await $fetch(`${config.public.apiBase}/api/file/doc-type`, {
      credentials: 'include'
    })
    docTypes.value = docTypesData.map((d: any) => d.name)

  } catch (e) {
    console.error('Ошибка получения данных:', e)
  } finally {
  isLoading.value = false
}
})

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU')
}

FilterService.register('custom', (value, filters) => {
  if (!filters || filters.length !== 2) return true
  const dateValue = value ? new Date(value) : null
  const [start, end] = filters
  if (!dateValue) return false
  return dateValue >= start && dateValue <= end
})
</script>

<template>
  <div class="flex justify-end">
    <Button @click="resetFilters" icon="pi pi-filter-slash"/>
  </div>

  <DataTable
      v-model:filters="filters"
      :value="files"
      paginator
      :rows="10"
      dataKey="id"
      filterDisplay="row"
      :globalFilterFields="['original_filename', 'doc_type.name', 'responsible', 'file_number']"
      class="my-10"
      :loading="isLoading"
  >

    <Column field="original_filename" header="Название" :showFilterMenu="false">
      <template #body="{ data }">
        <NuxtLink
            :to="`/file/${data.id}`"
            class="text-blue-600 hover:underline"
            :title="data.original_filename"
        >
          {{ data.original_filename.length > 70 ? data.original_filename.slice(0, 70) + '…' : data.original_filename }}
        </NuxtLink>
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Поиск по имени"/>
      </template>
    </Column>

    <Column field="doc_type.name" header="Тип" :showFilterMenu="false">
      <template #body="{ data }">{{ data.doc_type.name }}</template>
      <template #filter="{ filterModel, filterCallback }">
        <Select v-model="filterModel.value" @change="filterCallback()" :options="docTypes" placeholder="Выберите тип"/>
      </template>
    </Column>

    <Column field="permanent" header="Статус" :showFilterMenu="false">
      <template #body="{ data }">
        {{ data.permanent ? 'Постоянный' : 'Срочный' }}
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <Select
            v-model="filterModel.value"
            @change="filterCallback()"
            :options="permanent"
            optionLabel="label"
            optionValue="value"
            placeholder="Выберите статус"
        />
      </template>
    </Column>

    <Column field="file_number" header="Номер" :showFilterMenu="false">
      <template #body="{ data }">{{ data.file_number }}</template>
      <template #filter="{ filterModel, filterCallback }">
        <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Поиск по номеру"/>
      </template>
    </Column>

    <Column
        field="uploaded_at"
        header="Создан"
        dataType="date"
        :filter="true"
        :showFilterMenu="false"
    >
      <template #body="{ data }">
        {{ data.uploaded_at ? formatDate(data.uploaded_at) : '—' }}
      </template>

      <template #filter="{ filterModel, filterCallback }">
        <DatePicker
            v-model="filterModel.value"
            selectionMode="range"
            placeholder="Выберите диапазон"
            dateFormat="dd.mm.yy"
            showIcon
            @update:modelValue="filterCallback()"
        />
      </template>
    </Column>

    <Column field="valid_until" header="Действует" :showFilterMenu="false">
      <template #body="{ data }">
        {{ data.valid_until ? new Date(data.valid_until).toLocaleDateString('ru-RU') : '—' }}
      </template>
      <template #filter="{ filterModel, filterCallback }">
        <Calendar
            v-model="filterModel.value"
            @date-select="filterCallback()"
            selectionMode="range"
            dateFormat="dd.mm.yy"
            placeholder="Диапазон дат"
            showIcon
        />
      </template>
    </Column>

    <template #loading>
      <div class="flex justify-center items-center py-10">
        <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4"/>
      </div>
    </template>

    <template #empty>
      <div class="mx-auto">
        Нет данных
      </div>
    </template>
  </DataTable>
</template>

<style scoped>
</style>
