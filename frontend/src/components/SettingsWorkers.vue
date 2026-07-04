<template>
  <div class="workers-settings">
    <div class="header-actions" style="display: flex; justify-content: space-between; margin-bottom: 24px; align-items: center;">
      <h2>{{ authStore.isShelter ? 'Команда притулку' : 'Команда готелю' }}</h2>
      
      <a-button 
        v-if="authStore.role === 'admin'" 
        type="primary" 
        @click="openCreateModal"
      >
        <PlusOutlined /> Додати працівника
      </a-button>
    </div>

    <div v-if="authStore.isHotel" class="billing-settings" style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 24px; padding: 16px; border-radius: 16px; background: var(--color-card-background); border: 1px solid var(--color-border);">
      <div>
        <h3 style="margin: 0 0 4px; color: var(--color-heading);">Спосіб розрахунку проживання</h3>
        <p style="margin: 0; color: var(--color-muted);">Оберіть глобальну політику розрахунку вартості: за ночі чи за календарні дні.</p>
      </div>
      <a-select 
        v-model:value="billingMode" 
        style="width: 260px" 
        size="large" 
        @change="saveBillingSettings" 
        :loading="settingsLoading"
      >
        <a-select-option value="nights">За ночі (HoReCa стандарт)</a-select-option>
        <a-select-option value="days">За calendar-ні дні (Включно)</a-select-option>
      </a-select>
    </div>

    <div v-if="authStore.isHotel" class="branding-settings" style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; padding: 16px; border-radius: 16px; background: var(--color-card-background); border: 1px solid var(--color-border);">
      <div style="flex: 1 1 320px; min-width: 280px;">
        <h3 style="margin: 0 0 8px; color: var(--color-heading);">Логотип готелю</h3>
        <p style="margin: 0 0 16px; color: var(--color-muted);">Завантажте логотип, який буде відображатися на публічній сторінці.</p>
        <a-upload
          name="file"
          list-type="picture-card"
          :show-upload-list="false"
          accept="image/*"
          :custom-request="uploadLogo"
        >
          <img v-if="siteSettings.logo_url" :src="siteSettings.logo_url" alt="logo" style="width: 100%; max-height: 140px; object-fit: contain;" />
          <div v-else style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 140px; width: 100%;">
            <PlusOutlined />
            <div style="margin-top: 8px">Завантажити логотип</div>
          </div>
        </a-upload>
      </div>

      <div style="flex: 1 1 320px; min-width: 280px;">
        <h3 style="margin: 0 0 8px; color: var(--color-heading);">Обкладинка готелю</h3>
        <p style="margin: 0 0 16px; color: var(--color-muted);">Завантажте зображення для героїчної секції публічної сторінки.</p>
        <a-upload
          name="file"
          list-type="picture-card"
          :show-upload-list="false"
          accept="image/*"
          :custom-request="uploadCover"
        >
          <img v-if="siteSettings.cover_image_url" :src="siteSettings.cover_image_url" alt="cover" style="width: 100%; max-height: 140px; object-fit: cover;" />
          <div v-else style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 140px; width: 100%;">
            <PlusOutlined />
            <div style="margin-top: 8px">Завантажити обкладинку</div>
          </div>
        </a-upload>
      </div>
    </div>

    <div v-if="authStore.isShelter" class="shelter-settings" style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; padding: 16px; border-radius: 16px; background: var(--color-card-background); border: 1px solid var(--color-border);">
      <div style="flex: 1 1 420px; min-width: 280px;">
        <h3 style="margin: 0 0 8px; color: var(--color-heading);">Налаштування публічної сторінки притулку</h3>
        <p style="margin: 0 0 16px; color: var(--color-muted);">Відредагуйте заголовок, опис та контакти для сторінки притулку.</p>

        <a-form layout="vertical">
          <a-form-item label="Заголовок сторінки">
            <a-input v-model:value="siteSettings.hero_title" placeholder="Наприклад, Притулок Добрі Лапи" />
          </a-form-item>
          <a-form-item label="Опис притулку">
            <a-textarea v-model:value="siteSettings.about_text" rows="4" placeholder="Коротко про місію, адреси та відкриті дні" />
          </a-form-item>
          <a-form-item label="Телефон для контактів">
            <a-input v-model:value="siteSettings.contact_phone" placeholder="Наприклад, +380 67 123 45 67" />
          </a-form-item>
          <a-form-item label="Email для контактів">
            <a-input v-model:value="siteSettings.contact_email" placeholder="info@shelter.petcloud" />
          </a-form-item>
          <a-form-item label="Адреса притулку">
            <a-input v-model:value="siteSettings.address" placeholder="Вул. Центральна, 15, Київ" />
          </a-form-item>
        </a-form>

        <a-button type="primary" @click="saveShelterSettings" :loading="settingsLoading">Зберегти налаштування притулку</a-button>
      </div>

      <div style="flex: 1 1 320px; min-width: 280px;">
        <div style="display: grid; gap: 16px;">
          <div>
            <h3 style="margin: 0 0 8px; color: var(--color-heading);">Логотип притулку</h3>
            <p style="margin: 0 0 16px; color: var(--color-muted);">Завантажте логотип для публічної сторінки притулку.</p>
            <a-upload
              name="file"
              list-type="picture-card"
              :show-upload-list="false"
              accept="image/*"
              :custom-request="uploadLogo"
            >
              <img v-if="siteSettings.logo_url" :src="siteSettings.logo_url" alt="logo" style="width: 100%; max-height: 140px; object-fit: contain;" />
              <div v-else style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 140px; width: 100%;">
                <PlusOutlined />
                <div style="margin-top: 8px">Завантажити логотип</div>
              </div>
            </a-upload>
          </div>

          <div>
            <h3 style="margin: 0 0 8px; color: var(--color-heading);">Обкладинка притулку</h3>
            <p style="margin: 0 0 16px; color: var(--color-muted);">Завантажте велику обкладинку для публічної сторінки.</p>
            <a-upload
              name="file"
              list-type="picture-card"
              :show-upload-list="false"
              accept="image/*"
              :custom-request="uploadCover"
            >
              <img v-if="siteSettings.cover_image_url" :src="siteSettings.cover_image_url" alt="cover" style="width: 100%; max-height: 140px; object-fit: cover;" />
              <div v-else style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 140px; width: 100%;">
                <PlusOutlined />
                <div style="margin-top: 8px">Завантажити обкладинку</div>
              </div>
            </a-upload>
          </div>
        </div>
      </div>
    </div>

    <div v-if="authStore.isAdmin" class="subdomain-settings" style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; padding: 16px; border-radius: 16px; background: var(--color-card-background); border: 1px solid var(--color-border);">
      <div style="flex: 1 1 420px; min-width: 280px;">
        <h3 style="margin: 0 0 8px; color: var(--color-heading);">Публічний субдомен організації</h3>
        <p style="margin: 0 0 16px; color: var(--color-muted);">Вкажіть субдомен, за яким буде доступний публічний сайт організації.</p>

        <a-form layout="vertical">
          <a-form-item label="Субдомен">
            <a-input v-model:value="orgSubdomain" placeholder="my-shelter або my-hotel" />
          </a-form-item>
          <a-form-item label="Публічний URL">
            <a-input :value="publicOrgUrl" disabled />
          </a-form-item>
        </a-form>

        <a-button type="primary" @click="saveOrgSubdomain" :loading="orgSubdomainLoading">Зберегти субдомен</a-button>
      </div>
    </div>

    <div class="theme-switcher" style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 24px; padding: 16px; border-radius: 16px; background: var(--color-card-background); border: 1px solid var(--color-border);">
      <div>
        <h3 style="margin: 0 0 4px; color: var(--color-heading);">Тема інтерфейсу</h3>
        <p style="margin: 0; color: var(--color-muted);">Перемикач між темною та світлою темою.</p>
      </div>
      <a-switch
        checked-children="Темна"
        un-checked-children="Світла"
        v-model:checked="isDarkMode"
      />
    </div>

    <a-table :columns="filteredColumns" :data-source="workers" row-key="id" bordered>
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'role'">
          <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
            {{ record.role }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'actions' && authStore.role === 'admin'">
          <a-space>
            <a-button type="link" @click="openEditModal(record)">Редагувати</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="isModalOpen"
      :title="isEditMode ? 'Редагувати працівника' : 'Додати працівника'"
      :confirm-loading="confirmLoading"
      @ok="handleSubmit"
    >
      <a-form layout="vertical" style="margin-top: 16px;">
        <a-form-item label="ПІБ" required>
          <a-input v-model:value="form.full_name" placeholder="Іванов Іван Іванович" />
        </a-form-item>
        <a-form-item label="Email" required>
          <a-input v-model:value="form.email" type="email" placeholder="worker@petcloud.com" :disabled="isEditMode" />
        </a-form-item>
        <a-form-item label="Номер телефону">
          <a-input v-model:value="form.phone_number" placeholder="+380..." />
        </a-form-item>
        <a-form-item label="Пароль" :required="!isEditMode">
          <a-input-password v-model:value="form.password" placeholder="Мінімум 6 символів" />
        </a-form-item>
        <a-form-item label="Роль">
          <a-select v-model:value="form.role">
            <a-select-option value="worker">Працівник (Worker)</a-select-option>
            <a-select-option value="admin">Адміністратор (Admin)</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { PlusOutlined } from '@ant-design/icons-vue';
import { authApi, bookingApi, animalApi } from '@/api';
import { message } from 'ant-design-vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

// Стан для теми та працівників
const isDarkMode = ref(false);
const workers = ref([]);
const isModalOpen = ref(false);
const isEditMode = ref(false);
const confirmLoading = ref(false);
const editingWorkerId = ref(null);

// 🆕 Стан для фінансових та публічних налаштувань
const billingMode = ref('nights');
const settingsLoading = ref(false);
const siteSettings = ref({
  billing_mode: 'nights',
  logo_url: '',
  cover_image_url: '',
  hero_title: '',
  about_text: '',
  contact_phone: '',
  contact_email: '',
  address: ''
});
const orgSubdomain = ref('');
const orgSubdomainLoading = ref(false);
const publicOrgUrl = computed(() => orgSubdomain.value ? `${window.location.origin}/org/${orgSubdomain.value}` : '');

const form = ref({
  full_name: '',
  email: '',
  phone_number: '',
  password: '',
  role: 'worker'
});

const filteredColumns = [
  { title: 'ПІБ', dataIndex: 'full_name', key: 'full_name' },
  { title: 'Email', dataIndex: 'email', key: 'email' },
  { title: 'Телефон', dataIndex: 'phone_number', key: 'phone_number' },
  { title: 'Роль', dataIndex: 'role', key: 'role' },
  { title: 'Дії', key: 'actions' }
];

// 1. РОБОТА З НАЛАШТУВАННЯМИ ГОТЕЛЮ
const loadSettings = async () => {
  try {
    const serviceApi = authStore.isShelter ? animalApi : bookingApi;
    const res = await serviceApi.getSettings();
    billingMode.value = res.data.billing_mode || 'nights';
    siteSettings.value = {
      ...siteSettings.value,
      billing_mode: res.data.billing_mode || 'nights',
      logo_url: res.data.logo_url || '',
      cover_image_url: res.data.cover_image_url || '',
      hero_title: res.data.hero_title || '',
      about_text: res.data.about_text || '',
      contact_phone: res.data.contact_phone || '',
      contact_email: res.data.contact_email || '',
      address: res.data.address || ''
    };
  } catch (error) {
    console.error('Не вдалося завантажити налаштування');
  }
};

const fetchOrgInfo = async () => {
  try {
    const res = await authApi.getCurrentOrg();
    orgSubdomain.value = res.data.subdomain || '';
  } catch (error) {
    console.error('Не вдалося завантажити інформацію про організацію', error);
  }
};

const saveOrgSubdomain = async () => {
  orgSubdomainLoading.value = true;
  try {
    const res = await authApi.updateOrgSubdomain({ subdomain: orgSubdomain.value });
    orgSubdomain.value = res.data.subdomain || orgSubdomain.value;
    message.success('Субдомен збережено');
  } catch (error) {
    console.error(error);
    message.error('Не вдалося зберегти субдомен');
  } finally {
    orgSubdomainLoading.value = false;
  }
};

const saveBillingSettings = async (newValue) => {
  settingsLoading.value = true;
  try {
    await bookingApi.updateSettings({ billing_mode: newValue });
    siteSettings.value.billing_mode = newValue;
    message.success('Спосіб розрахунку проживання успішно оновлено!');
  } catch (error) {
    message.error('Помилка збереження налаштувань');
  } finally {
    settingsLoading.value = false;
  }
};

const uploadLogo = async ({ file, onSuccess, onError }) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    settingsLoading.value = true;
    const res = authStore.isShelter
      ? await animalApi.uploadSiteImage(formData)
      : await bookingApi.uploadHotelImage(formData);

    siteSettings.value.logo_url = res.data.url;
    const updateApi = authStore.isShelter ? animalApi : bookingApi;
    await updateApi.updateSettings({ logo_url: res.data.url });

    message.success('Логотип збережено');
    onSuccess(res.data);
  } catch (error) {
    console.error(error);
    message.error('Не вдалося завантажити логотип');
    onError(error);
  } finally {
    settingsLoading.value = false;
  }
};

