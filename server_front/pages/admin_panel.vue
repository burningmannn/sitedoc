<script setup lang="ts">
definePageMeta({
  middleware: ["auth", "admin"],
})

import {ref, onMounted} from 'vue'
import {useToast} from 'primevue/usetoast'
import {FilterMatchMode} from '@primevue/core/api';
import {useConfirm} from "primevue/useconfirm";

useHead({
  title: 'Админ-панель - Документооборот',
  meta: [
    { name: 'description', content: 'Уведомления пользователя' }
  ]
})

const toast = useToast()
const config = useRuntimeConfig()
const docTypes = ref([])
const departments = ref([])

const responsibles = ref([])
const confirm = useConfirm();

const users = ref([])
const editDialogVisible = ref(false)
const editedUser = ref({id: null, name: '', username: '', department_id: null, password: '', admin: false})
const selectedUser = ref(null)
const selectedDepartment = ref<string | null>(null)
const log_actions = ref("Загрузка...")
const log_errors = ref("Загрузка...")

async function loadLogActions() {
  try {
    log_actions.value = await $fetch(`${config.public.apiBase}/api/admin/actions`, {
      credentials: "include"
    })
  } catch (e) {
    log_actions.value = "Ошибка загрузки лога"
    toast.add({severity: 'error', summary: 'Ошибка', detail: `Не удалось загрузить лог событиый ${e}`, life: 3000})
  }
}

async function loadLogErrors() {
  try {
    log_errors.value = await $fetch(`${config.public.apiBase}/api/admin/errors`, {
      credentials: "include"
    })
  } catch (e) {
    log_errors.value = "Ошибка загрузки лога"
    toast.add({severity: 'error', summary: 'Ошибка', detail: `Не удалось загрузить лог событиый ${e}`, life: 3000})
  }
}


const filters = ref({
  global: {value: null, matchMode: FilterMatchMode.CONTAINS},
})

// Фильтры для справочников
const docTypeFilters = ref({
  global: {value: null, matchMode: FilterMatchMode.CONTAINS},
})
const departmentFilters = ref({
  global: {value: null, matchMode: FilterMatchMode.CONTAINS},
})
const responsibleFilters = ref({
  global: {value: null, matchMode: FilterMatchMode.CONTAINS},
})
// Диалоги и редактируемые объекты для справочников
const docTypeDialogVisible = ref(false)
const departmentDialogVisible = ref(false)

const editedDocType = ref({id: null, name: ''})
const editedDepartment = ref({id: null, name: ''})

// Функции для работы с диалогами типов документов
const openDocTypeDialog = (docType = null) => {
  if (docType) {
    editedDocType.value = {...docType}
  } else {
    editedDocType.value = {id: null, name: ''}
  }
  docTypeDialogVisible.value = true
}

const saveDocType = async () => {
  if (!editedDocType.value.name.trim()) {
    toast.add({severity: 'warn', summary: 'Поле не заполнено', detail: 'Введите название типа документа', life: 3000})
    return
  }
  
  try {
    if (editedDocType.value.id) {
      // Редактирование
      await $fetch(`${config.public.apiBase}/api/admin/doc-type/${editedDocType.value.id}`, {
        method: 'PUT',
        body: {name: editedDocType.value.name},
        credentials: 'include'
      })
      toast.add({severity: 'success', summary: 'Обновлено', detail: 'Тип документа обновлен', life: 3000})
    } else {
      // Создание
      await $fetch(`${config.public.apiBase}/api/admin/doc-type`, {
        method: 'POST',
        params: {name: editedDocType.value.name},
        credentials: 'include'
      })
      toast.add({severity: 'success', summary: 'Добавлено', detail: 'Тип документа добавлен', life: 3000})
    }
    
    docTypeDialogVisible.value = false
    await fetchData()
  } catch (e) {
    toast.add({severity: 'error', summary: 'Ошибка', detail: `Не удалось сохранить тип документа ${e}`, life: 3000})
  }
}

// Функции для работы с диалогами служб
const openDepartmentDialog = (department = null) => {
  if (department) {
    editedDepartment.value = {...department}
  } else {
    editedDepartment.value = {id: null, name: ''}
  }
  departmentDialogVisible.value = true
}

