<template>
  <div class="hotel-content">
    <div class="header-actions">
      <div>
        <h2 style="margin: 0; font-weight: 700; color: var(--color-heading);">📅 Завдання готелю</h2>
        <p style="margin: 8px 0 0; color: var(--color-muted);">Календар та список задач за днями</p>
      </div>

      <div style="display: flex; gap: 12px; align-items: center;">
        <a-segmented
          v-model:value="viewMode"
          :options="[
            { title: 'Календар', value: 'calendar' },
            { title: 'Список', value: 'list' },
            { title: 'Заявки 📋', value: 'requests' }
          ]"
          block
        >
          <template #label="{ value }">
            <AppstoreOutlined v-if="value === 'calendar'" style="font-size: 16px;" />
            <TableOutlined v-else-if="value === 'list'" style="font-size: 16px;" />
            <span v-else style="font-size: 14px;">📋</span>
          </template>
        </a-segmented>

        <a-button v-if="viewMode !== 'requests'" type="primary" shape="round" size="large" @click="openNewTaskModal">
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
                  <span v-if="item.pet_name">🏨 {{ item.pet_name }}</span>
                </div>
              </div>
            </div>

            <a-space size="small">
              <a-popconfirm
                v-if="item.recurrence_group_id"
                title="Скасувати повторення серії, починаючи з цього дня?"
                @confirm="cancelRecurrence(item)"
                ok-text="Так"
                cancel-text="Ні"
              >
                <a-button type="text" style="color: var(--color-warning);" size="small">
                  <SyncOutlined /> Скасувати серію
                </a-button>
              </a-popconfirm>

              <a-button type="text" style="color: var(--accent-primary);" size="small" @click="openEditTaskModal(item)">
                <EditOutlined />
              </a-button>
              <a-popconfirm title="Видалити це завдання?" @confirm="deleteTask(item.id)">
                <a-button type="text" danger size="small"><DeleteOutlined /></a-button>
              </a-popconfirm>
            </a-space>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <a-drawer
      v-model:open="isDrawerOpen"
      :title="`Завдання на ${selectedDateFormatted}`"
      placement="right"
      width="450"
      @close="isDrawerOpen = false"
    >
      <div v-if="selectedDayTasks.length === 0" class="empty-state">
        <div style="font-size: 40px; margin-bottom: 16px;">☕</div>
        <p>На цей день завдань немає.</p>
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
                  <span v-if="item.pet_name" style="margin-left: 8px;">🏨 {{ item.pet_name }}</span>
                </div>
              </div>
              <a-space size="small" direction="vertical" style="align-items: flex-end;">
                <div style="display: flex; gap: 4px;">
                  <a-popconfirm v-if="item.recurrence_group_id" title="Скасувати повтори з цього дня?" @confirm="cancelRecurrence(item)">
                    <a-button type="text" size="small" style="color: var(--color-warning);"><SyncOutlined /></a-button>
                  </a-popconfirm>
                  <a-button type="text" size="small" style="color: var(--accent-primary);" @click="openEditTaskModal(item)"><EditOutlined /></a-button>
                  <a-popconfirm title="Видалити?" @confirm="deleteTask(item.id)">
                    <a-button type="text" danger size="small"><DeleteOutlined /></a-button>
                  </a-popconfirm>
                </div>
              </a-space>
            </div>
          </a-list-item>
        </template>
      </a-list>
    </a-drawer>

    <!-- Раздел для управління заявками на бронювання -->
    <div v-if="viewMode === 'requests'" class="booking-requests-container">
      <a-empty v-if="bookingRequests.length === 0" description="Заявок на бронювання немає" />

      <a-list v-else item-layout="vertical" :data-source="bookingRequests">
        <template #renderItem="{ item }">
          <a-list-item class="request-item" :class="'status-' + item.status">
            <div style="display: flex; justify-content: space-between; width: 100%; gap: 16px;">
              <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                  <h3 style="margin: 0; font-size: 1.1rem; color: var(--color-heading);">
                    {{ item.pet_name }} ({{ item.species }})
                  </h3>
                  <a-tag 
                    :color="item.status === 'pending' ? 'blue' : item.status === 'approved' ? 'green' : 'red'"
                  >
                    {{ item.status === 'pending' ? 'Очікує' : item.status === 'approved' ? 'Одобрена' : 'Відхилена' }}
                  </a-tag>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
                  <div>
                    <span style="color: var(--color-muted); font-size: 0.85rem;">Власник</span>
                    <p style="margin: 4px 0 0; font-weight: 600;">{{ item.owner_name }}</p>
                  </div>
                  <div>
                    <span style="color: var(--color-muted); font-size: 0.85rem;">Телефон</span>
                    <p style="margin: 4px 0 0; font-weight: 600;">{{ item.owner_phone }}</p>
                  </div>
                  <div>
                    <span style="color: var(--color-muted); font-size: 0.85rem;">Дати</span>
                    <p style="margin: 4px 0 0; font-weight: 600;">{{ formatDate(item.start_date) }} - {{ formatDate(item.end_date) }}</p>
                  </div>
                  <div>
                    <span style="color: var(--color-muted); font-size: 0.85rem;">Вольєр №</span>
                    <p style="margin: 4px 0 0; font-weight: 600;">{{ aviaryMap[item.aviary_id]?.number || item.aviary_id }}</p>
                  </div>
                </div>

                <div v-if="item.description" style="margin-bottom: 12px;">
                  <span style="color: var(--color-muted); font-size: 0.85rem;">Опис</span>
                  <p style="margin: 4px 0 0; color: var(--color-text);">{{ item.description }}</p>
                </div>

                <div style="display: flex; gap: 12px; align-items: center;">
                  <span style="font-weight: 600; color: var(--accent-primary);">Вартість: {{ item.total_price }} ₴</span>
                  <span style="color: var(--color-muted); font-size: 0.85rem;">{{ formatDateTime(item.created_at) }}</span>
                </div>
              </div>

              <div v-if="item.status === 'pending'" style="display: flex; flex-direction: column; gap: 8px; min-width: 140px;">
                <a-button 
                  type="primary" 
                  style="background: #2563eb; border-color: #2563eb;"
                  @click="openEditRequestModal(item)"
                  size="small"
                >
                  ✎ Редагувати
                </a-button>
                <a-button 
                  type="primary" 
                  style="background: #16a34a; border-color: #16a34a;"
                  @click="approveRequest(item.id)"
                  :loading="approvingId === item.id"
                >
                  ✓ Одобрити
                </a-button>
                <a-button 
                  danger 
                  @click="rejectRequest(item.id)"
                  :loading="rejectingId === item.id"
                >
                  ✕ Відхилити
                </a-button>
              </div>
            </div>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <a-modal
      v-model:open="isEditingRequest"
      title="Редагування заявки на бронювання"
      ok-text="Зберегти"
      cancel-text="Скасувати"
      @ok="submitEditRequest"
      :confirm-loading="isSubmittingRequest"
      width="700px"
    >
      <a-form layout="vertical" v-if="editingRequestData">
        <a-divider orientation="left">Клієнт та Тварина</a-divider>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="Номер телефону власника" required>
              <a-input v-model:value="editingRequestData.owner_phone" placeholder="+380..." />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="ПІБ власника" required>
              <a-input v-model:value="editingRequestData.owner_name" placeholder="Олена Петрівна" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="Ім'я тварини" required>
              <a-input v-model:value="editingRequestData.pet_name" placeholder="Мурзік" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="Вид / Порода" required>
              <a-input v-model:value="editingRequestData.species" placeholder="Кіт (Мейн-кун)" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="Особливості">
          <a-textarea v-model:value="editingRequestData.description" placeholder="Розкажіть про тварину" />
        </a-form-item>

        <a-divider orientation="left">Проживання</a-divider>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="Дата прибуття" required>
              <a-date-picker 
                v-model:value="editingRequestDates[0]"
                format="YYYY-MM-DD"
                style="width: 100%"
                @change="handleEditRequestDateChange"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="Дата вибуття" required>
              <a-date-picker 
                v-model:value="editingRequestDates[1]"
                format="YYYY-MM-DD"
                style="width: 100%"
                @change="handleEditRequestDateChange"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="Вольєр" required>
          <a-select 
            v-model:value="editingRequestData.aviary_id" 
            placeholder="Спочатку оберіть дати"
            :disabled="editingRequestAvailableAviaries.length === 0"
          >
            <a-select-option v-for="aviary in editingRequestAvailableAviaries" :key="aviary.id" :value="aviary.id">
              Вольєр №{{ aviary.number }} ({{ aviary.category }}) - {{ aviary.daily_price }} ₴/доба
            </a-select-option>
          </a-select>
        </a-form-item>

        <div style="background: #eff6ff; padding: 16px; border-radius: 8px; border: 1px solid #bfdbfe;">
          <p style="margin: 0; font-weight: 600; color: #1e40af;">
            Нова вартість: {{ editingRequestData.total_price }} ₴
          </p>
        </div>
      </a-form>
    </a-modal>

    <a-modal
      @cancel="closeModal"
    >
      <a-form layout="vertical">
        <a-form-item label="Назва" required>
          <a-input v-model:value="taskForm.title" placeholder="Опис завдання" />
        </a-form-item>

        <a-form-item label="Дата та час" required>
          <a-date-picker
            v-model:value="newTaskDatetime"
            show-time
            format="DD.MM.YYYY HH:mm"
            @change="onDatetimeChange"
            placeholder="Оберіть дату та час"
            style="width: 100%;"
          />
        </a-form-item>

        <div v-if="!editingTask" style="background: var(--color-surface); padding: 12px; border-radius: 8px; margin-bottom: 24px; border: 1px solid var(--color-border);">
          <a-form-item style="margin-bottom: 8px;">
            <a-checkbox v-model:checked="isRecurring">Повторювати це завдання</a-checkbox>
          </a-form-item>
          <a-form-item v-if="isRecurring" label="Тривалість курсу повторення (днів)" required style="margin-bottom: 0;">
            <a-input-number v-model:value="taskForm.repeat_days" :min="2" :max="90" style="width: 100%;" />
          </a-form-item>
        </div>

        <a-form-item label="Бронювання">
          <a-select
            v-model:value="taskForm.booking_id"
            placeholder="Оберіть бронювання"
            allow-clear
          >
            <a-select-option
              v-for="booking in bookings"
              :key="booking.id"
              :value="booking.id"
            >
              {{ `#${booking.id} ${booking.pet_name ? booking.pet_name : ''}` }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="Опис">
          <a-textarea v-model:value="taskForm.description" rows="4" placeholder="Додатковий опис завдання" />
        </a-form-item>

        <a-form-item label="Статус виконання">
          <a-switch v-model:checked="taskForm.is_completed" />
          <span style="margin-left: 12px;">{{ taskForm.is_completed ? 'Виконано' : 'Не виконано' }}</span>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SyncOutlined,
  AppstoreOutlined,
  TableOutlined,
  LeftOutlined,
  RightOutlined,
  ClockCircleOutlined
} from '@ant-design/icons-vue';
import dayjs from 'dayjs';
import { message } from 'ant-design-vue';
import { bookingApi } from '@/api';

