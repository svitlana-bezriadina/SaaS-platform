<template>
  <div class="inventory-container">
    
    <div class="header-actions">
      <div style="display: flex; align-items: center; gap: 16px;">
        <h2 style="margin: 0; font-weight: 700; color: var(--color-heading);">📦 Склад та припаси</h2>
      </div>
      <a-button type="primary" shape="round" size="large" @click="openAddModal">
        <PlusOutlined /> Додати товар
      </a-button>
    </div>

    <a-tabs v-model:activeKey="activeCategory" class="custom-tabs">
      <a-tab-pane key="Всі" tab="Усі товари"></a-tab-pane>
      <a-tab-pane key="Корм" tab="🥩 Корм"></a-tab-pane>
      <a-tab-pane key="Ліки" tab="💊 Ліки"></a-tab-pane>
      <a-tab-pane key="Амуніція" tab="🪀 Амуніція"></a-tab-pane>
      <a-tab-pane key="Господарські" tab="🧴 Господарські"></a-tab-pane>
    </a-tabs>

    <div class="filters-panel">
      <a-input-search
        v-model:value="searchQuery"
        placeholder="Шукати за назвою..."
        style="width: 250px"
        allow-clear
      />
      <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
        <a-select v-model:value="targetAnimalFilter" placeholder="Фільтр за призначенням" style="width: 200px">
          <a-select-option value="Усі">Усі</a-select-option>
          <a-select-option value="Котів">🐱 Котів</a-select-option>
          <a-select-option value="Собак">🐶 Собак</a-select-option>
          <a-select-option value="Універсальний">🐾 Універсальний</a-select-option>
          <a-select-option value="Без призначення">Без призначення</a-select-option>
        </a-select>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 14px; color: var(--color-muted); font-weight: 500;">
            Тільки ті, що закінчуються:
          </span>
          <a-switch v-model:checked="showLowStockOnly" />
        </div>
      </div>
    </div>

    <a-spin :spinning="loading">
      <div v-if="filteredInventory.length === 0" class="empty-state">
        <div style="font-size: 40px; margin-bottom: 16px;">🪹</div>
        <p>Товарів не знайдено або склад порожній.</p>
      </div>

      <a-row v-else :gutter="[16, 16]">
        <a-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in filteredInventory" :key="item.id">
          <a-card hoverable class="inventory-card" :class="{ 'low-stock-card': isLowStock(item) }">
            
            <div class="card-header">
              <div class="item-title">
                <div>{{ item.name }}</div>
                <div v-if="item.target_animal" class="target-animal-sub">
                  🐾 Для: {{ item.target_animal }}
                </div>
              </div>
              <a-tag :color="getCategoryColor(item.category)">{{ item.category }}</a-tag>
            </div>

            <div class="progress-section">
              <div class="quantity-text">
                <span class="current-qty">{{ item.quantity }}</span> 
                <span class="total-qty"> / {{ item.target_quantity }} {{ item.unit }}</span>
              </div>
              <a-progress 
                :percent="getProgressPercent(item)" 
                :status="isLowStock(item) ? 'exception' : 'normal'"
                :show-info="false" 
                stroke-linecap="square"
              />
              <div v-if="isLowStock(item)" class="alert-text">
                <WarningOutlined /> Закінчується!
              </div>
            </div>

            <div class="card-footer">
              <div class="quick-actions">
                <a-button shape="circle" size="small" @click="quickUpdate(item, -1)">
                  <MinusOutlined />
                </a-button>
                <a-button shape="circle" size="small" @click="quickUpdate(item, 1)">
                  <PlusOutlined />
                </a-button>
              </div>
              
              <div class="admin-actions">
                <a-button type="text" size="small" style="color: var(--accent-primary);" @click="openEditModal(item)">
                  <EditOutlined />
                </a-button>
                <a-popconfirm title="Видалити товар?" @confirm="deleteItem(item.id)">
                  <a-button type="text" v-if="authStore.role === 'admin'" danger size="small"><DeleteOutlined /></a-button>
                </a-popconfirm>
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </a-spin>

    <a-modal
      v-model:open="isModalOpen"
      :title="editingId ? 'Редагувати товар' : 'Додати новий товар'"
      @ok="submitForm"
      @cancel="resetForm"
      ok-text="Зберегти"
      cancel-text="Скасувати"
    >
      <a-form layout="vertical">
        <a-form-item label="Назва товару" required>
          <a-input v-model:value="form.name" placeholder="Введіть назву" />
        </a-form-item>
        
        <a-form-item label="Категорія" required>
          <a-select v-model:value="form.category" placeholder="Оберіть категорію">
            <a-select-option value="Корм">🥩 Корм</a-select-option>
            <a-select-option value="Ліки">💊 Ліки</a-select-option>
            <a-select-option value="Амуніція">🪀 Амуніція</a-select-option>
            <a-select-option value="Господарські">🧴 Gospodars'ki</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item 
          v-if="form.category === 'Корм' || form.category === 'Ліки'" 
          label="Призначення (Для яких тварин)"
        >
          <a-select v-model:value="form.target_animal" placeholder="Оберіть вид або залиште порожнім" allow-clear>
            <a-select-option value="Котів">🐱 Для котів</a-select-option>
            <a-select-option value="Собак">🐶 Для собак</a-select-option>
            <a-select-option value="Універсальний">🐾 Універсальний</a-select-option>
          </a-select>
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="Поточна кількість" required>
              <a-input-number v-model:value="form.quantity" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="Бажана норма (для 100%)" required>
              <a-input-number v-model:value="form.target_quantity" :min="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="Одиниці виміру (кг, шт, мл)" required>
          <a-input v-model:value="form.unit" placeholder="Наприклад: кг" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  PlusOutlined, MinusOutlined, EditOutlined, 
  DeleteOutlined, WarningOutlined 
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { animalApi } from '@/api';
import { useAuthStore } from '../../stores/auth';


