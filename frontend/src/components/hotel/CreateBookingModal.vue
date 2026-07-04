<template>
  <a-modal
    :open="open"
    title="Оформлення нового заїзду"
    width="700px"
    ok-text="Зберегти бронювання"
    cancel-text="Скасувати"
    :confirm-loading="loading"
    @ok="handleSubmit"
    @update:open="$emit('update:open', $event)"
  >
    <a-form layout="vertical" class="booking-form">
      
      <a-divider orientation="left">1. Клієнт та Тварина</a-divider>
      
      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item label="Номер телефону власника" required>
            <a-input-search
              v-model:value="form.owner_phone"
              placeholder="+380..."
              enter-button="Знайти"
              @search="searchClient"
              :loading="isSearching"
            />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="ПІБ власника" required>
            <a-input v-model:value="form.owner_name" placeholder="Наприклад: Олена Петрівна" />
          </a-form-item>
        </a-col>
      </a-row>

      <a-row :gutter="16">
        <a-col :span="8">
          <a-form-item label="Ім'я тварини" required>
            <a-input v-model:value="form.pet_name" placeholder="Мурзік" />
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="Вид / Порода" required>
            <a-input v-model:value="form.species" placeholder="Кіт (Мейн-кун)" />
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="Особливості (Алергії, тощо)">
            <a-input v-model:value="form.description" />
          </a-form-item>
        </a-col>
      </a-row>

      <a-divider orientation="left">2. Проживання</a-divider>
      
      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item label="Дати заїзду та виїзду" required>
            <a-range-picker 
              v-model:value="form.dates" 
              style="width: 100%" 
              format="YYYY-MM-DD"
              @change="handleDateChange"
            />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="Вільні вольєри" required>
            <a-select 
              v-model:value="form.aviary_id" 
              placeholder="Спочатку оберіть дати" 
              :disabled="!form.dates || form.dates.length === 0"
              :options="aviaryOptions"
            />
          </a-form-item>
        </a-col>
      </a-row>

      <a-divider orientation="left">3. Додаткові послуги</a-divider>
      
      <a-form-item>
        <a-checkbox-group v-model:value="form.service_ids" style="width: 100%">
          <a-row>
            <a-col :span="12" v-for="service in availableServices" :key="service.id">
              <a-checkbox :value="service.id">
                {{ service.name }} (+{{ service.price }} грн)
              </a-checkbox>
            </a-col>
          </a-row>
        </a-checkbox-group>
      </a-form-item>

      <div class="total-price-box">
        <h3>Загальна вартість: <span>{{ calculatedTotal }} грн</span></h3>
        <p v-if="daysCount > 0">Проживання: {{ daysCount }} діб</p>
      </div>

    </a-form>
  </a-modal>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { bookingApi } from '@/api';

const props = defineProps({
  open: Boolean
});
const emit = defineEmits(['update:open', 'success']);

const loading = ref(false);
const isSearching = ref(false);
const billingMode = ref('nights'); // за замовчуванням ночі
// Списки з бекенду
const availableAviaries = ref([]);
const availableServices = ref([]);

// Стан форми
const form = reactive({
  pet_id: null,
  owner_phone: '',
  owner_name: '',
  pet_name: '',
  species: '',
  description: '',
  dates: [], // Масив з двох об'єктів Day.js
  aviary_id: null,
  service_ids: []
});

// Завантаження списку послуг при відкритті компонента
const fetchServices = async () => {
  try {
    const res = await bookingApi.getActiveServices();
    availableServices.value = res.data;
  } catch (error) {
    console.error('Помилка завантаження послуг');
  }
};

const fetchHotelSettings = async () => {
  try {
    const res = await bookingApi.getSettings();
    billingMode.value = res.billing_mode;
  } catch (error) {
    console.error('Помилка завантаження налаштувань');
  }
};

// 1. ПОШУК КЛІЄНТА
const searchClient = async () => {
  if (!form.owner_phone) return message.warning('Введіть номер телефону');
  
  isSearching.value = true;
  try {
    const res = await bookingApi.searchHotelPetsByPhone(form.owner_phone);
    
    if (res.data && res.data.length > 0) {
      // Якщо знайшли (беремо першу тварину для спрощення, або можна зробити вибір, якщо їх кілька)
      const client = res.data[0];
      form.pet_id = client.id;
      form.owner_name = client.owner_name;
      form.pet_name = client.name;
      form.species = client.species;
      form.description = client.description;
      message.success('Клієнта знайдено! Дані заповнено.');
    } else {
      // Якщо не знайшли
      form.pet_id = null;
      message.info('Новий клієнт. Заповніть дані вручну.');
    }
  } catch (error) {
    message.error('Помилка пошуку');
  } finally {
    isSearching.value = false;
  }
};