const viewMode = ref('calendar');
const currentDate = ref(dayjs());
const listViewDate = ref(dayjs());
const isDrawerOpen = ref(false);
const selectedDateString = ref(dayjs().format('YYYY-MM-DD'));
const tasks = ref([]);
const bookings = ref([]);
const bookingRequests = ref([]);
const aviaryMap = ref({});
const approvingId = ref(null);
const rejectingId = ref(null);
const isModalOpen = ref(false);
const editingTask = ref(null);
const isRecurring = ref(false);
const newTaskDatetime = ref(null);

// Редагування заявок
const isEditingRequest = ref(false);
const isSubmittingRequest = ref(false);
const editingRequestData = ref(null);
const editingRequestDates = ref([null, null]);
const editingRequestAvailableAviaries = ref([]);

const taskForm = ref({
  title: '',
  date_time: '',
  booking_id: null,
  description: '',
  is_completed: false,
  repeat_days: 7
});

const columns = [
  { title: 'ID', dataIndex: 'id', width: 70 },
  { title: 'Заголовок', dataIndex: 'title' },
  { title: 'Дата та час', key: 'date_time' },
  { title: 'Бронювання', key: 'booking' },
  { title: 'Статус', key: 'status', width: 140 },
  { title: 'Дії', key: 'actions', width: 280 }
];

