<template>
  <div class="public-org-page fade-in">
    <div v-if="loading" class="full-screen-loader">
      <div class="spinner"></div>
      <p>Завантажуємо сторінку...</p>
    </div>

    <div v-else-if="error" class="error-page">
      <div class="error-content">
        <span class="error-icon">🐾</span>
        <h2>Організацію не знайдено</h2>
        <p>{{ error }}</p>
        <button class="primary-btn" @click="goHome">Повернутись на головну</button>
      </div>
    </div>

    <div v-else>
      <section class="clean-hero">
        <div class="container hero-container">
          <div class="hero-text-content">
            <h1 class="hero-title">{{ siteData.settings.hero_title || org.name }}</h1>
            <p class="hero-description">{{ siteData.settings.about_text || fallbackDescription }}</p>
            
            <div class="hero-actions">
              <a v-if="siteData.settings.contact_phone" :href="'tel:' + siteData.settings.contact_phone" class="btn-primary">
                Зателефонувати
              </a>
              <a v-if="siteData.settings.contact_email" :href="'mailto:' + siteData.settings.contact_email" class="btn-secondary">
                Написати нам
              </a>
              <button v-if="!isShelter" class="btn-primary" @click="openBookingModal">
                🗓️ Забронювати номер
              </button>
            </div>
            
            <div v-if="siteData.settings.address" class="hero-address">
              <span class="icon">📍</span> {{ siteData.settings.address }}
            </div>
          </div>
          
          <div class="hero-image-wrapper">
            <img 
              v-if="siteData.settings.cover_image_url" 
              :src="siteData.settings.cover_image_url" 
              alt="cover" 
              class="hero-cover-image" 
            />
            <div v-else class="hero-cover-placeholder">
              <img v-if="siteData.settings.logo_url" :src="siteData.settings.logo_url" alt="logo" class="placeholder-logo" />
              <span v-else>🏢</span>
            </div>
          </div>
        </div>
      </section>

      <section class="mission-section">
        <div class="container">
          <h2 class="section-title text-center">Наша Місія</h2>
          <div class="mission-grid">
            <div class="mission-item">
              <div class="mission-icon">💛</div>
              <h3>Щира турбота</h3>
              <p>Ми забезпечуємо кожній тварині любов, безпеку та необхідний медичний догляд.</p>
            </div>
            <div class="mission-item">
              <div class="mission-icon">🐾</div>
              <h3>Досвідчена команда</h3>
              <p>Наші спеціалісти та волонтери мають великий досвід у соціалізації та лікуванні.</p>
            </div>
            <div class="mission-item">
              <div class="mission-icon">🏠</div>
              <h3>Пошук дому</h3>
              <p>Наша головна мета — знайти для кожного хвостика люблячу та надійну родину.</p>
            </div>
          </div>
        </div>
      </section>

      <section class="content-section bg-light" v-if="isShelter">
        <div class="container">
          <h2 class="section-title text-center">Зустрічайте вашого нового друга</h2>

          <div v-if="uniqueSpecies.length > 1" class="filter-container">
            <button 
              v-for="species in uniqueSpecies" 
              :key="species"
              class="filter-btn"
              :class="{ 'active': selectedSpecies === species }"
              @click="selectedSpecies = species"
            >
              {{ species }}
            </button>
          </div>

          <div class="card-grid">
            <div v-for="animal in filteredAnimals" :key="animal.id" class="trust-card">
              <div class="card-photo">
                <img v-if="animal.photo_url" :src="animal.photo_url" alt="animal" />
                <div v-else class="photo-placeholder">Немає фото</div>
              </div>
              <div class="card-body">
                <div class="card-header">
                  <h3>{{ animal.name }}</h3>
                </div>
                
                <div class="card-details">
                  <div class="detail-col">
                    <span class="label">Вид</span>
                    <span class="value">{{ animal.species }}</span>
                  </div>
                  <div class="detail-col">
                    <span class="label">Вік</span>
                    <span class="value">{{ animal.age }} років</span>
                  </div>
                </div>

                <div class="status-badge ready">
                  <span>✓</span> Готовий до родини
                </div>

                <button class="btn-outline-primary full-width">Дізнатись більше</button>
              </div>
            </div>
            
            <div v-if="filteredAnimals.length === 0" class="no-results">
              <p>На жаль, за обраним фільтром тварин не знайдено.</p>
            </div>
          </div>
        </div>
      </section>
      
      <footer class="site-footer">
        <div class="container">
          <p>© 2026 {{ org.name }}. Працює на базі PetCloud.</p>
        </div>
      </footer>
    </div>

    <!-- Модальне вікно для бронювання готелю -->
    <div v-if="showBookingModal && !isShelter" class="modal-overlay" @click="closeBookingModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Оформлення нового заїзду</h2>
          <button class="modal-close" @click="closeBookingModal">✕</button>
        </div>

        <form @submit.prevent="submitBooking" class="booking-form">
          
          <div class="form-section">
            <h3>1. Клієнт та Тварина</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label>Номер телефону власника *</label>
                <input v-model="bookingForm.owner_phone" type="tel" placeholder="+380..." required />
              </div>
              <div class="form-group">
                <label>ПІБ власника *</label>
                <input v-model="bookingForm.owner_name" type="text" placeholder="Олена Петрівна" required />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Ім'я тварини *</label>
                <input v-model="bookingForm.pet_name" type="text" placeholder="Мурзік" required />
              </div>
              <div class="form-group">
                <label>Вид / Порода *</label>
                <input v-model="bookingForm.species" type="text" placeholder="Кіт (Мейн-кун)" required />
              </div>
            </div>

            <div class="form-group">
              <label>Особливості (Алергії, тощо)</label>
              <textarea v-model="bookingForm.description" placeholder="Розкажіть про вашу тварину, її поведінку тощо"></textarea>
            </div>
          </div>

          <div class="form-section">
            <h3>2. Проживання</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label>Дата прибуття *</label>
                <input v-model="bookingForm.start_date" type="date" required @change="handleDateChange" />
              </div>
              <div class="form-group">
                <label>Дата вибуття *</label>
                <input v-model="bookingForm.end_date" type="date" required @change="handleDateChange" />
              </div>
            </div>

            <div class="form-group">
              <label>Вільні вольєри *</label>
              <select v-model="bookingForm.aviary_id" required :disabled="availableAviaries.length === 0">
                <option value="">Спочатку оберіть дати</option>
                <option v-for="aviary in availableAviaries" :key="aviary.id" :value="aviary.id">
                  Вольєр №{{ aviary.number }} ({{ aviary.category }}) - {{ aviary.daily_price }} ₴/доба
                </option>
              </select>
            </div>
          </div>

          <div class="form-section" v-if="availableServices.length > 0">
            <h3>3. Додаткові послуги</h3>
            
            <div class="services-list">
              <div class="service-item" v-for="service in availableServices" :key="service.id">
                <label class="service-checkbox">
                  <input 
                    type="checkbox" 
                    :value="service.id" 
                    v-model="bookingForm.service_ids"
                  />
                  <span class="service-name">{{ service.name }}</span>
                  <span class="service-price">+{{ service.price }} ₴</span>
                </label>
              </div>
            </div>
          </div>

          <div class="total-price-box" v-if="calculatedTotal > 0">
            <h3>Загальна вартість: <span class="total-amount">{{ calculatedTotal }} ₴</span></h3>
            <p v-if="daysCount > 0">Проживання: {{ daysCount }} діб</p>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="closeBookingModal">Скасувати</button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting || !bookingForm.aviary_id">
              {{ isSubmitting ? 'Надсилання...' : 'Надіслати заявку' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { authApi, animalApi, bookingApi } from '@/api';
import { message } from 'ant-design-vue';

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const error = ref('');
const org = ref(null);
const siteData = ref(null);

const isShelter = computed(() => org.value?.org_type === 'shelter');
const fallbackDescription = 'Це офіційна сторінка нашої організації. Зв\'яжіться з нами для отримання детальної інформації.';

// --- Логіка бронювання готелю ---
const showBookingModal = ref(false);
const isSubmitting = ref(false);
const availableAviaries = ref([]);
const availableServices = ref([]);

const bookingForm = ref({
  owner_phone: '',
  owner_name: '',
  pet_name: '',
  species: '',
  description: '',
  start_date: '',
  end_date: '',
  aviary_id: null,
  service_ids: []
});

const openBookingModal = () => {
  resetBookingForm();
  showBookingModal.value = true;
  fetchAvailableServices();
};

const closeBookingModal = () => {
  showBookingModal.value = false;
  resetBookingForm();
};

const resetBookingForm = () => {
  bookingForm.value = {
    owner_phone: '',
    owner_name: '',
    pet_name: '',
    species: '',
    description: '',
    start_date: '',
    end_date: '',
    aviary_id: null,
    service_ids: []
  };
  availableAviaries.value = [];
};

const fetchAvailableServices = async () => {
  try {
    const res = await bookingApi.getPublicServices(org.value.schema_name);
    availableServices.value = res.data;
  } catch (error) {
    console.error('Помилка завантаження послуг', error);
  }
};

const handleDateChange = async () => {
  bookingForm.value.aviary_id = null;
  
  if (!bookingForm.value.start_date || !bookingForm.value.end_date) {
    availableAviaries.value = [];
    return;
  }

  try {
    const res = await bookingApi.getPublicAvailableAviaries(
      bookingForm.value.start_date,
      bookingForm.value.end_date,
      org.value.schema_name
    );
    availableAviaries.value = res.data;
    
    if (res.data.length === 0) {
      message.warning('На ці дати немає вільних вольєрів');
    }
  } catch (error) {
    console.error('Помилка завантаження вольєрів', error);
    message.error('Не вдалося завантажити вільні вольєри');
  }
};

const daysCount = computed(() => {
  if (!bookingForm.value.start_date || !bookingForm.value.end_date) return 0;
  const start = new Date(bookingForm.value.start_date);
  const end = new Date(bookingForm.value.end_date);
  const msPerDay = 1000 * 60 * 60 * 24;
  const diffDays = Math.ceil((end - start) / msPerDay);

  const billingMode = siteData.value?.settings?.billing_mode || 'nights';
  let days = diffDays;
  if (billingMode === 'days') {
    // inclusive calendar days: include both start and end
    days = diffDays + 1;
  }
  return days > 0 ? days : 1;
});

const calculatedTotal = computed(() => {
  let total = 0;
  
  if (bookingForm.value.aviary_id && daysCount.value > 0) {
    const aviary = availableAviaries.value.find(a => a.id === bookingForm.value.aviary_id);
    if (aviary) {
      total += aviary.daily_price * daysCount.value;
    }
  }
  
  bookingForm.value.service_ids.forEach(serviceId => {
    const service = availableServices.value.find(s => s.id === serviceId);
    if (service) {
      total += service.price;
    }
  });
  
  return total;
});

const submitBooking = async () => {
  if (!bookingForm.value.owner_phone || !bookingForm.value.owner_name || 
      !bookingForm.value.pet_name || !bookingForm.value.aviary_id) {
    message.error('Заповніть усі обов\'язкові поля та оберіть вольєр');
    return;
  }

  isSubmitting.value = true;
  try {
    await bookingApi.createBookingRequest(org.value.schema_name, {
      owner_phone: bookingForm.value.owner_phone,
      owner_name: bookingForm.value.owner_name,
      pet_name: bookingForm.value.pet_name,
      species: bookingForm.value.species,
      description: bookingForm.value.description,
      aviary_id: bookingForm.value.aviary_id,
      start_date: bookingForm.value.start_date,
      end_date: bookingForm.value.end_date,
      service_ids: bookingForm.value.service_ids
    });
    
    message.success('Заявку надіслано! Очікуйте на підтвердження від адміністратора.');
    closeBookingModal();
  } catch (err) {
    console.error(err);
    message.error(err.response?.data?.detail || 'Помилка при надісланні заявки');
  } finally {
    isSubmitting.value = false;
  }
};

// --- Логіка фільтрації тварин (для притулків) ---
const selectedSpecies = ref('Всі');

const uniqueSpecies = computed(() => {
  if (!siteData.value?.animals || siteData.value.animals.length === 0) return [];
  const speciesSet = new Set(siteData.value.animals.map(a => a.species));
  return ['Всі', ...Array.from(speciesSet)];
});

const filteredAnimals = computed(() => {
  if (!siteData.value?.animals) return [];
  if (selectedSpecies.value === 'Всі') return siteData.value.animals;
  return siteData.value.animals.filter(a => a.species === selectedSpecies.value);
});

// --- Завантаження сайту ---
const loadPublicSite = async () => {
  loading.value = true;
  error.value = '';

  try {
    const orgResponse = await authApi.getOrgInfo(route.params.subdomain);
    org.value = orgResponse.data;

    if (org.value.org_type === 'shelter') {
      const siteResponse = await animalApi.getPublicSite(org.value.schema_name);
      siteData.value = siteResponse.data;
    } else {
      const siteResponse = await bookingApi.getPublicSite(org.value.schema_name);
      siteData.value = siteResponse.data;
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не вдалося завантажити сторінку організації.';
  } finally {
    loading.value = false;
  }
};

const goHome = () => {
  router.push({ name: 'LandingPage' });
};

onMounted(loadPublicSite);
</script>

<style scoped>
/* Глобальні налаштування */
.public-org-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #1e293b;
  background-color: #ffffff;
}
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.text-center { text-align: center; }
.bg-light { background-color: #f8fafc; }
.full-width { width: 100%; }
.fade-in { animation: fadeIn 0.4s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* Кнопки */
.btn-primary {
  background: #2563eb; color: white; border: none; padding: 12px 28px;
  border-radius: 8px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: 0.2s;
  text-decoration: none; display: inline-block; text-align: center;
}
.btn-primary:hover:not(:disabled) { background: #1d4ed8; }
.btn-primary:disabled { background: #94a3b8; cursor: not-allowed; }

.btn-secondary {
  background: #f1f5f9; color: #334155; border: none; padding: 12px 28px;
  border-radius: 8px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: 0.2s;
  text-decoration: none; display: inline-block; text-align: center;
}
.btn-secondary:hover { background: #e2e8f0; }

.btn-outline-primary {
  background: transparent; color: #2563eb; border: 2px solid #2563eb;
  padding: 10px 24px; border-radius: 8px; font-weight: 600; font-size: 1rem;
  cursor: pointer; transition: 0.2s;
}
.btn-outline-primary:hover { background: #eff6ff; }

/* Loader & Error */
.full-screen-loader, .error-page { height: 100vh; display: flex; align-items: center; justify-content: center; flex-direction: column; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-icon { font-size: 48px; margin-bottom: 16px; }

/* Clean Hero Section */
.clean-hero { padding: 60px 0; background: #ffffff; }
.hero-container { display: flex; align-items: center; gap: 60px; }
.hero-text-content { flex: 1; }
.hero-title { font-size: 3rem; font-weight: 800; color: #0f172a; margin-bottom: 20px; line-height: 1.2; }
.hero-description { font-size: 1.15rem; color: #475569; margin-bottom: 32px; line-height: 1.6; }
.hero-actions { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.hero-address { color: #64748b; font-weight: 500; }
.hero-image-wrapper { flex: 1; display: flex; justify-content: center; }
.hero-cover-image { width: 100%; max-width: 500px; height: 400px; object-fit: cover; border-radius: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
.hero-cover-placeholder { width: 100%; max-width: 500px; height: 400px; background: #f1f5f9; border-radius: 24px; display: flex; align-items: center; justify-content: center; font-size: 64px; }
.placeholder-logo { max-width: 200px; max-height: 200px; object-fit: contain; }

/* Mission Section */
.mission-section { padding: 40px 0 80px; }
.section-title { font-size: 2.25rem; font-weight: 800; color: #0f172a; margin-bottom: 40px; }
.mission-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; }
.mission-item { text-align: center; padding: 24px; }
.mission-icon { font-size: 40px; margin-bottom: 20px; }
.mission-item h3 { font-size: 1.25rem; color: #1e293b; margin-bottom: 12px; font-weight: 700; }
.mission-item p { color: #64748b; line-height: 1.6; font-size: 0.95rem; }

/* Content Section & Filter */
.content-section { padding: 80px 0; border-top: 1px solid #e2e8f0; }
.filter-container { display: flex; justify-content: center; gap: 12px; margin-bottom: 40px; flex-wrap: wrap; }
.filter-btn { background: white; border: 1px solid #cbd5e1; color: #475569; padding: 8px 24px; border-radius: 100px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.filter-btn:hover { border-color: #94a3b8; color: #1e293b; }
.filter-btn.active { background: #2563eb; color: white; border-color: #2563eb; }

/* Cards Grid */
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 32px; }
.no-results { grid-column: 1 / -1; text-align: center; padding: 40px; color: #64748b; font-size: 1.1rem; }

/* Trust Card (Animal) */
.trust-card { background: white; border: 1px solid #e2e8f0; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column; transition: box-shadow 0.2s, transform 0.2s; }
.trust-card:hover { box-shadow: 0 12px 24px rgba(0,0,0,0.06); transform: translateY(-4px); }
.card-photo { height: 260px; background: #f1f5f9; }
.card-photo img { width: 100%; height: 100%; object-fit: cover; }
.photo-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #94a3b8; }
.card-body { padding: 24px; display: flex; flex-direction: column; flex-grow: 1; }
.card-header h3 { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0 0 20px 0; text-transform: uppercase; letter-spacing: 0.5px; }

.card-details { display: flex; justify-content: space-between; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #f1f5f9; }
.detail-col { display: flex; flex-direction: column; }
.detail-col .label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
.detail-col .value { font-size: 1rem; color: #0f172a; font-weight: 600; }

.status-badge { margin-bottom: 24px; padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 0.9rem; text-align: center; }
.status-badge.ready { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }

/* Hotel Card Variations */
.hotel-card { align-items: center; text-align: center; padding: 16px; }
.aviary-title { font-size: 1.5rem; margin-bottom: 8px; }
.aviary-category { color: #64748b; margin-bottom: 24px; font-weight: 500; }
.price-block { margin-bottom: 24px; }
.price-amount { font-size: 2.5rem; font-weight: 800; color: #0f172a; }
.price-currency { color: #64748b; font-weight: 500; }
.hotel-status { margin-bottom: 24px; font-weight: 600; padding: 6px 12px; border-radius: 100px; display: inline-block; }
.hotel-status.available { background: #eff6ff; color: #2563eb; }
.hotel-status.occupied { background: #fef2f2; color: #dc2626; }

/* Footer */
.site-footer { background: #0f172a; color: #94a3b8; text-align: center; padding: 32px 0; margin-top: auto; }

/* Footer */
.site-footer { background: #0f172a; color: #94a3b8; text-align: center; padding: 32px 0; margin-top: auto; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #0f172a;
  font-weight: 700;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  transition: 0.2s;
}

.modal-close:hover {
  color: #1e293b;
}

.booking-form {
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.price-preview {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
  color: #1e40af;
  font-weight: 600;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.btn-cancel {
  background: #f1f5f9;
  color: #334155;
  border: none;
  padding: 12px 28px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: 0.2s;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.services-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.service-item {
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.service-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.service-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.service-checkbox input {
  width: auto;
  cursor: pointer;
}

.service-name {
  flex-grow: 1;
  font-weight: 500;
  color: #334155;
}

.service-price {
  color: #2563eb;
  font-weight: 600;
  white-space: nowrap;
}

.total-price-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 24px;
  margin-top: 24px;
  text-align: right;
}

.total-price-box h3 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  color: #0f172a;
}

.total-amount {
  font-size: 1.5rem;
  color: #2563eb;
  font-weight: 800;
}

.total-price-box p {
  margin: 0;
  font-size: 0.9rem;
  color: #64748b;
}

/* Адаптивність */
@media (max-width: 992px) {
  .hero-container { flex-direction: column; text-align: center; }
  .hero-actions { justify-content: center; }
  .mission-grid { grid-template-columns: 1fr; gap: 24px; }
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 95%;
    border-radius: 8px;
  }

  .form-section {
    margin-bottom: 24px;
  }

  .modal-header {
    padding: 16px;
  }

  .booking-form {
    padding: 16px;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
  }
}
</style>