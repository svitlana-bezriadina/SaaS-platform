<template>
  <div class="hotel-content">
    <div class="header-actions">
      <div>
        <h2>Управління бронюваннями</h2>
        <p class="header-description">Переглядайте кожне бронювання у вигляді карток, швидко сортуйте за датами і відкривайте повні деталі клієнта.</p>
      </div>

      <a-space align="center" size="middle">
        <a-select v-model:value="statusFilter" style="min-width: 180px; border-radius: 8px;">
          <a-select-option value="all">Усі статуси</a-select-option>
          <a-select-option value="Актуальне">Актуальне</a-select-option>
          <a-select-option value="Завершене">Завершене</a-select-option>
          <a-select-option value="Скасоване">Скасоване</a-select-option>
        </a-select>

        <a-select v-model:value="sortByDate" style="min-width: 220px; border-radius: 8px;">
          <a-select-option value="upcoming">Найближчі заїзди</a-select-option>
          <a-select-option value="oldest">Спочатку старі</a-select-option>
          <a-select-option value="newest">Спочатку нові</a-select-option>
        </a-select>

        <a-button type="primary" size="large" @click="$emit('open-booking-modal')" style="border-radius: 8px;">
          <CalendarOutlined /> Нове бронювання
        </a-button>
      </a-space>
    </div>

    <div class="stats-grid">
      <a-card class="stat-card">
        <div class="stat-label">Всього бронювань</div>
        <div class="stat-value">{{ totalBookings }}</div>
      </a-card>
      <a-card class="stat-card">
        <div class="stat-label">Активні зараз</div>
        <div class="stat-value">{{ activeBookings }}</div>
      </a-card>
      <a-card class="stat-card">
        <div class="stat-label">Найближчі заїзди</div>
        <div class="stat-value">{{ upcomingBookings }}</div>
      </a-card>
    </div>

    <a-row :gutter="[20, 20]">
      <a-col :xs="24" :sm="24" :md="12" :lg="8" v-for="booking in sortedBookings" :key="booking.id">
        <a-card hoverable class="booking-card">
          <template #title>
            <div class="booking-title-row">
              <div>
                <div class="booking-title">Бронювання №{{ booking.id }}</div>
                <div class="booking-subtitle">Вольєр №{{ booking.aviary_id }}</div>
              </div>
              <a-tag :color="statusColor(booking.status)">{{ booking.status }}</a-tag>
            </div>
          </template>

          <div class="booking-card-content">
            <div class="booking-row">
              <span class="label">Період</span>
              <span>{{ formatDate(booking.start_date) }} → {{ formatDate(booking.end_date) }}</span>
            </div>
            <div class="booking-row">
              <span class="label">Тварина</span>
              <span>{{ getPetInfo(booking)?.name || booking.pet_name || `#${booking.pet_id}` }}</span>
            </div>
            <div class="booking-row">
              <span class="label">Власник</span>
              <span>{{ getPetInfo(booking)?.owner_name || 'Невідомо' }}</span>
            </div>
            <div class="booking-row">
              <span class="label">Оплата</span>
              <a-tag :color="paymentColor(booking.payment_status)">{{ booking.payment_status }}</a-tag>
            </div>
            <div class="booking-row">
              <span class="label">Сума</span>
              <strong>{{ booking.total_price }} грн</strong>
            </div>
          </div>

          <div class="booking-actions">
            <a-button type="link" @click="openDetailsModal(booking)">Деталі</a-button>
            <a-popconfirm title="Видалити бронювання?" ok-text="Так" cancel-text="Ні" @confirm="deleteBooking(booking.id)">
              <a-button type="link" danger>Видалити</a-button>
            </a-popconfirm>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <div v-if="sortedBookings.length === 0" class="empty-state">
      Немає бронювань для відображення
    </div>

    <a-modal
      v-model:open="isDetailsModalOpen"
      title="Деталі бронювання"
      ok-text="Зберегти зміни"
      cancel-text="Закрити"
      :confirm-loading="loading"
      @ok="saveBookingChanges"
      width="650px"
    >
      <div v-if="selectedBooking">
        <a-descriptions bordered size="small" :column="1" style="margin-bottom: 24px;">
          <a-descriptions-item label="ID бронювання">{{ selectedBooking.id }}</a-descriptions-item>
          <a-descriptions-item label="Тварина">{{ getPetInfo(selectedBooking)?.name || selectedBooking.pet_name || (selectedBooking.pet_id ? `#${selectedBooking.pet_id}` : 'Невідомо') }}</a-descriptions-item>
          <a-descriptions-item label="Власник">{{ getPetInfo(selectedBooking)?.owner_name || 'Невідомо' }}</a-descriptions-item>
          <a-descriptions-item label="Телефон власника">{{ getPetInfo(selectedBooking)?.owner_phone || 'Невідомо' }}</a-descriptions-item>
          <a-descriptions-item label="Вольєр">№ {{ selectedBooking.aviary_id }}</a-descriptions-item>
          <a-descriptions-item label="Період">{{ formatDate(selectedBooking.start_date) }} ➔ {{ formatDate(selectedBooking.end_date) }}</a-descriptions-item>
          <a-descriptions-item label="Поточна сума"><strong>{{ selectedBooking.total_price }} грн</strong></a-descriptions-item>
          <a-descriptions-item label="Статус бронювання">
            <a-tag :color="statusColor(selectedBooking.status)">{{ selectedBooking.status }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="Статус оплати">
            <a-tag :color="paymentColor(selectedBooking.payment_status)">{{ selectedBooking.payment_status }}</a-tag>
          </a-descriptions-item>
        </a-descriptions>

        <a-form layout="vertical">
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="Статус проживання">
                <a-select v-model:value="editForm.status">
                  <a-select-option value="Очікується">Очікується</a-select-option>
                  <a-select-option value="Актуальне">Актуальне</a-select-option>
                  <a-select-option value="Завершене">Завершене</a-select-option>
                  <a-select-option value="Скасоване">Скасоване</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="Статус оплати">
                <a-select v-model:value="editForm.payment_status">
                  <a-select-option value="Не оплачено">Не оплачено</a-select-option>
                  <a-select-option value="Оплачено частково">Оплачено частково</a-select-option>
                  <a-select-option value="Оплачено">Оплачено</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <a-form-item label="Додаткові послуги (Прайс-лист)">
            <a-checkbox-group v-model:value="editForm.service_ids" style="width: 100%">
              <a-row>
                <a-col :span="12" v-for="service in availableServices" :key="service.id">
                  <a-checkbox :value="service.id">
                    {{ service.name }} (+{{ service.price }} грн)
                  </a-checkbox>
                </a-col>
              </a-row>
            </a-checkbox-group>
            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 8px;">
              *При зміні послуг загальна сума буде автоматично перерахована.
            </div>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { CalendarOutlined } from '@ant-design/icons-vue';
import dayjs from 'dayjs';
import { bookingApi } from '@/api';
import { message } from 'ant-design-vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const props = defineProps({
  bookings: { type: Array, default: () => [] },
  hotelPets: { type: Array, default: () => [] }
});

