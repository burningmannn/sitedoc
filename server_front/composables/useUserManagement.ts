export function useUserManagement(fetchData: () => Promise<void>) {
    const config = useRuntimeConfig()
    interface User {
        id: number | null
        name: string
        username: string
        department_id: string | null
        // добавь остальные свойства, которые есть у пользователя
    }

    const toast = useToast()
    const editDialogVisible = ref(false)

    const editedUser = ref<User>({
        id: null,
        name: '',
        username: '',
        department_id: null,
    })
    const editUser = (user: User) => {
        editedUser.value = { ...user }
        editDialogVisible.value = true
    }

    const saveUser = async () => {
        await $fetch(`${config.public.apiBase}/api/admin/users/${editedUser.value.id}`, {
            method: 'PUT',
            body: editedUser.value
        })
        editDialogVisible.value = false
        await fetchData()
    }

    const deleteUser = async (id: number) => {
        if (confirm('Вы уверены, что хотите удалить пользователя?')) {
            await $fetch(`${config.public.apiBase}/api/admin/users/${id}`, { method: 'DELETE' })
            await fetchData()
        }
    }

    const user = ref({
        username: '',
        password: '',
        name: '',
        last_name: '',
        department_id: null
    })

    const registerUser = async () => {
        if (!user.value.username || !user.value.password || !user.value.name || !user.value.department_id) {
            toast.add({ severity: 'warn', summary: 'Поля не заполнены', life: 3000 })
            return
        }
        try {
            await $fetch(`${config.public.apiBase}/api/auth/register`, {
                method: 'POST',
                body: user.value
            })
            toast.add({ severity: 'success', summary: 'Пользователь создан', life: 3000 })
            user.value = { username: '', password: '', name: '', last_name: '', department_id: null }
            await fetchData()
        } catch (e) {
            toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось создать пользователя', life: 3000 })
            console.error(e)
        }
    }

    return {
        user,
        editedUser,
        editDialogVisible,
        editUser,
        saveUser,
        deleteUser,
        registerUser
    }
}
