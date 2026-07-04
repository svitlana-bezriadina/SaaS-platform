<template>
  <a-modal 
    :open="open" 
    :footer="null" 
    :closable="true" 
    width="900px" 
    centered
    @cancel="closeModal"
    class="medical-profile-modal"
    :title="`Медична картка: ${animal?.name || 'Пацієнт'}`"
  >
    <div class="medical-profile-layout">
      
      <div class="left-sidebar">
        <div class="profile-card">
          <div class="avatar-wrapper">
            <img v-if="animal?.photo_url" :src="animal.photo_url" alt="animal photo" />
            <div v-else class="avatar-placeholder">
              <PictureOutlined />
            </div>
          </div>
          
          <h3 class="patient-name">{{ animal?.name }}</h3>
          <div class="patient-tags">
            <a-tag color="blue">{{ animal?.species }}</a-tag>
            <a-tag color="purple">{{ animal?.age }} р.</a-tag>
          </div>

          <div class="health-status-wrapper" v-if="animal">
            <a-select
              v-model:value="animal.health_status"
              :bordered="false"
              class="status-select"
              :class="getStatusColorClass(animal.health_status)"
              @change="updateHealthStatus"
            >
              <template #suffixIcon><DownOutlined style="color: inherit;"/></template>
              <a-select-option value="Здоровий">🟢 Здоровий</a-select-option>
              <a-select-option value="На лікуванні">🟡 На лікуванні</a-select-option>
              <a-select-option value="Критичний">🔴 Критичний</a-select-option>
              <a-select-option value="Карантин">🔵 Карантин</a-select-option>
            </a-select>
          </div>
        </div>

        <a-button type="primary" block size="large" class="add-btn" @click="openAddForm">
          <PlusOutlined /> Додати запис
        </a-button>
      </div>

      <div class="right-content">
        <a-tabs v-model:activeKey="activeTab">
          
          <a-tab-pane key="history" tab="🩺 Історія хвороби">
            <div class="timeline-container">
              
              <div class="timeline-filters">
                <a-input-search
                  v-model:value="searchQuery"
                  placeholder="Пошук за діагнозом..."
                  style="width: 220px"
                  allow-clear
                />
                <a-range-picker
                  v-model:value="dateRange"
                  format="DD.MM.YYYY"
                  style="width: 240px"
                  allow-clear
                  placeholder="['З дати', 'По дату']"
                />
                <a-button
                  type="danger"
                  :disabled="!selectedRecords.length"
                  @click="deleteSelectedRecords"
                  style="margin-left: auto;"
                >
                  <DeleteOutlined /> {{ selectedRecords.length }}
                </a-button>
              </div>

              <div class="tab-scroll-area">
                <a-empty v-if="filteredRecords.length === 0" description="Записів не знайдено" />
                
                <a-timeline v-else class="medical-timeline">
                  <a-timeline-item 
                    v-for="record in filteredRecords" 
                    :key="record.id"
                    :color="getRecordColor(record.type)"
                  >
                    <div class="timeline-record-card">
                      <div class="record-card-top">
                        <a-checkbox
                          :checked="selectedRecords.includes(record.id)"
                          @change="toggleRecordSelection(record.id)"
                        />
                        <div class="record-header">
                          <span class="record-date">{{ formatDate(record.record_date) }}</span>
                          <a-tag :color="getRecordColor(record.type)">{{ record.type }}</a-tag>
                        </div>
                      </div>
                      <div class="record-notes">
                        {{ record.notes || 'Без додаткових нотаток.' }}
                      </div>
                    </div>
                  </a-timeline-item>
                </a-timeline>
              </div>

            </div>
          </a-tab-pane>

          <a-tab-pane key="documents" tab="📁 Аналізи та документи">
            <div class="tab-scroll-area empty-tab-state">
              <FolderOpenOutlined style="font-size: 48px; color: var(--color-muted); margin-bottom: 16px;" />
              <h4>Документи відсутні</h4>
              <p>Тут зберігатимуться результати лабораторних аналізів та рентгенівські знімки пацієнта.</p>
              <a-button type="dashed">Завантажити файл</a-button>
            </div>
          </a-tab-pane>

        </a-tabs>
      </div>
    </div>

    <a-modal
      v-model:open="isAddModalOpen"
      title="Новий медичний запис"
      ok-text="Зберегти"
      cancel-text="Скасувати"
      @ok="saveRecord"
      @cancel="closeAddForm"
    >
      <a-form layout="vertical">
        <a-form-item label="Дата запису" required>
          <a-date-picker 
            v-model:value="newRecord.date" 
            format="DD.MM.YYYY" 
            style="width: 100%" 
          />
        </a-form-item>
        
        <a-form-item label="Тип процедури" required>
          <a-select v-model:value="newRecord.type" placeholder="Оберіть тип">
            <a-select-option value="Огляд">🩺 Огляд</a-select-option>
            <a-select-option value="Вакцинація">💉 Вакцинація</a-select-option>
            <a-select-option value="Операція">✂️ Операція</a-select-option>
            <a-select-option value="Аналізи">🧪 Аналізи</a-select-option>
            <a-select-option value="Лікування">💊 Лікування</a-select-option>
            <a-select-option value="Інше">📋 Інше...</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="Висновки лікаря (нотатки)">
          <a-textarea 
            v-model:value="newRecord.notes" 
            :rows="4" 
            placeholder="Опишіть стан тварини, діагноз або призначення..." 
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </a-modal>
</template>

