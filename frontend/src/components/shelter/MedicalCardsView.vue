<template>
  <div class="medical-journal">
    <div class="journal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
      <h2 style="margin: 0; font-weight: 700; color: var(--color-heading);">Медичний журнал</h2>
    </div>

    <a-card style="margin-bottom: 24px; border-radius: 12px; border: 1px solid var(--color-border); box-shadow: var(--color-shadow); background: var(--color-card-background);" :bodyStyle="{ padding: '16px 24px' }">
      <a-space wrap size="middle">
        <a-input-search
          v-model:value="searchQuery"
          placeholder="Пошук за кличкою..."
          style="width: 250px"
          allow-clear
        />
        <a-select v-model:value="sortBy" style="width: 180px">
          <a-select-option value="newest">Спочатку нові</a-select-option>
          <a-select-option value="oldest">Спочатку старі</a-select-option>
        </a-select>
      </a-space>
    </a-card>

    <a-spin :spinning="loading">
      <div class="cards-grid">
        <div 
          v-for="animal in filteredAnimals" 
          :key="animal.id" 
          class="medical-card-item"
          @click="openNotebook(animal)"
        >
          <div class="card-header">
            <div class="card-avatar">
              <img v-if="animal.photo_url" :src="animal.photo_url" alt="avatar" />
              <div v-else class="avatar-placeholder">{{ animal.name.charAt(0).toUpperCase() }}</div>
            </div>
            <div class="card-title-block">
              <div class="animal-name">{{ animal.name }}</div>
              <div class="animal-species">{{ animal.species }} • {{ animal.age }} р.</div>
            </div>
          </div>
          
          <div class="card-divider"></div>
          
          <div class="card-footer">
            <div class="record-info">
              <span class="label">Останній запис:</span>
              <span class="date" :class="{ 'empty': !animal.last_record_date }">
                {{ animal.last_record_date ? formatDate(animal.last_record_date) : 'Немає записів' }}
              </span>
            </div>
            <div class="open-btn">
              <RightOutlined />
            </div>
          </div>
        </div>
        
        <div v-if="filteredAnimals.length === 0" style="grid-column: 1 / -1; text-align: center; color: var(--color-muted); padding: 40px;">
          Тварин не знайдено
        </div>
      </div>
    </a-spin>

    <AnimalNotebookModal
      v-model:open="isNotebookOpen"
      :animal="selectedAnimal"
      :records="cards"
      @refresh="$emit('refresh')"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { animalApi } from '@/api';
import { PlusOutlined, RightOutlined } from '@ant-design/icons-vue';
import AnimalNotebookModal from './MedicalNotebookModal.vue';

const props = defineProps({
  cards: { type: Array, default: () => [] },
  loading: Boolean
});

const emit = defineEmits(['refresh']);

const animals = ref([]);
const isNotebookOpen = ref(false);
const selectedAnimal = ref(null);

const searchQuery = ref('');
const sortBy = ref('newest');

const animalsWithLastRecord = computed(() => {
  if (!animals.value.length) return [];
  
  return animals.value.map(animal => {
    // Важливий фікс: нестроге порівняння id, щоб типи точно збіглися
    const animalRecords = props.cards?.filter(r => r.animal_id == animal.id) || [];
    
    const lastDate = animalRecords.length > 0 
      ? animalRecords.reduce((max, r) => new Date(r.record_date) > new Date(max) ? r.record_date : max, animalRecords[0].record_date)
      : null;

    return { ...animal, last_record_date: lastDate };
  });
});

const filteredAnimals = computed(() => {
  let result = [...animalsWithLastRecord.value];

  if (searchQuery.value) {
    result = result.filter(a => a.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
  }

  result.sort((a, b) => {
    const dateA = new Date(a.last_record_date || 0);
    const dateB = new Date(b.last_record_date || 0);
    return sortBy.value === 'newest' ? dateB - dateA : dateA - dateB;
  });

  return result;
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  const [year, month, day] = dateString.split('-');
  return `${month}/${day}/${year}`;
};

const openNotebook = (animal) => {
  selectedAnimal.value = animal;
  isNotebookOpen.value = true;
};

onMounted(async () => {
  try {
    const res = await animalApi.getAllAnimal();
    animals.value = res.data;
  } catch (e) { console.error(e); }
});
</script>

<style scoped>
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.medical-card-item {
  background: var(--color-card-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--color-shadow);
}

.medical-card-item:hover {
  transform: translateY(-4px);
  border-color: var(--color-border-hover);
  box-shadow: var(--color-shadow);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.card-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-surface);
  flex-shrink: 0;
}

.card-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  font-weight: 600;
  color: var(--color-muted);
}

.card-title-block {
  display: flex;
  flex-direction: column;
}

.animal-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-heading);
  margin-bottom: 4px;
}

.animal-species {
  font-size: 13px;
  color: var(--color-muted);
}

.card-divider {
  height: 1px;
  background: var(--color-border);
  margin-bottom: 16px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-info {
  display: flex;
  flex-direction: column;
}

.record-info .label {
  font-size: 11px;
  text-transform: uppercase;
  color: var(--color-muted);
  font-weight: 600;
  margin-bottom: 2px;
}

.record-info .date {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-heading);
}

.record-info .date.empty {
  color: var(--color-muted);
  font-weight: 400;
}

.open-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-surface);
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--color-muted);
  transition: all 0.2s;
}

.medical-card-item:hover .open-btn {
  background: var(--accent-primary);
  color: #ffffff;
}
</style>