const fetchTasks = async () => {
  try {
    const res = await bookingApi.getHotelTasks();
    tasks.value = res.data;
  } catch (error) {
    console.error(error);
    message.error('Не вдалося завантажити завдання');
  }
};

const fetchBookings = async () => {
  try {
    const res = await bookingApi.getAll();
    bookings.value = res.data.map((item) => ({
      ...item,
      pet_name: item.pet_name || ''
    }));
  } catch (error) {
    console.error(error);
  }
};

const fetchBookingRequests = async () => {
  try {
    const res = await bookingApi.getBookingRequests();
    bookingRequests.value = res.data;
  } catch (error) {
    console.error(error);
    message.error('Не вдалося завантажити заявки на бронювання');
  }
};

const fetchAviaries = async () => {
  try {
    const res = await bookingApi.getAviaries();
    aviaryMap.value = {};
    res.data.forEach(aviary => {
      aviaryMap.value[aviary.id] = aviary;
    });
  } catch (error) {
    console.error(error);
  }
};

const approveRequest = async (id) => {
  approvingId.value = id;
  try {
    await bookingApi.approveBookingRequest(id);
    message.success('Заявку одобрено! Бронювання створено.');
    await fetchBookingRequests();
    await fetchBookings();
  } catch (error) {
    console.error(error);
    message.error(error.response?.data?.detail || 'Помилка при одобренні заявки');
  } finally {
    approvingId.value = null;
  }
};