// 2. ПОШУК ВІЛЬНИХ ВОЛЬЄРІВ (спрацьовує при зміні дат)
const handleDateChange = async () => {
  form.aviary_id = null; // Скидаємо старий вибір вольєра
  if (!form.dates || form.dates.length !== 2) {
    availableAviaries.value = [];
    return;
  }

  const startStr = form.dates[0].format('YYYY-MM-DD');
  const endStr = form.dates[1].format('YYYY-MM-DD');

  try {
    const res = await bookingApi.getAvailableAviaries(startStr, endStr);
    availableAviaries.value = res.data;
    if (res.data.length === 0) {
      message.warning('На ці дати немає вільних вольєрів!');
    }
  } catch (error) {
    console.error(error);
  }
};

// Форматуємо вольєри для селекта (щоб бачити назву і ціну)
const aviaryOptions = computed(() => {
  return availableAviaries.value.map(a => ({
    value: a.id,
    label: `${a.number} (${a.category}) - ${a.daily_price} грн/доба`
  }));
});

// 3. АВТОМАТИЧНА КАЛЬКУЛЯЦІЯ ВАРТОСТІ
const daysCount = computed(() => {
  if (!form.dates || form.dates.length !== 2) return 0;
  let days = form.dates[1].diff(form.dates[0], 'day');
  
  // Якщо режим "за календарні дні", додаємо +1
  if (billingMode.value === 'days') {
    days += 1;
  }
  
  return days > 0 ? days : 1;
});

const calculatedTotal = computed(() => {
  let total = 0;
  // Рахуємо проживання
  if (form.aviary_id) {
    const aviary = availableAviaries.value.find(a => a.id === form.aviary_id);
    if (aviary) {
      total += aviary.daily_price * daysCount.value;
    }
  }
  // Додаємо послуги
  form.service_ids.forEach(id => {
    const service = availableServices.value.find(s => s.id === id);
    if (service) total += service.price;
  });
  return total;
});

// ВІДПРАВКА ДАНИХ (МЕГА-ЕНДПОІНТ)
const handleSubmit = async () => {
  if (!form.owner_phone || !form.owner_name || !form.pet_name || !form.dates || !form.aviary_id) {
    return message.error('Заповніть усі обов\'язкові поля та оберіть вольєр');
  }

  loading.value = true;
  try {
    const payload = {
      pet_id: form.pet_id,
      owner_phone: form.owner_phone,
      owner_name: form.owner_name,
      pet_name: form.pet_name,
      species: form.species,
      description: form.description || "",
      aviary_id: form.aviary_id,
      start_date: form.dates[0].format('YYYY-MM-DD'),
      end_date: form.dates[1].format('YYYY-MM-DD'),
      service_ids: form.service_ids
    };

    await bookingApi.createFullBooking(payload);

    message.success('Бронювання успішно створено!');
    emit('success'); // Кажемо DashboardView оновити таблиці
    emit('update:open', false); // Закриваємо модалку
  } catch (error) {
    if (error.response && error.response.data.detail) {
      message.error(error.response.data.detail);
    } else {
      message.error('Помилка створення бронювання');
    }
  } finally {
    loading.value = false;
  }
};

// Скидаємо форму при кожному відкритті модалки
watch(() => props.open, (newVal) => {
  if (newVal) {
    Object.assign(form, {
      pet_id: null, owner_phone: '', owner_name: '', pet_name: '', 
      species: '', description: '', dates: [], aviary_id: null, service_ids: []
    });
    availableAviaries.value = [];
    fetchServices();
    fetchHotelSettings();
  }
});
</script>

<style scoped>
.booking-form {
  margin-top: 10px;
}
.total-price-box {
  margin-top: 24px;
  padding: 16px;
  background: var(--bg-tertiary, #f1f5f9);
  border-radius: 8px;
  text-align: right;
  border: 1px solid var(--border-color, #e2e8f0);
}
.total-price-box h3 {
  margin: 0;
  font-size: 18px;
}
.total-price-box h3 span {
  color: var(--accent-primary, #1677ff);
  font-weight: 700;
  font-size: 24px;
}
.total-price-box p {
  margin: 4px 0 0 0;
  color: var(--text-secondary, #64748b);
}
</style>