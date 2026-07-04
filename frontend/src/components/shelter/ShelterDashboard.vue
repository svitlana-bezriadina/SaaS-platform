<template>
  <div class="shelter-content">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <div style="display: flex; align-items: center; gap: 16px;">
        <h2 style="margin: 0; font-weight: 700; color: var(--color-heading);">🐾 Наші підопічні</h2>
        
        <a-radio-group v-model:value="viewMode" button-style="solid">
          <a-radio-button value="table"><TableOutlined /></a-radio-button>
          <a-radio-button value="grid"><AppstoreOutlined /></a-radio-button>
        </a-radio-group>
      </div>

      <a-button type="primary" size="large" @click="$emit('open-add-modal')" style="border-radius: 8px;">
        <PlusOutlined /> Додати тварину
      </a-button>
    </div>

    <a-card style="margin-bottom: 24px; border-radius: 12px; border: 1px solid var(--color-border); box-shadow: var(--color-shadow); background: var(--color-card-background);" :bodyStyle="{ padding: '16px 24px' }">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <a-space wrap size="middle">
          
          <a-input-search
            v-model:value="searchQuery"
            placeholder="Пошук за кличкою..."
            style="width: 200px; background: var(--bg-tertiary);"
            allow-clear
          />

          <a-select
            v-model:value="filterSpecies"
            placeholder="Всі види"
            style="width: 140px; background: var(--bg-tertiary);"
            allow-clear
          >
            <a-select-option v-for="species in uniqueSpecies" :key="species" :value="species">
              {{ species }}
            </a-select-option>
          </a-select>

          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--color-muted); font-size: 13px;">Вік:</span>
            <a-input-number v-model:value="filterAgeMin" placeholder="Від" style="width: 70px" :min="0" />
            <span style="color: var(--color-muted);">-</span>
            <a-input-number v-model:value="filterAgeMax" placeholder="До" style="width: 70px" :min="0" />
          </div>

          <a-select v-model:value="sortByDate" style="width: 170px">
            <a-select-option value="newest">Спочатку нові</a-select-option>
            <a-select-option value="oldest">Спочатку старі</a-select-option>
          </a-select>

        </a-space>
      </div>
    </a-card>

    <a-table 
      v-if="viewMode === 'table'"
      :columns="columns" 
      :data-source="filteredAnimals" 
      :loading="loading" 
      row-key="id"
      :pagination="{ pageSize: 10 }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column?.key === 'name'">
          <div style="display: flex; align-items: center; gap: 12px;">
            <a-avatar :src="record.photo_url" :size="40">
              {{ record.name.charAt(0).toUpperCase() }}
            </a-avatar>
            <div style="display: flex; flex-direction: column;">
              <span style="font-weight: 600; color: var(--color-heading);">{{ record.name }}</span>
              <span style="font-size: 11px; color: var(--color-muted);">
                Зареєстровано: {{ formatDate(record.date_register) }}
              </span>
            </div>
          </div>
        </template>
        
        <template v-else-if="column?.key === 'is_public'">
          <a-switch
            :checked="record.is_public"
            @change="togglePublicState(record)"
          />
        </template>
        <template v-else-if="column?.key === 'actions'">
          <a-space>
            <a-button type="text" @click="$emit('edit', record)" style="color: var(--accent-primary);"><EditOutlined /></a-button>
            <a-popconfirm title="Видалити?" @confirm="$emit('delete', record.id)">
              <a-button type="text" v-if="authStore.role === 'admin'"danger><DeleteOutlined style="color: var(--color-danger)" /></a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <div v-else class="animal-grid">
      <a-spin :spinning="loading">
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :sm="12" :md="8" :lg="6" v-for="animal in filteredAnimals" :key="animal.id">
            <a-card hoverable class="animal-card">
              <template #cover>
                <div class="card-image-wrapper">
                  <img alt="animal" :src="animal.photo_url || 'https://via.placeholder.com/200'" />
                </div>
              </template>
              
              <template #actions>
                <EditOutlined key="edit" @click="$emit('edit', animal)" />
                <a-popconfirm title="Видалити?" @confirm="$emit('delete', animal.id)">
                  <DeleteOutlined key="delete" v-if="authStore.role === 'admin'" style="color: var(--color-danger)" />
                </a-popconfirm>
              </template>

              <a-card-meta>
                <template #title>
                  <div class="card-title">{{ animal.name }}</div>
                </template>
                <template #description>
                  <div class="card-info">
                    <span class="animal-type">{{ animal.species }} • {{ animal.age }} р.</span>
                    <span style="font-size: 11px; color: var(--color-muted); margin-bottom: 4px;">
                      Зареєстровано: {{ formatDate(animal.date_register) }}
                    </span>
                    <div class="description-fixed">
                      {{ animal.description || 'Опис відсутній' }}
                    </div>
                  </div>
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
        </a-row>

        <div v-if="filteredAnimals.length === 0 && !loading" style="text-align: center; color: var(--color-muted); padding: 40px 0;">
          За вашим запитом тварин не знайдено
        </div>
      </a-spin>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { 
  PlusOutlined, EditOutlined, 
  DeleteOutlined, TableOutlined, AppstoreOutlined 
} from '@ant-design/icons-vue';
import { useAuthStore } from '../../stores/auth';