const inventory = ref([]);
const loading = ref(false);
const authStore = useAuthStore();

const activeCategory = ref('Всі');
const searchQuery = ref('');
const targetAnimalFilter = ref('Усі');
const showLowStockOnly = ref(false);

const isModalOpen = ref(false);
const editingId = ref(null);
const form = ref({
  name: '',
  category: 'Корм',
  quantity: 0,
  target_quantity: 10,
  unit: 'кг',
  target_animal: null 
});

const fetchInventory = async () => {
  loading.value = true;
  try {
    const res = await animalApi.getAllInventory();
    inventory.value = res.data;
  } catch (error) {
    message.error('Помилка завантаження складу');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchInventory();
});

const getProgressPercent = (item) => {
  if (!item.target_quantity) return 0;
  const percent = (item.quantity / item.target_quantity) * 100;
  return Math.min(100, Math.round(percent));
};

const isLowStock = (item) => {
  return getProgressPercent(item) <= 20;
};

const getCategoryColor = (category) => {
  const colors = {
    'Корм': 'green',
    'Ліки': 'red',
    'Амуніція': 'blue',
    'Господарські': 'purple'
  };
  return colors[category] || 'default';
};

const filteredInventory = computed(() => {
  let result = inventory.value;

  if (activeCategory.value !== 'Всі') {
    result = result.filter(item => item.category === activeCategory.value);
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(item => item.name.toLowerCase().includes(query));
  }

  if (targetAnimalFilter.value && targetAnimalFilter.value !== 'Усі') {
    result = result.filter(item => {
      if (targetAnimalFilter.value === 'Без призначення') {
        return !item.target_animal;
      }
      return item.target_animal === targetAnimalFilter.value;
    });
  }

  if (showLowStockOnly.value) {
    result = result.filter(item => isLowStock(item));
  }

  return result.sort((a, b) => {
    if (isLowStock(a) !== isLowStock(b)) return isLowStock(a) ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
});

const quickUpdate = async (item, change) => {
  const newQuantity = Math.max(0, item.quantity + change);
  if (newQuantity === item.quantity) return;

  const originalQuantity = item.quantity;
  item.quantity = newQuantity;

  try {
    await animalApi.updateInventory(item.id, { quantity: newQuantity });
  } catch (error) {
    item.quantity = originalQuantity;
    message.error('Помилка оновлення');
  }
};

const deleteItem = async (id) => {
  try {
    await animalApi.deleteInventory(id);
    inventory.value = inventory.value.filter(item => item.id !== id);
    message.success('Видалено');
  } catch (error) {
    message.error('Помилка видалення');
  }
};

const openAddModal = () => {
  resetForm();
  isModalOpen.value = true;
};

const openEditModal = (item) => {
  editingId.value = item.id;
  form.value = { ...item };
  isModalOpen.value = true;
};

const submitForm = async () => {
  if (!form.value.name || form.value.quantity === null) {
    return message.warning('Заповніть обов\'язкові поля');
  }

  // Якщо категорію змінили на амуніцію чи господарські - примусово очищуємо поле перед відправкою
  if (form.value.category !== 'Корм' && form.value.category !== 'Ліки') {
    form.value.target_animal = null;
  }

  try {
    if (editingId.value) {
      await animalApi.updateInventory(editingId.value, form.value);
      message.success('Оновлено успішно');
    } else {
      await animalApi.createInventory(form.value);
      message.success('Додано на склад');
    }
    await fetchInventory();
    isModalOpen.value = false;
  } catch (error) {
    message.error('Сталася помилка');
  }
};

const resetForm = () => {
  editingId.value = null;
  form.value = { name: '', category: 'Корм', quantity: 0, target_quantity: 10, unit: 'кг', target_animal: null };
};
</script>

<style scoped>
/* Усі твої попередні стилі залишаються незмінними */
.inventory-container {
  padding: 10px 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.custom-tabs :deep(.ant-tabs-nav::before) {
  border-bottom: 2px solid var(--color-border);
}

.filters-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: var(--color-surface);
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--color-muted);
}

.inventory-card {
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid var(--color-border);
  background: var(--color-card-background);
  transition: all 0.3s;
}

.low-stock-card {
  border-color: var(--color-danger);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.item-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-heading);
  line-height: 1.3;
  margin-right: 8px;
}

/* Новий дрібний стиль для підпису тварини */
.target-animal-sub {
  font-size: 12px;
  color: var(--color-muted);
  font-weight: 500;
  margin-top: 2px;
}

.progress-section {
  flex-grow: 1;
  margin-bottom: 16px;
}

.quantity-text {
  margin-bottom: 4px;
}

.current-qty {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-heading);
}

.total-qty {
  font-size: 14px;
  color: var(--color-muted);
}

.alert-text {
  font-size: 12px;
  color: var(--color-danger);
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.admin-actions {
  display: flex;
  gap: 4px;
}
</style>