<script setup>
import { ref, computed } from 'vue';
import { animalApi } from '@/api';
import dayjs from 'dayjs';
import isBetween from 'dayjs/plugin/isBetween';
import { message } from 'ant-design-vue';
import { PictureOutlined, PlusOutlined, FolderOpenOutlined, DownOutlined, DeleteOutlined } from '@ant-design/icons-vue';

dayjs.extend(isBetween);

const props = defineProps({
  open: Boolean,
  animal: Object,
  records: Array
});

const emit = defineEmits(['update:open', 'refresh']);

const activeTab = ref('history');
const isAddModalOpen = ref(false);
const selectedRecords = ref([]);

const searchQuery = ref('');
const dateRange = ref(null);

const newRecord = ref({
  date: dayjs(),
  type: 'Огляд',
  notes: ''
});

const filteredRecords = computed(() => {
  if (!props.animal || !props.records) return [];
  
  let result = props.records.filter(r => r.animal_id == props.animal.id);

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(r => 
      (r.type && r.type.toLowerCase().includes(query)) || 
      (r.notes && r.notes.toLowerCase().includes(query))
    );
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = dateRange.value[0].startOf('day');
    const endDate = dateRange.value[1].endOf('day');
    
    result = result.filter(r => {
      const recDate = dayjs(r.record_date);
      return recDate.isBetween(startDate, endDate, 'day', '[]'); 
    });
  }

  return result.sort((a, b) => new Date(b.record_date) - new Date(a.record_date));
});

const getStatusColorClass = (status) => {
  const map = {
    'Здоровий': 'status-green',
    'На лікуванні': 'status-yellow',
    'Критичний': 'status-red',
    'Карантин': 'status-blue'
  };
  return map[status] || 'status-green';
};

const updateHealthStatus = async (newStatus) => {
  try {
    const payload = {
      name: props.animal.name,
      age: props.animal.age,
      species: props.animal.species,
      description: props.animal.description,
      photo_url: props.animal.photo_url,
      health_status: newStatus
    };

    await animalApi.updateAnimal(props.animal.id, payload);
    message.success(`Статус змінено на: ${newStatus}`);
    emit('refresh'); 
  } catch (error) {
    message.error('Помилка оновлення статусу');
    console.error(error);
  }
};

const getRecordColor = (type) => {
  const colors = {
    'Вакцинація': 'green',
    'Операція': 'red',
    'Аналізи': 'purple',
    'Лікування': 'orange',
    'Огляд': 'blue'
  };
  return colors[type] || 'blue';
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  return dayjs(dateString).format('DD.MM.YYYY');
};

const closeModal = () => {
  emit('update:open', false);
};

const openAddForm = () => {
  newRecord.value = { date: dayjs(), type: 'Огляд', notes: '' };
  isAddModalOpen.value = true;
};

const closeAddForm = () => {
  isAddModalOpen.value = false;
};