const saveDepartment = async () => {
  if (!editedDepartment.value.name.trim()) {
    toast.add({severity: 'warn', summary: 'Поле не заполнено', detail: 'Введите название службы', life: 3000})
    return
  }
  
  try {
    if (editedDepartment.value.id) {
      // Редактирование
      await $fetch(`${config.public.apiBase}/api/admin/department/${editedDepartment.value.id}`, {
        method: 'PUT',
        params: {name: editedDepartment.value.name},
        credentials: 'include'
      })
      toast.add({severity: 'success', summary: 'Обновлено', detail: 'Служба обновлена', life: 3000})
    } else {
      // Создание
      await $fetch(`${config.public.apiBase}/api/admin/department`, {
        method: 'POST',
        params: {name: editedDepartment.value.name},
        credentials: 'include'
      })
      toast.add({severity: 'success', summary: 'Добавлено', detail: 'Служба добавлена', life: 3000})
    }
    
    departmentDialogVisible.value = false
    await fetchData()
  } catch (e) {
    toast.add({severity: 'error', summary: 'Ошибка', detail: `Не удалось сохранить службу ${e}`, life: 3000})
  }
}

function editUser(user) {
  editedUser.value = {
    ...user,
    department_id: user.department ? user.department.id : null
  }
  console.log('Редактируемый пользователь:', editedUser.value) // Для отладки
  editDialogVisible.value = true
}

async function saveUser() {
  console.log('Сохраняем пользователя:', editedUser.value)
  console.log('department_id:', editedUser.value.department_id)
  try {
    await $fetch(`${config.public.apiBase}/api/admin/users/${editedUser.value.id}`, {
      method: 'PUT',
      body: editedUser.value,
      credentials: 'include'
    })
    toast.add({severity: 'success', summary: 'Обновлено', detail: 'Информация о пользователе обновлена', life: 3000})
    editDialogVisible.value = false
  } catch (e) {
    toast.add({severity: 'error', summary: 'Ошибка', detail: `Не удалось создать пользователя ${e}`, life: 3000})
  }
  await fetchData()
}

async function confirmDeleteUser(id: number) {
  confirm.require({
    message: 'Вы уверены, что хотите удалить пользователя?',
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
        await $fetch(`${config.public.apiBase}/api/admin/users/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        toast.add({severity: 'success', summary: 'Пользователь удалён', life: 3000})
        await fetchData()
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: `Не удалось удалить пользователя ${error}`,
          life: 3000
        })
      }
    },
  })
}

async function deleteDocType(id: number) {
  confirm.require({
    message: 'Вы уверены, что хотите удалить этот тип документа?\n' +
        'ВНИМАНИЕ: при удалении будут навсегда удалены ВСЕ файлы, связанные с этим типом.\n' +
        'Это действие необратимо.',
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
        await $fetch(`${config.public.apiBase}/api/admin/doc-type/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        toast.add({severity: 'success', summary: 'Тип документа удален', detail: 'Пользователь удалён', life: 3000})
        await fetchData()
      } catch (error) {
        toast.add({severity: 'error', summary: 'Ошибка', detail: 'Не удалось удалить пользователя', life: 3000})
      }
    },
  })
}

