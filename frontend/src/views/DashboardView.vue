<template>
  <a-layout style="min-height: 100vh">
    <TheSidebar v-model:collapsed="collapsed" :current-view="currentView" @change-view="handleChangeView" />
    <a-layout>
      <TheHeader :title="pageTitle" />
      <a-layout-content style="margin: 16px">
        <div style="padding: 24px; background: var(--color-background-soft); min-height: 360px">
          
          <ShelterDashboard 
            v-if="authStore.isShelter && currentView === 'animals'" 
            :animals="animals" 
            :loading="loading" 
            :columns="shelterColumns"
            @open-add-modal="openCreateModal"
            @edit="openEditModal"
            @delete="deleteAnimal"
            @toggle-public="toggleAnimalPublic"
          />

          <MedicalCardsView 
            v-else-if="authStore.isShelter && currentView === 'medical_cards'" 
            :cards="medicalCards" 
            :loading="loading"
            @refresh="fetchMedicalCards" 
          />

          <ShelterCalendarTasks 
            v-else-if="authStore.isShelter && currentView === 'calendar'" 
            @refresh="fetchCalendar"
          />

          <ShelterInventory 
            v-else-if="authStore.isShelter && currentView === 'inventory'" 
          />

          <HotelDashboard 
            v-else-if="authStore.isHotel && currentView === 'animals'" 
            :bookings="bookings"
            :hotel-pets="animals"
            @open-booking-modal="isBookingModalOpen = true"
            @refresh-data="fetchAnimals"
          />

          <HotelServices 
            v-else-if="authStore.isHotel && currentView === 'services'"
          />

          <HotelAviaries 
            v-else-if="authStore.isHotel && currentView === 'aviaries'" 
          />

          <HotelTasks
            v-else-if="authStore.isHotel && currentView === 'hotel_tasks'"
          />

          <SettingsWorkers 
            v-else-if="currentView === 'settings'"
          />
          
        </div>
      </a-layout-content>
    </a-layout>

    <AddAnimalModal 
      v-if="authStore.isShelter" 
      v-model:open="isModalOpen" 
      :animal-to-edit="editingAnimal" 
      @success="fetchAnimals" 
    />

    <CreateBookingModal 
      v-if="authStore.isHotel" 
      v-model:open="isBookingModalOpen" 
      @success="fetchAnimals"
    />
  </a-layout>
</template>

<script setup>
import ShelterDashboard from '../components/shelter/ShelterDashboard.vue';
import HotelDashboard from '../components/hotel/HotelDashboard.vue';
import MedicalCardsView from '../components/shelter/MedicalCardsView.vue';
import TheSidebar from '../components/TheSidebar.vue';
import TheHeader from '../components/TheHeader.vue';
import AddAnimalModal from '../components/shelter/AddAnimalModal.vue';
import CreateBookingModal from '../components/hotel/CreateBookingModal.vue';
import ShelterCalendarTasks from '../components/shelter/ShelterCalendarTasks.vue';
import ShelterInventory from '../components/shelter/ShelterInventory.vue';
import SettingsWorkers from '@/components/SettingsWorkers.vue';
import HotelAviaries from '@/components/hotel/HotelAviaries.vue';
import HotelServices from '@/components/hotel/HotelServices.vue';
import HotelTasks from '@/components/hotel/HotelTasks.vue';

import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import { animalApi, bookingApi } from '@/api';


const authStore = useAuthStore();
const collapsed = ref(false);
const currentView = ref('animals');
const loading = ref(false);
const animals = ref([]);
const bookings = ref([]);
const shelterColumns = [
  { title: 'Тварина', key: 'name', dataIndex: 'name' },
  { title: 'Вид', dataIndex: 'species', key: 'species' },
  { title: 'Вік', dataIndex: 'age', key: 'age' },
  { title: 'На сайті', dataIndex: 'is_public', key: 'is_public', width: 120 },
  { title: 'Дії', key: 'actions', width: 150 }
];

const pageTitle = computed(() => {
  if (currentView.value === 'settings') {
    return 'Налаштування';
  }
  if (authStore.isHotel && currentView.value === 'hotel_tasks') {
    return 'Завдання готелю';
  }
  return authStore.isShelter ? 'Панель притулку' : 'Панель готелю';
});

const fetchAnimals = async () => {
  loading.value = true;
  try {
    if (authStore.isShelter) {
      const res = await animalApi.getAllAnimal();
      animals.value = res.data;
    } else if (authStore.isHotel) {
      const [petsRes, bookingsRes] = await Promise.all([
        bookingApi.getHotelPets(),
        bookingApi.getAll()
      ]);
      animals.value = petsRes.data;
      bookings.value = bookingsRes.data;
    }
  } catch (error) {
    console.error("Помилка завантаження:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (authStore.isHotel && currentView.value === 'medical_cards') {
    currentView.value = 'animals';
  }

  handleChangeView(currentView.value);
});

const isModalOpen = ref(false);
const editingAnimal = ref(null);
const isBookingModalOpen = ref(false);

const openCreateModal = () => {
    editingAnimal.value = null;
    isModalOpen.value = true;
};

const openEditModal = (animal) => {
    editingAnimal.value = { ...animal };
    isModalOpen.value = true;
};

const deleteAnimal = async (id) => {
  try {
    await animalApi.delete(id);
    await fetchAnimals();
  } catch (error) {
    console.error("Помилка видалення:", error);
  }
};

const toggleAnimalPublic = async (animal) => {
  try {
    const updatedAnimal = { ...animal, is_public: !animal.is_public };
    await animalApi.updateAnimal(animal.id, updatedAnimal);
    await fetchAnimals();
  } catch (error) {
    console.error("Помилка оновлення статусу публічності:", error);
  }
};

const medicalCards = ref([]);

const fetchMedicalCards = async () => {
  loading.value = true;
  try {
    const res = await animalApi.getAllMedCard();
    medicalCards.value = res.data;
  } catch (error) {
    console.error("Помилка завантаження медкарток:", error);
  } finally {
    loading.value = false;
  }
};

const fetchCalendar = async () => {
  try {
  } catch (error) {
    console.error("Помилка завантаження календаря:", error);
  }
};

// Оновлюємо функцію зміни вкладок
const handleChangeView = (view) => {
  currentView.value = view;
  if (view === 'animals') fetchAnimals();
  if (view === 'medical_cards') fetchMedicalCards();
  if (view === 'calendar') fetchCalendar();
};
</script>

<style scoped>
/* Твої улюблені стилі без змін */
.modern-table :deep(.ant-table) {
  background: transparent;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.name-info {
  display: flex;
  flex-direction: column;
}

.animal-name {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 14px;
}

.animal-breed {
  font-size: 12px;
  color: var(--text-secondary);
}

.ant-btn-primary {
  background: var(--accent-primary);
  border-radius: 8px;
  font-weight: 600;
  height: 40px;
}
</style>