const saveRecord = async () => {
  if (!newRecord.value.date || !newRecord.value.type) {
    return message.warning('Будь ласка, вкажіть дату та тип запису');
  }
  try {
    const payload = {
      animal_id: props.animal.id,
      record_date: newRecord.value.date.format('YYYY-MM-DD'),
      type: newRecord.value.type,
      notes: newRecord.value.notes
    };
    await animalApi.createMedCard(payload);
    message.success('Медичний запис успішно додано!');
    emit('refresh');
    isAddModalOpen.value = false;
  } catch (e) {
    console.error(e);
    message.error('Помилка при збереженні запису');
  }
};

const toggleRecordSelection = (recordId) => {
  if (selectedRecords.value.includes(recordId)) {
    selectedRecords.value = selectedRecords.value.filter(id => id !== recordId);
  } else {
    selectedRecords.value = [...selectedRecords.value, recordId];
  }
};

const deleteSelectedRecords = async () => {
  if (!selectedRecords.value.length) return;
  try {
    await Promise.all(selectedRecords.value.map(id => animalApi.deleteMedCard(id)));
    message.success('Обрані записи видалено');
    selectedRecords.value = [];
    emit('refresh');
  } catch (error) {
    console.error(error);
    message.error('Помилка видалення обраних записів');
  }
};
</script>

<style scoped>
:deep(.ant-modal-content) {
  padding: 0;
  overflow: hidden;
  border-radius: 16px;
  background: var(--color-card-background) !important;
  color: var(--color-text) !important;
}

:deep(.ant-modal-header) {
  padding: 16px 24px;
  margin-bottom: 0;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-heading);
}

:deep(.ant-modal-title) {
  color: var(--color-heading) !important;
}

.medical-profile-layout {
  display: flex;
  height: 600px;
  background: var(--color-card-background);
}

/* --- ЛІВА ПАНЕЛЬ --- */
.left-sidebar {
  width: 280px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.profile-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: auto;
}

.avatar-wrapper {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid var(--color-card-background);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
  margin-bottom: 16px;
  background: var(--color-surface);
}

.avatar-wrapper img {
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
  font-size: 48px;
  color: var(--color-muted);
}

.patient-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-heading);
  margin-bottom: 8px;
  text-align: center;
}

.patient-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.health-status-wrapper {
  width: 100%;
}

.status-select {
  width: 100%;
  border-radius: 20px;
  font-weight: 600;
  border: 1px solid var(--color-border);
}

:deep(.status-green .ant-select-selector) { background-color: var(--bg-success) !important; color: var(--color-success) !important; }
:deep(.status-yellow .ant-select-selector) { background-color: var(--bg-warning) !important; color: var(--color-warning) !important; }
:deep(.status-red .ant-select-selector) { background-color: var(--bg-danger) !important; color: var(--color-danger) !important; }
:deep(.status-blue .ant-select-selector) { background-color: var(--bg-info) !important; color: var(--accent-primary) !important; }

.add-btn {
  margin-top: 24px;
  font-weight: 600;
  border-radius: 8px;
}

/* --- ПРАВА ПАНЕЛЬ --- */
.right-content {
  flex: 1;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.ant-tabs) {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: transparent;
}

:deep(.ant-tabs-content) {
  flex: 1;
  overflow: hidden;
}

.timeline-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.timeline-filters {
  display: flex;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 16px;
}

/* МАГІЯ СКРОЛУ */
.tab-scroll-area {
  flex: 1;
  max-height: 420px;
  overflow-y: auto;
  padding-right: 12px;
  padding-bottom: 24px;
}

.tab-scroll-area::-webkit-scrollbar { width: 6px; }
.tab-scroll-area::-webkit-scrollbar-thumb { background: var(--color-muted); border-radius: 6px; }

/* Дизайн запису в таймлайні */
.medical-timeline {
  margin-top: 10px;
}

.timeline-record-card {
  background: var(--color-card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
  margin-bottom: 16px;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  border-bottom: 1px dashed var(--color-border);
  padding-bottom: 8px;
}

.record-card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 12px;
}

.record-card-top .record-header {
  flex: 1;
}

.record-date {
  font-weight: 600;
  color: var(--color-muted);
  font-size: 14px;
}

.record-notes {
  color: var(--color-text);
  line-height: 1.6;
  white-space: pre-wrap;
}

.empty-tab-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: var(--color-muted);
  height: 100%;
}

.empty-tab-state h4 {
  color: var(--color-heading);
  font-weight: 600;
  margin-bottom: 8px;
}
</style>