// Емітуємо подію refresh-data, щоб DashboardView перезавантажив таблиці
const emit = defineEmits(['open-booking-modal', 'refresh-data']);

// Логіка для модалки редагування
const isDetailsModalOpen = ref(false);
const loading = ref(false);
const selectedBooking = ref(null);
const availableServices = ref([]);

const editForm = ref({
  status: '',
  payment_status: '',
  service_ids: []
});

const hotelPetsById = computed(() => {
  const map = {};
  props.hotelPets.forEach((pet) => {
    if (pet && pet.id !== undefined) {
      map[pet.id] = pet;
    }
  });
  return map;
});

const getPetInfo = (booking) => {
  return booking?.pet_id ? hotelPetsById.value[booking.pet_id] : null;
};

const totalBookings = computed(() => props.bookings.length);
const activeBookings = computed(() => {
  const today = dayjs();
  return props.bookings.filter((booking) => {
    return booking.status === 'Актуальне' &&
      dayjs(booking.start_date).isSameOrBefore(today, 'day') &&
      dayjs(booking.end_date).isSameOrAfter(today, 'day');
  }).length;
});
const upcomingBookings = computed(() => {
  const today = dayjs();
  return props.bookings.filter((booking) => dayjs(booking.start_date).isAfter(today, 'day')).length;
});
const sortByDate = ref('upcoming');
const statusFilter = ref('all');