const rejectRequest = async (id) => {
  rejectingId.value = id;
  try {
    await bookingApi.rejectBookingRequest(id);
    message.success('Заявку відхилено.');
    await fetchBookingRequests();
  } catch (error) {
    console.error(error);
    message.error(error.response?.data?.detail || 'Помилка при відхиленні заявки');
  } finally {
    rejectingId.value = null;
  }
};

const formattedListViewDate = computed(() => listViewDate.value.format('DD.MM.YYYY'));
const selectedDateFormatted = computed(() => dayjs(selectedDateString.value).format('DD.MM.YYYY'));

const todayTasksList = computed(() => {
  const targetDate = listViewDate.value.format('YYYY-MM-DD');
  return tasks.value
    .filter((task) => dayjs(task.date_time).format('YYYY-MM-DD') === targetDate)
    .sort((a, b) => {
      if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1;
      return new Date(a.date_time) - new Date(b.date_time);
    });
});

const selectedDayTasks = computed(() => {
  return tasks.value
    .filter((task) => dayjs(task.date_time).format('YYYY-MM-DD') === selectedDateString.value)
    .sort((a, b) => {
      if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1;
      return new Date(a.date_time) - new Date(b.date_time);
    });
});

const getTasksForDate = (date) => {
  const targetDate = date.format('YYYY-MM-DD');
  return tasks.value
    .filter((task) => dayjs(task.date_time).format('YYYY-MM-DD') === targetDate)
    .sort((a, b) => {
      if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1;
      return new Date(a.date_time) - new Date(b.date_time);
    });
};

const goToPreviousDay = () => { listViewDate.value = listViewDate.value.subtract(1, 'day'); };
const goToNextDay = () => { listViewDate.value = listViewDate.value.add(1, 'day'); };

