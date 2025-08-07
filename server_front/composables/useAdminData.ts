import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

export function useAdminData() {
    const toast = useToast()

    const docTypes = ref([])
    const departments = ref([])
    const users = ref([])
    const responsibles = ref([])

    const fetchData = async () => {
        docTypes.value = await $fetch('/api/file/doc-type')
        departments.value = await $fetch('/api/admin/department')
        users.value = await $fetch('/api/admin/users')
        responsibles.value = await $fetch('/api/admin/assign')
    }

    const addItem = async (url: string, name: string, successMsg: string) => {
        if (!name) return
        await $fetch(url, { method: 'POST', params: { name } })
        toast.add({ severity: 'success', summary: 'Добавлено', detail: successMsg, life: 3000 })
        await fetchData()
    }

    const deleteItem = async (url: string, successMsg: string) => {
        await $fetch(url, { method: 'DELETE' })
        toast.add({ severity: 'warn', summary: 'Удалено', detail: successMsg, life: 3000 })
        await fetchData()
    }

    const assignResponsible = async (departmentId: number, userId: number) => {
        await $fetch(`/api/admin/assign/${departmentId}/`, {
            method: 'POST',
            body: { user_id: userId }
        })
        toast.add({ severity: 'success', summary: 'Назначен ответственный', life: 3000 })
        await fetchData()
    }

    const deleteResponsible = async (responsibleId: number) => {
        await $fetch(`/api/admin/assign/${responsibleId}/`, { method: 'DELETE' })
        toast.add({ severity: 'success', summary: 'Ответственный удалён', life: 3000 })
        await fetchData()
    }

    return {
        docTypes,
        departments,
        users,
        responsibles,
        fetchData,
        addItem,
        deleteItem,
        assignResponsible,
        deleteResponsible
    }
}
