<template>
  <div class="services-view">
    <div style="display: flex; justify-content: space-between; margin-bottom: 24px;">
      <h2>Прайс-лист додаткових послуг</h2>
      <a-button type="primary" @click="openAddModal">
        Додати послугу
      </a-button>
    </div>

    <a-table 
      :columns="columns" 
      :data-source="services" 
      :loading="loading"
      row-key="id"
      bordered
    >
      <template #bodyCell="{ column, record }">
        
        <template v-if="column.key === 'price'">
          <strong>{{ record.price }} грн</strong>
        </template>

        <template v-else-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? 'Активна' : 'В архіві' }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button type="link" @click="openEditModal(record)">Редагувати</a-button>
            <a-popconfirm
              v-if="record.is_active"
              title="Перемістити в архів? Послуга зникне з меню бронювання."
              ok-text="Так"
              cancel-text="Ні"
              @confirm="deleteService(record.id)"
            >
              <a-button type="link" danger>В архів</a-button>
            </a-popconfirm>
          </a-space>
        </template>
        
      </template>
    </a-table>

    <a-modal 
      v-model:open="isModalOpen" 
      :title="isEditing ? 'Редагувати послугу' : 'Нова послугу'"
      @ok="handleSubmit"
    >
      <a-form layout="vertical" style="margin-top: 16px;">
        <a-form-item label="Назва послуги (напр. 'Стрижка кігтів')" required>
          <a-input v-model:value="form.name" />
        </a-form-item>

        <a-form-item label="Вартість (грн)" required>
          <a-input-number v-model:value="form.price" style="width: 100%" :min="0" />
        </a-form-item>

        <a-form-item label="Статус послуги" v-if="isEditing">
          <a-switch v-model:checked="form.is_active" checked-children="Активна" un-checked-children="В архіві" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { bookingApi } from '@/api';
import { message } from 'ant-design-vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const services = ref([]);
const loading = ref(false);
const isModalOpen = ref(false);
const isEditing = ref(false);
const editId = ref(null);

const form = ref({
  name: '',
  price: 0,
  is_active: true
});

const columns = [
  { title: 'ID', dataIndex: 'id', width: 60 },
  { title: 'Назва послуги', dataIndex: 'name', key: 'name' },
  { title: 'Вартість', dataIndex: 'price', key: 'price' },
  { title: 'Статус', dataIndex: 'is_active', key: 'is_active' },
  { title: 'Дії', key: 'actions' }
];

const fetchServices = async () => {
  loading.value = true;
  try {
    const res = await bookingApi.getAllServices();
    services.value = res.data;
  } catch (error) {
    message.error("Помилка завантаження прайс-листа");
  } finally {
    loading.value = false;
  }
};

const openAddModal = () => {
  isEditing.value = false;
  form.value = { name: '', price: 0, is_active: true };
  isModalOpen.value = true;
};

const openEditModal = (record) => {
  isEditing.value = true;
  editId.value = record.id;
  form.value = { ...record };
  isModalOpen.value = true;
};

const handleSubmit = async () => {
  if (!form.value.name) return message.warning('Введіть назву послуги');
  try {
    if (isEditing.value) {
      await bookingApi.updateService(editId.value, form.value, authStore.token);
      message.success('Послугу оновлено');
    } else {
      await bookingApi.createService(form.value, authStore.token);
      message.success('Послугу додано');
    }
    isModalOpen.value = false;
    fetchServices();
  } catch (error) {
    message.error('Помилка збереження');
  }
};

const deleteService = async (id) => {
  try {
    await bookingApi.deleteService(id, authStore.token);
    message.success('Послугу переміщено в архів');
    fetchServices();
  } catch (error) {
    message.error('Помилка видалення');
  }
};

onMounted(() => {
  fetchServices();
});
</script>