const uploadCover = async ({ file, onSuccess, onError }) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    settingsLoading.value = true;
    const res = authStore.isShelter
      ? await animalApi.uploadSiteImage(formData)
      : await bookingApi.uploadHotelImage(formData);

    siteSettings.value.cover_image_url = res.data.url;
    const updateApi = authStore.isShelter ? animalApi : bookingApi;
    await updateApi.updateSettings({ cover_image_url: res.data.url });

    message.success('Обкладинка збережена');
    onSuccess(res.data);
  } catch (error) {
    console.error(error);
    message.error('Не вдалося завантажити обкладинку');
    onError(error);
  } finally {
    settingsLoading.value = false;
  }
};

// 2. РОБОТА З КОМАНДОЮ (Існуючий функціонал)
const fetchWorkers = async () => {
  try {
    const res = await authApi.getWorkers();
    workers.value = res.data;
  } catch (error) {
    message.error('Помилка завантаження списку працівників');
  }
};

const openCreateModal = () => {
  isEditMode.value = false;
  form.value = { full_name: '', email: '', phone_number: '', password: '', role: 'worker' };
  isModalOpen.value = true;
};

const openEditModal = (record) => {
  isEditMode.value = true;
  editingWorkerId.value = record.id;
  form.value = {
    full_name: record.full_name,
    email: record.email,
    phone_number: record.phone_number || '',
    password: '', // залишаємо порожнім, якщо не міняють
    role: record.role
  };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const saveShelterSettings = async () => {
  settingsLoading.value = true;
  try {
    await animalApi.updateSettings({
      hero_title: siteSettings.value.hero_title,
      about_text: siteSettings.value.about_text,
      contact_phone: siteSettings.value.contact_phone,
      contact_email: siteSettings.value.contact_email,
      address: siteSettings.value.address
    });
    message.success('Налаштування сторінки притулку збережено');
  } catch (error) {
    console.error(error);
    message.error('Не вдалося зберегти налаштування притулку');
  } finally {
    settingsLoading.value = false;
  }
};

const handleSubmit = async () => {
  if (!form.value.full_name || !form.value.email) {
    return message.warning('Заповніть обов\'язкові поля (ПІБ та Email)');
  }
  
  if (!isEditMode.value && !form.value.password) {
    return message.warning('При створенні нового працівника пароль обов\'язковий');
  }

  confirmLoading.value = true;
  try {
    const payload = { ...form.value };
    if (isEditMode.value) {
      await authApi.updateWorker(editingWorkerId.value, payload);
      message.success('Працівника оновлено');
    } else {
      await authApi.createWorker(payload);
      message.success('Працівника додано');
    }
    closeModal();
    await fetchWorkers();
  } catch (error) {
    console.error(error);
    message.error(isEditMode.value ? 'Помилка оновлення' : 'Помилка створення');
  } finally {
    confirmLoading.value = false;
  }
};

// Слідкуємо за темною темою (існуюча логіка)
watch(isDarkMode, (newVal) => {
  if (newVal) {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
});

onMounted(() => {
  fetchWorkers();
  loadSettings();
  fetchOrgInfo();
});
</script>