async function deleteDepartment(id: number) {
  confirm.require({
    message: 'Вы уверены, что хотите удалить службу?',
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
        await $fetch(`${config.public.apiBase}/api/admin/department/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        toast.add({
          severity: 'success',
          summary: 'Успех',
          detail: 'Служба удалена',
          life: 3000
        })
        await fetchData()
      } catch (error: any) {
        const errorMessage = error?.data?.detail || error.message || 'Неизвестная ошибка'
        toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: `Не удалось удалить службу: ${errorMessage}`,
          life: 5000
        })
      }
    },
  })
}


async function deleteResponsible(responsibleId: number) {
  confirm.require({
    message: 'Вы уверены, что хотите удалить ответственного?',
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
        await $fetch(`${config.public.apiBase}/api/admin/assign/${responsibleId}/`, {
          method: 'DELETE',
          credentials: 'include'
        })
        fetchData()
        toast.add({severity: 'success', summary: 'Успех', detail: 'Ответственный удалён', life: 3000})
      } catch (error) {
        toast.add({severity: 'error', summary: 'Ошибка', detail: 'Не удалось удалить ответственного', life: 3000})
        await fetchData()
      }
    },
  })
}

const fetchData = async () => {
  try {
    docTypes.value = await $fetch(`${config.public.apiBase}/api/file/doc-type`, {
      credentials: 'include'
    })
    departments.value = await $fetch(`${config.public.apiBase}/api/admin/department`, {
      credentials: 'include'
    })
    users.value = await $fetch(`${config.public.apiBase}/api/admin/users`, {
      credentials: 'include'
    })
    responsibles.value = await $fetch(`${config.public.apiBase}/api/admin/assign`, {
      credentials: 'include'
    })
  } catch (e) {
    toast.add({severity: 'error', summary: 'Ошибка', detail: 'Не загрузить данные старницы', life: 3000})
  }

}




const user = ref({
  username: '',
  password: '',
  name: '',
  department_id: null,
  admin: false
})

const registerUser = async () => {
  if (
      !user.value.username ||
      !user.value.password ||
      !user.value.name ||
      !user.value.department_id
  ) {
    toast.add({severity: 'warn', summary: 'Поля не заполнены', life: 3000})
    return
  }
  try {
    await $fetch(`${config.public.apiBase}/api/auth/signup`, {
      method: 'POST',
      body: user.value,
      credentials: 'include'
    })
    toast.add({severity: 'success', summary: 'Пользователь создан', life: 3000})
    user.value = {username: '', password: '', name: '', department_id: null, admin: false}
    // Обновляем список пользователей после создания
    await fetchData()
  } catch (e) {
    toast.add({severity: 'error', summary: 'Ошибка', detail: 'Не удалось создать пользователя', life: 3000})
    console.error(e)
  }
}

async function assignResponsible() {
  if (!selectedUser.value || !selectedDepartment.value) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Выберите отдел и пользователя',
      life: 3000
    })
    return
  }

  try {
    await $fetch(`${config.public.apiBase}/api/admin/assign/${selectedDepartment.value}/`, {
      method: 'POST',
      body: {
        user_id: selectedUser.value.id
      },
      credentials: 'include'
    })
    toast.add({
      severity: 'success',
      summary: 'Ответственный назначен',
      life: 3000
    })
    await fetchData()
  } catch (e) {
    console.error('Ошибка назначения:', e)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось назначить ответственного',
      life: 3000
    })
  }
}


onMounted(() => {
  fetchData()
  loadLogActions()
  loadLogErrors()
})
</script>

<template>
  <ConfirmDialog/>
  <div class="max-w-7xl mx-auto mt-20">
    <Toast/>
    <div class="">
      <h1 class="text-2xl font-semibold mb-6">Справочники</h1>
      <div class="flex gap-6">
        <div class="mb-10">
          <h2 class="text-xl font-semibold mb-4">Типы документов</h2>
          
          <div class="flex justify-start mb-4">
            <Button label="Добавить тип документа" icon="pi pi-plus" @click="openDocTypeDialog(null)" />
          </div>
          
          <DataTable
              :value="docTypes"
              :paginator="true"
              :rows="7"
              :rowsPerPageOptions="[5, 7, 10]"
              stripedRows
              responsiveLayout="scroll"
              :filters="docTypeFilters"
              :globalFilterFields="['name']"
              class="w-full"
          >
            <template #header>
              <div class="flex justify-start">
                <IconField>
                  <InputIcon>
                    <i class="pi pi-search"/>
                  </InputIcon>
                  <InputText v-model="docTypeFilters['global'].value" placeholder="Поиск типов документов..."/>
                </IconField>
              </div>
            </template>

            <Column field="id" sortable header="ID" style="width: 80px"/>
            <Column field="name" sortable header="Название"/>
            <Column header="Действия" style="width: 150px">
              <template #body="slotProps">
                <Button
                    icon="pi pi-pencil"
                    severity="secondary"
                    size="small"
                    text
                    @click="openDocTypeDialog(slotProps.data)"
                />
                <Button
                    icon="pi pi-trash"
                    severity="danger"
                    size="small"
                    text
                    @click="deleteDocType(slotProps.data.id)"
                />
              </template>
            </Column>
          </DataTable>
          
          <!-- Диалог для создания/редактирования типа документа -->
          <Dialog v-model:visible="docTypeDialogVisible" header="Тип документа" :modal="true" :closable="true">
            <div class="flex flex-col gap-4">
              <label>Название типа документа</label>
              <InputText v-model="editedDocType.name" placeholder="Введите название"/>
              <div class="flex justify-end gap-2 mt-4">
                <Button label="Отмена" severity="secondary" @click="docTypeDialogVisible = false"/>
                <Button label="Сохранить" @click="saveDocType"/>
              </div>
            </div>
          </Dialog>
        </div>

        <div>
          <h2 class="text-xl font-semibold mb-4">Службы</h2>
          
          <div class="flex justify-start mb-4">
            <Button label="Добавить службу" icon="pi pi-plus" @click="openDepartmentDialog(null)" />
          </div>
          
          <DataTable
              :value="departments"
              :paginator="true"
              :rows="7"
              :rowsPerPageOptions="[5, 7, 10]"
              stripedRows
              responsiveLayout="scroll"
              :filters="departmentFilters"
              :globalFilterFields="['name']"
              class="w-full"
          >
            <template #header>
              <div class="flex justify-start">
                <IconField>
                  <InputIcon>
                    <i class="pi pi-search"/>
                  </InputIcon>
                  <InputText v-model="departmentFilters['global'].value" placeholder="Поиск служб..."/>
                </IconField>
              </div>
            </template>

            <Column field="id" sortable header="ID" style="width: 80px"/>
            <Column field="name" sortable header="Название"/>
            <Column header="Действия" style="width: 150px">
              <template #body="slotProps">
                <Button
                    icon="pi pi-pencil"
                    severity="secondary"
                    size="small"
                    text
                    @click="openDepartmentDialog(slotProps.data)"
                />
                <Button
                    icon="pi pi-trash"
                    severity="danger"
                    size="small"
                    text
                    @click="deleteDepartment(slotProps.data.id)"
                />
              </template>
            </Column>
          </DataTable>
          
          <!-- Диалог для создания/редактирования службы -->
          <Dialog v-model:visible="departmentDialogVisible" header="Служба" :modal="true" :closable="true">
            <div class="flex flex-col gap-4">
              <label>Название службы</label>
              <InputText v-model="editedDepartment.name" placeholder="Название службы"/>
              <div class="flex justify-end gap-2 mt-4">
                <Button label="Отмена" severity="secondary" @click="departmentDialogVisible = false"/>
                <Button label="Сохранить" @click="saveDepartment"/>
              </div>
            </div>
          </Dialog>
        </div>

        <div>
          <h2 class="text-xl font-semibold mb-4">Ответственные по службам</h2>

          <div class="flex items-center gap-2 mb-4">
            <!-- Выбор пользователя -->
            <div class="card flex justify-center">
              <Select
                  v-model="selectedUser"
                  :options="users"
                  filter
                  optionLabel="name"
                  placeholder="Выберите ответственного"
                  class="w-full md:w-56"
              >
                <template #value="slotProps">
                  <div v-if="slotProps.value" class="flex items-center">
                    <div>{{ slotProps.value.name }}</div>
                  </div>
                  <span v-else>{{ slotProps.placeholder }}</span>
                </template>
                <template #option="slotProps">
                  <div class="flex items-center">
                    <div>{{ slotProps.option.name }}</div>
                  </div>
                </template>
              </Select>
            </div>

            <!-- Выбор службы -->
            <Dropdown
                v-model="selectedDepartment"
                :options="departments"
                optionLabel="name"
                optionValue="id"
                placeholder="Выберите службу"
                class="md:col-span-2"
            />

            <!-- Кнопка добавить -->
            <Button label="Добавить" @click="assignResponsible"/>
          </div>

          <DataTable
              :value="responsibles"
              :paginator="true"
              :rows="7"
              :rowsPerPageOptions="[5, 7, 10]"
              stripedRows
              responsiveLayout="scroll"
              :filters="responsibleFilters"
              :globalFilterFields="['user_name', 'department_name']"
              class="w-full"
          >
            <template #header>
              <div class="flex justify-start">
                <IconField>
                  <InputIcon>
                    <i class="pi pi-search"/>
                  </InputIcon>
                  <InputText v-model="responsibleFilters['global'].value" placeholder="Поиск ответственных..."/>
                </IconField>
              </div>
            </template>

            <Column field="id" sortable header="ID" style="width: 80px"/>
            <Column field="user_name" sortable header="Сотрудник"/>
            <Column header="Служба">
              <template #body="slotProps">
                {{ slotProps.data.department_name?.name || slotProps.data.department_name || 'Без отдела' }}
              </template>
            </Column>
            <Column header="Действия" style="width: 100px">
              <template #body="slotProps">
                <Button
                    icon="pi pi-trash"
                    severity="danger"
                    size="small"
                    text
                    @click="deleteResponsible(slotProps.data.id)"
                />
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
    </div>


    <div class="flex flex-col md:flex-row gap-10 mt-10">
      <!-- Левая колонка: Создание пользователя -->
      <div class="md:w-1/3">
        <h2 class="text-xl font-semibold mb-5">Создание нового пользователя</h2>
        <div class="flex flex-col gap-3">
          <InputText v-model="user.name" placeholder="Фамилия инициалы"/>
          <InputText v-model="user.username" placeholder="Логин"/>
          <InputText v-model="user.password" placeholder="Пароль" type="password"/>
          <Dropdown
              v-model="user.department_id"
              :options="departments"
              optionLabel="name"
              optionValue="id"
              placeholder="Выберите службу"
              class="w-full"
          />
          <div class="flex items-center gap-2 mt-2">
            <Checkbox v-model="user.admin" binary />
            <label>Администратор</label>
          </div>
          <Button class="mt-4" label="Зарегистрировать" icon="pi pi-user-plus" @click="registerUser"/>
        </div>
      </div>

      <!-- Правая колонка: Таблица -->
      <div class="md:w-2/3">
        <h2 class="text-xl font-semibold mb-2">Список пользователей</h2>

        <DataTable
            :value="users"
            :paginator="true"
            :rows="10"
            :rowsPerPageOptions="[5, 10, 20]"
            stripedRows
            responsiveLayout="scroll"
            :filters="filters"
            :globalFilterFields="['name']"
            class="w-full"
        >
          <template #header>
            <div class="flex justify-start">
              <IconField>
                <InputIcon>
                  <i class="pi pi-search"/>
                </InputIcon>
                <InputText v-model="filters['global'].value" placeholder="Поиск по имени..."/>
              </IconField>
            </div>
          </template>

          <Column field="id" sortable header="ID"/>
          <Column field="name" sortable header="Имя"/>
          <Column header="Роль">
            <template #body="slotProps">
              <Tag :value="slotProps.data.admin ? 'Админ' : 'Пользователь'" 
                   :severity="slotProps.data.admin ? 'success' : 'info'" />
            </template>
          </Column>
          <Column header="Действия" :exportable="false">
            <template #body="slotProps">
              <Button
                  icon="pi pi-pencil"
                  class="p-button-sm p-button-text text-blue-500"
                  @click="editUser(slotProps.data)"
              />
              <Button
                  icon="pi pi-trash"
                  class="p-button-sm p-button-text text-red-500"
                  @click="confirmDeleteUser(slotProps.data.id)"
              />
            </template>
          </Column>
        </DataTable>

        <!-- Диалог редактирования -->
        <Dialog v-model:visible="editDialogVisible" header="Редактировать пользователя" :modal="true" :closable="true">
          <div class="flex flex-col gap-4">
            <label>Логин</label>
            <InputText v-model="editedUser.username"/>
            <label>Пароль</label>
            <InputText v-model="editedUser.password"/>
            <label>ФИО</label>
            <InputText v-model="editedUser.name"/>
            <label>Служба</label>
            <Dropdown
                v-model="editedUser.department_id"
                :options="departments"
                optionLabel="name"
                optionValue="id"
                placeholder="Выберите службу"
                class="w-full"
            />
            <div class="flex items-center gap-2 mt-2">
              <Checkbox v-model="editedUser.admin" binary />
              <label>Администратор</label>
            </div>
            <Button label="Сохранить" class="mt-4" @click="saveUser"/>
          </div>
        </Dialog>
      </div>
    </div>


    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4">
      <!-- Журнал действий -->
      <div>
        <h2 class="text-xl font-semibold mb-2">Журнал действий</h2>
        <Button label="Обновить" @click="loadLogActions" class="mb-3" />
        <div class="bg-gray-100 p-4 rounded overflow-auto max-h-[75vh] text-sm whitespace-pre-wrap font-mono text-black">
          <div
              v-for="(line, index) in log_actions.split('\n').reverse()"
              :key="index"
              class="border-b border-gray-200 py-1"
          >
            {{ line }}
          </div>
        </div>
      </div>

      <!-- Журнал ошибок -->
      <div>
        <h2 class="text-xl font-semibold mb-2">Журнал ошибок</h2>
        <Button label="Обновить" @click="loadLogErrors" class="mb-3" />
        <div class="bg-red-100 p-4 rounded overflow-auto max-h-[75vh] text-sm whitespace-pre-wrap font-mono text-black">
          <div
              v-for="(line, index) in log_errors.split('\n').reverse()"
              :key="index"
              class="border-b border-red-200 py-1"
          >
            {{ line }}
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