const onSelectDate = (value) => {
  selectedDateString.value = value.format('YYYY-MM-DD');
  isDrawerOpen.value = true;
};

const resetForm = () => {
  taskForm.value = {
    title: '',
    date_time: '',
    booking_id: null,
    description: '',
    is_completed: false,
    repeat_days: 7
  };
  isRecurring.value = false;
  newTaskDatetime.value = null;
};

const openNewTaskModal = () => {
  editingTask.value = null;
  resetForm();
  isModalOpen.value = true;
};

const openEditTaskModal = (task) => {
  editingTask.value = task;
  taskForm.value = {
    title: task.title,
    date_time: task.date_time,
    booking_id: task.booking_id,
    description: task.description || '',
    is_completed: task.is_completed || false,
    repeat_days: 7
  };
  isRecurring.value = false;
  newTaskDatetime.value = task.date_time ? dayjs(task.date_time) : null;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const onDatetimeChange = (value) => {
  if (value) {
    taskForm.value.date_time = value.format('YYYY-MM-DDTHH:mm:ss');
  }
};

const toggleTaskStatus = async (task) => {
  try {
    await bookingApi.updateHotelTask(task.id, { is_completed: task.is_completed });
    message.success(task.is_completed ? 'Завдання виконано!' : 'Повернуто в роботу');
  } catch (error) {
    task.is_completed = !task.is_completed;
    message.error('Помилка оновлення статусу');
  }
};

const submitTask = async () => {
  if (!taskForm.value.title || !taskForm.value.date_time) {
    message.error('Заповніть назву та дату');
    return;
  }

  const payload = {
    title: taskForm.value.title,
    date_time: taskForm.value.date_time,
    booking_id: taskForm.value.booking_id,
    description: taskForm.value.description,
    is_completed: taskForm.value.is_completed,
    repeat_days: isRecurring.value ? taskForm.value.repeat_days : null
  };

  try {
    if (editingTask.value) {
      await bookingApi.updateHotelTask(editingTask.value.id, payload);
      message.success('Завдання оновлено');
    } else {
      await bookingApi.createHotelTask(payload);
      message.success(isRecurring.value ? 'Серію повторюваних завдань створено!' : 'Завдання створено');
    }
    isModalOpen.value = false;
    await fetchTasks();
  } catch (error) {
    console.error(error);
    message.error('Не вдалося зберегти завдання');
  }
};

const deleteTask = async (id) => {
  try {
    await bookingApi.deleteHotelTask(id);
    message.success('Завдання видалено');
    await fetchTasks();
  } catch (error) {
    console.error(error);
    message.error('Не вдалося видалити завдання');
  }
};

const cancelRecurrence = async (task) => {
  try {
    await bookingApi.deleteHotelTaskRecurrence(task.id);
    message.success('Наступні повторення серії скасовано');
    await fetchTasks();
  } catch (error) {
    console.error(error);
    message.error('Не вдалося скасувати серію повторень');
  }
};

const formatTime = (value) => {
  return value ? dayjs(value).format('HH:mm') : '-';
};

const formatDate = (value) => {
  return value ? dayjs(value).format('DD.MM.YYYY') : '-';
};

const formatDateTime = (value) => {
  return value ? dayjs(value).format('DD.MM.YYYY HH:mm') : '-';
};

// Функції для редагування заявок
const openEditRequestModal = (request) => {
  editingRequestData.value = { ...request };
  editingRequestDates.value = [
    dayjs(request.start_date),
    dayjs(request.end_date)
  ];
  editingRequestAvailableAviaries.value = [];
  isEditingRequest.value = true;
};

const handleEditRequestDateChange = async () => {
  if (!editingRequestDates.value[0] || !editingRequestDates.value[1]) {
    editingRequestAvailableAviaries.value = [];
    return;
  }

  const startStr = editingRequestDates.value[0].format('YYYY-MM-DD');
  const endStr = editingRequestDates.value[1].format('YYYY-MM-DD');

  try {
    const res = await bookingApi.getAvailableAviaries(startStr, endStr);
    editingRequestAvailableAviaries.value = res.data;
    
    // Перевіряємо чи обраний вольєр все ще доступний
    if (!res.data.find(a => a.id === editingRequestData.value.aviary_id)) {
      editingRequestData.value.aviary_id = null;
    }
    
    // Перераховуємо вартість
    calculateEditingRequestPrice();
  } catch (error) {
    console.error(error);
    message.error('Не вдалося завантажити вільні вольєри');
  }
};

const calculateEditingRequestPrice = () => {
  if (!editingRequestDates.value[0] || !editingRequestDates.value[1] || !editingRequestData.value.aviary_id) {
    editingRequestData.value.total_price = 0;
    return;
  }

  const start = editingRequestDates.value[0];
  const end = editingRequestDates.value[1];
  let days = end.diff(start, 'day');
  if (days <= 0) days = 1;

  const aviary = editingRequestAvailableAviaries.value.find(a => a.id === editingRequestData.value.aviary_id);
  if (aviary) {
    editingRequestData.value.total_price = aviary.daily_price * days;
  }
};

const submitEditRequest = async () => {
  if (!editingRequestData.value.owner_phone || !editingRequestData.value.owner_name || 
      !editingRequestData.value.pet_name || !editingRequestData.value.aviary_id) {
    message.error('Заповніть усі обов\'язкові поля');
    return;
  }

  isSubmittingRequest.value = true;
  try {
    await bookingApi.updateBookingRequest(editingRequestData.value.id, {
      pet_name: editingRequestData.value.pet_name,
      species: editingRequestData.value.species,
      owner_name: editingRequestData.value.owner_name,
      owner_phone: editingRequestData.value.owner_phone,
      description: editingRequestData.value.description,
      aviary_id: editingRequestData.value.aviary_id,
      start_date: editingRequestDates.value[0].format('YYYY-MM-DD'),
      end_date: editingRequestDates.value[1].format('YYYY-MM-DD'),
      service_ids: []
    });
    
    message.success('Заявку оновлено!');
    isEditingRequest.value = false;
    await fetchBookingRequests();
  } catch (error) {
    console.error(error);
    message.error(error.response?.data?.detail || 'Помилка при обновленні заявки');
  } finally {
    isSubmittingRequest.value = false;
  }
};

onMounted(() => {
  fetchTasks();
  fetchBookings();
  fetchBookingRequests();
  fetchAviaries();
});
</script>

<style scoped>
.hotel-content {
  display: flex;
  flex-direction: column;
}

.calendar-container {
  padding: 10px 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.events-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.task-badge {
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 12px;
  margin-bottom: 2px;
}

.completed-text :deep(.ant-badge-status-text) {
  text-decoration: line-through;
  color: var(--color-muted);
}

.more-tasks {
  font-size: 11px;
  color: var(--color-muted);
  font-weight: 600;
  margin-top: 4px;
}

.list-view-container {
  margin-top: 24px;
}

.list-view-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

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
  opacity: 0.75;
}

.task-title {
  font-weight: 600;
  color: var(--color-heading);
  font-size: 14px;
}

.strike-through {
  text-decoration: line-through;
  color: var(--color-muted);
}

.drawer-task-item {
  background: var(--color-surface);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
  border: 1px solid var(--color-border);
}

.drawer-task-item.is-done {
  opacity: 0.75;
}

.task-time-animal {
  font-size: 12px;
  color: var(--color-muted);
  display: flex;
  align-items: center;
}

.empty-state {
  text-align: center;
  color: var(--color-muted);
  margin-top: 80px;
}

.booking-requests-container {
  margin-top: 24px;
}

.request-item {
  background: var(--color-card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: box-shadow 0.2s;
}

.request-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.request-item.status-pending {
  border-left: 4px solid #2563eb;
}

.request-item.status-approved {
  border-left: 4px solid #16a34a;
  opacity: 0.8;
}

.request-item.status-rejected {
  border-left: 4px solid #dc2626;
  opacity: 0.6;
}
</style>
