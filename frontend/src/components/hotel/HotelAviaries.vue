<template>
  <div class="aviaries-view">
    <div style="display: flex; justify-content: space-between; margin-bottom: 24px;">
      <h2>Фонд вольєрів (Номери)</h2>
      <a-button type="primary" @click="openAddModal">
        Додати вольєр
      </a-button>
    </div>

    <a-table 
      :columns="columns" 
      :data-source="aviaries" 
      :loading="loading"
      row-key="id"
      bordered
    >
      <template #bodyCell="{ column, record }">
        
        <template v-if="column.key === 'category'">
          <a-tag :color="record.category === 'VIP' ? 'gold' : 'green'">
            {{ record.category }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'Виведений з експлуатації' ? 'red' : 'blue'">
            {{ record.status === 'available' ? 'Доступний' : record.status }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'daily_price'">
          <strong>{{ record.daily_price }} грн</strong> / доба
        </template>

        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button type="link" @click="openEditModal(record)">Редагувати</a-button>
            <a-popconfirm
              v-if="record.status !== 'Виведений з експлуатації'"
              title="Списати цей вольєр? Він більше не буде доступний для бронювання."
              ok-text="Так"
              cancel-text="Ні"
              @confirm="deleteAviary(record.id)"
            >
              <a-button type="link" danger>Списати</a-button>
            </a-popconfirm>
          </a-space>
        </template>
        
      </template>
    </a-table>

    <a-modal 
      v-model:open="isModalOpen" 
      :title="isEditing ? 'Редагувати вольєр' : 'Новий вольєр'"
      @ok="handleSubmit"
    >
      <a-form layout="vertical">
        <a-form-item label="Номер або Назва (напр. '101' або 'Котячий Рай')">
          <a-input v-model:value="form.number" />
        </a-form-item>
        
        <a-form-item label="Категорія">
          <a-select v-model:value="form.category">
            <a-select-option value="Стандарт">Стандарт</a-select-option>
            <a-select-option value="Комфорт">Комфорт</a-select-option>
            <a-select-option value="VIP">VIP</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="Ціна за добу (грн)">
          <a-input-number v-model:value="form.daily_price" style="width: 100%" :min="0" />
        </a-form-item>

        <a-form-item label="Статус" v-if="isEditing">
          <a-select v-model:value="form.status">
            <a-select-option value="Доступний">Доступний</a-select-option>
            <a-select-option value="Ремонт">Ремонт</a-select-option>
            <a-select-option value="Виведений з експлуатації">Виведений з експлуатації</a-select-option>
          </a-select>
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
const aviaries = ref([]);
const loading = ref(false);
const isModalOpen = ref(false);
const isEditing = ref(false);
const editId = ref(null);

const form = ref({
  number: '',
  category: 'Стандарт',
  daily_price: 0,
  status: 'Доступний'
});

const columns = [
  { title: 'Назва/Номер', dataIndex: 'number', key: 'number' },
  { title: 'Категорія', dataIndex: 'category', key: 'category' },
  { title: 'Ціна', dataIndex: 'daily_price', key: 'daily_price' },
  { title: 'Статус', dataIndex: 'status', key: 'status' },
  { title: 'Дії', key: 'actions' }
];

const fetchAviaries = async () => {
  loading.value = true;
  try {
    const res = await bookingApi.getAviaries(authStore.token);
    aviaries.value = res.data;
  } catch (error) {
    message.error("Помилка завантаження вольєрів");
  } finally {
    loading.value = false;
  }
};

const openAddModal = () => {
  isEditing.value = false;
  form.value = { number: '', category: 'Стандарт', daily_price: 0, status: 'Доступний' };
  isModalOpen.value = true;
};

const openEditModal = (record) => {
  isEditing.value = true;
  editId.value = record.id;
  form.value = { ...record };
  isModalOpen.value = true;
};

const handleSubmit = async () => {
  try {
    if (isEditing.value) {
      await bookingApi.updateAviary(editId.value, form.value, authStore.token);
      message.success('Вольєр оновлено');
    } else {
      await bookingApi.createAviary(form.value, authStore.token);
      message.success('Вольєр додано');
    }
    isModalOpen.value = false;
    fetchAviaries();
  } catch (error) {
    message.error('Помилка збереження');
  }
};

const deleteAviary = async (id) => {
  try {
    // Soft Delete!
    await bookingApi.deleteAviary(id, authStore.token);
    message.success('Вольєр виведено з експлуатації');
    fetchAviaries();
  } catch (error) {
    message.error('Помилка видалення');
  }
};

onMounted(() => {
  fetchAviaries();
});
</script>