const props = defineProps({
  animals: { type: Array, default: () => [] },
  loading: Boolean,
  columns: Array
});

const emit = defineEmits(['open-add-modal', 'edit', 'delete', 'toggle-public']);

const togglePublicState = (animal) => {
  emit('toggle-public', animal);
};

const viewMode = ref('table');
const authStore = useAuthStore();
// --- ЛОГІКА ФІЛЬТРІВ ТА СОРТУВАННЯ ---
const searchQuery = ref('');
const filterSpecies = ref(null);
const filterAgeMin = ref(null);
const filterAgeMax = ref(null);
const sortByDate = ref('newest');

// Витягуємо унікальні види тварин для dropdown
const uniqueSpecies = computed(() => {
  const speciesList = props.animals.map(a => a.species).filter(Boolean);
  return [...new Set(speciesList)];
});

// Каскадна фільтрація
const filteredAnimals = computed(() => {
  let result = [...props.animals];

  if (searchQuery.value) {
    const lowerQuery = searchQuery.value.toLowerCase();
    result = result.filter(a => a.name.toLowerCase().includes(lowerQuery));
  }

  if (filterSpecies.value) {
    result = result.filter(a => a.species === filterSpecies.value);
  }

  if (filterAgeMin.value !== null && filterAgeMin.value !== '') {
    result = result.filter(a => a.age >= filterAgeMin.value);
  }

  if (filterAgeMax.value !== null && filterAgeMax.value !== '') {
    result = result.filter(a => a.age <= filterAgeMax.value);
  }

  result.sort((a, b) => {
    const dateA = new Date(a.date_register || 0);
    const dateB = new Date(b.date_register || 0);
    return sortByDate.value === 'newest' ? dateB - dateA : dateA - dateB ;
  });

  return result;
});

// Форматування дати
const formatDate = (dateString) => {
  if (!dateString) return 'Невідомо';
  const [year, month, day] = dateString.split('-');
  return `${day}.${month}.${year}`;
};
</script>

<style scoped>
/* Твої оригінальні стилі залишаються незмінними */
.animal-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
}

.card-image-wrapper {
  height: 200px;
  background: var(--color-surface);
  overflow: hidden;
}

.card-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 700;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.animal-type {
  font-size: 13px;
  color: var(--accent-primary);
  font-weight: 500;
}

.description-fixed {
  height: 40px; 
  font-size: 12px;
  color: var(--color-muted);
  line-height: 1.6;
  
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.public-tag {
  margin-top: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.12);
  color: #16a34a;
  font-size: 12px;
  font-weight: 600;
}

:deep(.ant-card-body) {
  flex-grow: 1;
}
</style>