const sortedBookings = computed(() => {
  let items = [...props.bookings];
  if (statusFilter.value !== 'all') {
    items = items.filter((booking) => booking.status === statusFilter.value);
  }

  if (sortByDate.value === 'oldest') {
    return items.sort((a, b) => new Date(a.start_date) - new Date(b.start_date));
  }
  if (sortByDate.value === 'newest') {
    return items.sort((a, b) => new Date(b.start_date) - new Date(a.start_date));
  }
  return items.sort((a, b) => new Date(a.start_date) - new Date(b.start_date));
});

const statusColor = (status) => {
  if (status === 'Актуальне') return 'blue';
  if (status === 'Завершене') return 'default';
  if (status === 'Скасоване') return 'red';
  return 'processing';
};

const paymentColor = (paymentStatus) => {
  if (paymentStatus === 'Оплачено') return 'success';
  if (paymentStatus === 'Не оплачено') return 'error';
  return 'warning';
};

const formatDate = (dateString) => {
  if (!dateString) return 'Невідомо';
  const [year, month, day] = dateString.split('-');
  return `${day}.${month}.${year}`;
};

// Завантаження доступних послуг (тільки is_active=true)
const fetchServices = async () => {
  try {
    const res = await bookingApi.getActiveServices();
    availableServices.value = res.data;
  } catch (error) {
    console.error(error);
  }
};

const openDetailsModal = async (record) => {
  selectedBooking.value = record;
  editForm.value.status = record.status;
  editForm.value.payment_status = record.payment_status;
  editForm.value.service_ids = []; // Скидаємо старі галочки
  
  isDetailsModalOpen.value = true;
  loading.value = true;

  try {
    // Отримуємо з бекенду масив ID підключених послуг
    const res = await bookingApi.getBookingServices(record.id);
    editForm.value.service_ids = res.data;
  } catch (error) {
    message.error("Не вдалося завантажити послуги бронювання");
  } finally {
    loading.value = false;
  }
};

const saveBookingChanges = async () => {
  loading.value = true;
  try {
    await bookingApi.updateBooking(selectedBooking.value.id, editForm.value, authStore.token);
    message.success("Зміни успішно збережено!");
    isDetailsModalOpen.value = false;
    emit('refresh-data'); // Кажемо батьківському компоненту оновити дані
  } catch (error) {
    message.error("Помилка збереження змін");
  } finally {
    loading.value = false;
  }
};

const deleteBooking = async (id) => {
  try {
    await bookingApi.deleteBooking(id, authStore.token);
    message.success("Бронювання видалено");
    emit('refresh-data');
  } catch (error) {
    message.error("Помилка видалення");
  }
};

onMounted(() => {
  fetchServices();
});
</script>

<style scoped>
.hotel-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.header-description {
  margin: 8px 0 0;
  color: var(--color-muted);
  max-width: 520px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  border-radius: 16px;
  border: 1px solid var(--color-border);
  background: var(--color-card-background);
  min-height: 110px;
  padding: 20px;
}

.stat-label {
  color: var(--color-muted);
  font-size: 13px;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-heading);
}

.booking-card {
  border-radius: 18px;
  overflow: hidden;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.booking-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
}

.booking-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.booking-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-heading);
}

.booking-subtitle {
  font-size: 13px;
  color: var(--color-muted);
  margin-top: 4px;
}

.booking-card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.booking-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.label {
  color: var(--color-muted);
  font-size: 13px;
}

.booking-actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 16px;
  margin-top: 18px;
}

.empty-state {
  text-align: center;
  color: var(--color-muted);
  padding: 64px 0;
}
</style>