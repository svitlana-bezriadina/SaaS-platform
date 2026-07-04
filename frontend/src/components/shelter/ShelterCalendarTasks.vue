<template>
  <div class="calendar-container">
    <div class="header-actions">
      <h2 style="margin: 0; font-weight: 700; color: var(--color-heading);">📅 Календар завдань</h2>
      <div style="display: flex; gap: 12px; align-items: center;">
        <a-segmented 
          v-model:value="viewMode" 
          :options="[
            { title: 'Календар', value: 'calendar' },
            { title: 'Список', value: 'list' }
          ]" 
          block
        >
          <template #label="{ value }">
            <AppstoreOutlined v-if="value === 'calendar'" style="font-size: 16px;" />
            <TableOutlined v-else style="font-size: 16px;" />
          </template>
        </a-segmented>
        <a-button type="primary" shape="round" size="large" @click="openAddTaskModal">
          <PlusOutlined /> Додати завдання
        </a-button>
      </div>
    </div>

    <a-card v-if="viewMode === 'calendar'" style="border-radius: 12px; border: 1px solid var(--color-border); box-shadow: var(--color-shadow); background: var(--color-card-background);">
      <a-calendar v-model:value="currentDate" @select="onSelectDate">
        <template #dateCellRender="{ current }">
          <ul class="events-list">
            <li v-for="task in getTasksForDate(current).slice(0, 2)" :key="task.id">
              <a-badge 
                :status="task.is_completed ? 'success' : 'processing'" 
                :text="task.title" 
                class="task-badge"
                :class="{ 'completed-text': task.is_completed }"
              />
            </li>
            <li v-if="getTasksForDate(current).length > 2" class="more-tasks">
              + ще {{ getTasksForDate(current).length - 2 }}
            </li>
          </ul>
        </template>
      </a-calendar>
    </a-card>

    <div v-else class="list-view-container">
      <div class="list-view-navigation" style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 24px;">
        <a-button @click="goToPreviousDay"><LeftOutlined /></a-button>
        <span style="font-size: 18px; font-weight: 700; color: var(--color-heading); min-width: 150px; text-align: center;">
          {{ formattedListViewDate }}
        </span>
        <a-button @click="goToNextDay"><RightOutlined /></a-button>
      </div>

      <a-empty v-if="todayTasksList.length === 0" description="На цей день завдань немає" />
      
      <a-list v-else item-layout="horizontal" :data-source="todayTasksList">
        <template #renderItem="{ item }">
          <a-list-item class="task-item-row" :class="{ 'is-done': item.is_completed }">
            <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
              <a-checkbox 
                v-model:checked="item.is_completed" 
                @change="toggleTaskStatus(item)"
              />
              <div>
                <div class="task-title" :class="{ 'strike-through': item.is_completed }">
                  {{ item.title }}
                </div>
                <div class="task-subinfo" style="font-size: 12px; color: var(--color-muted); display: flex; gap: 12px; margin-top: 2px;">
                  <span><ClockCircleOutlined /> {{ formatTime(item.date_time) }}</span>
                  <span v-if="item.animal_name">🐾 {{ item.animal_name }}</span>
                </div>
              </div>
            </div>

            <a-space size="small">
              <a-popconfirm 
                v-if="item.recurrence_group_id"
                title="Скасувати повторення серії, починаючи з цього дня?" 
                @confirm="cancelRecurrenceFromDay(item)"
                ok-text="Так" cancel-text="Ні"
              >
                <a-button type="text" style="color: var(--color-warning);" v-if="authStore.role === 'admin'" size="small" title="Вимкнути повтори з цього дня">
                  <SyncOutlined /> Скасувати повтори
                </a-button>
              </a-popconfirm>

              <a-button type="text" style="color: var(--accent-primary);" size="small" @click="openEditTaskModal(item)">
                <EditOutlined />
              </a-button>
              <a-popconfirm title="Видалити це завдання?" @confirm="deleteTask(item.id)">
                <a-button type="text" danger size="small" v-if="authStore.role === 'admin'"><DeleteOutlined /></a-button>
              </a-popconfirm>
            </a-space>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <a-drawer
      v-model:open="isDrawerOpen"
      :title="`Завдання на ${selectedDateFormatted}`"`
      placement="right"
      width="450"
      @close="isDrawerOpen = false"
    >
      <div v-if="selectedDayTasks.length === 0" class="empty-state">
        <div style="font-size: 40px; margin-bottom: 16px;">☕</div>
        <p>На цей день завдань немає. Можна відпочити!</p>
      </div>

      <a-list v-else item-layout="horizontal" :data-source="selectedDayTasks">
        <template #renderItem="{ item }">
          <a-list-item class="drawer-task-item" :class="{ 'is-done': item.is_completed }">
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%;">
              <a-checkbox 
                v-model:checked="item.is_completed" 
                @change="toggleTaskStatus(item)"
                style="margin-top: 4px;"
              />
              
              <div style="flex: 1;">
                <div class="task-title" :class="{ 'strike-through': item.is_completed }">
                  {{ item.title }}
                </div>
                <div class="task-time-animal">
                  <ClockCircleOutlined style="margin-right: 4px;" /> 
                  {{ formatTime(item.date_time) }}
                  <span v-if="item.animal_name" style="margin-left: 8px;">
                    🐾 {{ item.animal_name }}
                  </span>
                </div>
              </div>

              <a-space size="small" direction="vertical"  style="align-items: flex-end;">
                <div style="display: flex; gap: 4px;">
                  <a-popconfirm v-if="item.recurrence_group_id" title="Скасувати повтори з цього дня?" @confirm="cancelRecurrenceFromDay(item)">
                    <a-button type="text" size="small" style="color: var(--color-warning);" v-if="authStore.role === 'admin'"><SyncOutlined /></a-button>
                  </a-popconfirm>
                  <a-button type="text" size="small" style="color: var(--accent-primary);" @click="openEditTaskModal(item)"><EditOutlined /></a-button>
                  <a-popconfirm title="Видалити?" @confirm="deleteTask(item.id)">
                    <a-button type="text" danger size="small" v-if="authStore.role === 'admin'"><DeleteOutlined /></a-button>
                  </a-popconfirm>
                </div>
              </a-space>
            </div>
          </a-list-item>
        </template>
      </a-list>
    </a-drawer>

    <a-modal
      v-model:open="isTaskModalOpen"
      :title="editingTaskId ? 'Редагувати завдання' : 'Додати завдання'"
      :ok-text="editingTaskId ? 'Зберегти' : 'Додати'"
      cancel-text="Скасувати"
      @ok="submitTask"
      @cancel="closeTaskModal"
    >
      <a-form layout="vertical">
        <a-form-item label="Назва завдання" required>
          <a-input v-model:value="taskForm.title"/>
        </a-form-item>

        <a-form-item label="Дата та час" required>
          <a-date-picker
            v-model:value="newTaskDatetime"
            show-time
            format="DD.MM.YYYY HH:mm"
            @change="onDatetimeChange"
            placeholder="Виберіть дату та час"
            style="width: 100%;"
          />
        </a-form-item>

        <div v-if="!editingTaskId" style="background: var(--color-surface); padding: 12px; border-radius: 8px; margin-bottom: 24px; border: 1px solid var(--color-border);">
          <a-form-item style="margin-bottom: 8px;">
            <a-checkbox v-model:checked="isRecurring">Повторювати це завдання</a-checkbox>
          </a-form-item>
          
          <a-form-item v-if="isRecurring" label="Тривалість курсу повторення (днів)" required style="margin-bottom: 0;">
            <a-input-number v-model:value="taskForm.repeat_days" :min="2" :max="90" style="width: 100%;" />
          </a-form-item>
        </div>

        <a-form-item label="Тварина">
          <a-select v-model:value="taskForm.animal_id" placeholder="Оберіть тварину" allow-clear>
            <a-select-option v-for="animal in animals" :key="animal.id" :value="animal.id">
              {{ animal.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

import { 
  PlusOutlined, ClockCircleOutlined, DeleteOutlined, 
  EditOutlined, AppstoreOutlined, TableOutlined,
  LeftOutlined, RightOutlined, SyncOutlined
} from '@ant-design/icons-vue';
import dayjs from 'dayjs';
import { message } from 'ant-design-vue';
import { animalApi } from '@/api';
import { useAuthStore } from '../../stores/auth';

// --- СТАН ---
const authStore = useAuthStore();
const viewMode = ref('calendar');
const currentDate = ref(dayjs());
const listViewDate = ref(dayjs()); // Твоя оригінальная змінна для гортання днів
const isDrawerOpen = ref(false);
const isTaskModalOpen = ref(false);
const editingTaskId = ref(null);
const isRecurring = ref(false);
const tasks = ref([]);
const animals = ref([]);
const selectedDateString = ref(dayjs().format('YYYY-MM-DD'));

// Форма
const taskForm = ref({ title: '', date_time: '', animal_id: null, repeat_days: 7 });
const newTaskDatetime = ref(null);

// --- ЗАВАНТАЖЕННЯ ДАНИХ ---
const fetchTasks = async () => {
  try {
    const res = await animalApi.getAllTasks();
    
    if (Array.isArray(res.data)) {
        tasks.value = res.data;
    } else {
        console.warn("Бекенд повернув не масив:", res.data);
        tasks.value = [];
    }
  } catch (error) {
    console.error("Помилка завантаження завдань:", error);
    tasks.value = [];
  }
};

const fetchAnimals = async () => {
  try {
    const res = await animalApi.getAllAnimal();
    animals.value = res.data;
  } catch (error) {
    console.error(error);
  }
};

onMounted(() => {
  fetchTasks();
  fetchAnimals();
});

// --- ТВОЯ ОРИГІНАЛЬНА НАВІГАЦІЯ СПИСКУ ---
const formattedListViewDate = computed(() => listViewDate.value.format('DD.MM.YYYY'));

const goToPreviousDay = () => { listViewDate.value = listViewDate.value.subtract(1, 'day'); };
const goToNextDay = () => { listViewDate.value = listViewDate.value.add(1, 'day'); };

// Фільтруємо таски чітко на ОДИН обраний день на екрані
const todayTasksList = computed(() => {
  const targetDate = listViewDate.value.format('YYYY-MM-DD');
  return tasks.value.filter(t => dayjs(t.date_time).format('YYYY-MM-DD') === targetDate)
              .sort((a, b) => {
                if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1;
                return new Date(a.date_time) - new Date(b.date_time);
              });
});

// Фільтрація для клітинок календаря
const getTasksForDate = (date) => {
  const targetDate = date.format('YYYY-MM-DD');
  return tasks.value.filter(t => dayjs(t.date_time).format('YYYY-MM-DD') === targetDate)
              .sort((a, b) => {
                if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1;
                return new Date(a.date_time) - new Date(b.date_time);
              });
};

const onSelectDate = (value) => {
  selectedDateString.value = value.format('YYYY-MM-DD');
  isDrawerOpen.value = true;
};

const selectedDayTasks = computed(() => {
  return tasks.value.filter(t => dayjs(t.date_time).format('YYYY-MM-DD') === selectedDateString.value)
              .sort((a, b) => {
                if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1;
                return new Date(a.date_time) - new Date(b.date_time);
              });
});

// --- ФОРМАТУВАННЯ ---
const selectedDateFormatted = computed(() => dayjs(selectedDateString.value).format('DD.MM.YYYY'));
const formatTime = (dt) => dayjs(dt).format('HH:mm');

// --- РОБОТА З БЕКЕНДОМ ---
const toggleTaskStatus = async (task) => {
  try {
    await animalApi.updateTask(task.id, { is_completed: task.is_completed });
    message.success(task.is_completed ? 'Завдання виконано!' : 'Повернуто в роботу');
  } catch (error) {
    task.is_completed = !task.is_completed;
    message.error('Помилка оновлення статусу');
  }
};

const deleteTask = async (id) => {
  try {
    await animalApi.deleteTask(id);
    tasks.value = tasks.value.filter(t => t.id !== id);
    message.success('Завдання видалено');
  } catch (error) {
    message.error('Помилка видалення');
  }
};

// РОЗУМНЕ СКАСУВАННЯ ПОВТОРІВ З ПОТОЧНОГО ДНЯ
const cancelRecurrenceFromDay = async (task) => {
  try {
    await animalApi.deleteRecurrence(task.id);
    message.success('Наступні повторення серії успішно скасовано, попередні збережено!');
    await fetchTasks(); // Перезавантажуємо таски
    isDrawerOpen.value = false;
  } catch (error) {
    message.error('Не вдалося скасувати серію повторень');
  }
};

// --- ФОРМА ДЛЯ МОДАЛКИ ---
const onDatetimeChange = (date) => {
  if (date) taskForm.value.date_time = date.format('YYYY-MM-DDTHH:mm:ss');
};

const openAddTaskModal = () => {
  editingTaskId.value = null;
  taskForm.value = { title: '', date_time: '', animal_id: null, repeat_days: 7 };
  newTaskDatetime.value = null;
  isRecurring.value = false;
  isTaskModalOpen.value = true;
};

const openEditTaskModal = (task) => {
  editingTaskId.value = task.id;
  taskForm.value = {
    title: task.title,
    date_time: task.date_time,
    animal_id: task.animal_id,
    repeat_days: null
  };
  newTaskDatetime.value = dayjs(task.date_time);
  isTaskModalOpen.value = true;
};

const closeTaskModal = () => {
  isTaskModalOpen.value = false;
  editingTaskId.value = null;
};

const submitTask = async () => {
  if (!taskForm.value.title || !taskForm.value.date_time) {
    return message.error('Заповніть обов\'язкові поля');
  }

  const payload = {
    title: taskForm.value.title,
    date_time: taskForm.value.date_time,
    animal_id: taskForm.value.animal_id,
    repeat_days: isRecurring.value ? taskForm.value.repeat_days : null
  };

  try {
    if (editingTaskId.value) {
      await animalApi.updateTask(editingTaskId.value, payload);
      message.success('Завдання оновлено');
    } else {
      await animalApi.createTask(payload);
      message.success(isRecurring.value ? 'Серію повторюваних завдань створено!' : 'Завдання створено');
    }
    await fetchTasks();
    isTaskModalOpen.value = false;
  } catch (error) {
    message.error('Помилка збереження');
  }
};
</script>

<style scoped>
.calendar-container { padding: 10px 0; }
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.events-list { list-style: none; margin: 0; padding: 0; }
.task-badge { width: 100%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; font-size: 12px; margin-bottom: 2px; }
.completed-text :deep(.ant-badge-status-text) { text-decoration: line-through; color: var(--color-muted); }
.more-tasks { font-size: 11px; color: var(--color-muted); font-weight: 600; margin-top: 4px; }
:deep(.ant-picker-calendar-full .ant-picker-panel) { background: transparent; }
.empty-state { text-align: center; color: var(--color-muted); margin-top: 80px; }

/* Стилі для ТВОГО одноденного списку */
.task-item-row {
  background: var(--color-card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.task-item-row.is-done {
  background: var(--color-card-background);
  opacity: 0.75;
}
.task-title { font-weight: 600; color: var(--color-heading); font-size: 14px; }
.strike-through { text-decoration: line-through; color: var(--color-muted); }
.drawer-task-item { background: var(--color-surface); border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; border: 1px solid var(--color-border); }
.drawer-task-item.is-done { background: var(--color-card-background); opacity: 0.75; }
.task-time-animal { font-size: 12px; color: var(--color-muted); display: flex; align-items: center; }
</style>