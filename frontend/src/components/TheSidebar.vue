<template>
  <a-layout-sider 
    width="260" 
    class="modern-sidebar"
  >
    <div class="logo-container">
      <div class="logo-icon">🐾</div>
      <span class="logo-text">PetCloud</span>
    </div>
    
    <a-menu :selectedKeys="selectedKeys" mode="inline" class="modern-menu">
      <div class="menu-label">ГОЛОВНЕ МЕНЮ</div>
      
      <a-menu-item key="animals" @click="emit('change-view', 'animals')">
        <user-outlined />
        <span>{{ authStore.isHotel ? 'Клієнти (Тварини)' : 'Підопічні' }}</span>
      </a-menu-item>
      
      <template v-if="authStore.isHotel">
          <a-menu-item key="services" @click="emit('change-view', 'services')">
            <tag-outlined />
            <span>Прайс-лист</span>
          </a-menu-item>

          <a-menu-item key="aviaries" @click="emit('change-view', 'aviaries')">
            <home-outlined />
            <span>Фонд вольєрів</span>
          </a-menu-item>

          <a-menu-item key="hotel_tasks" @click="emit('change-view', 'hotel_tasks')">
            <calendar-outlined />
            <span>Завдання готелю</span>
          </a-menu-item>
      </template>

      <template v-if="authStore.isShelter">
           <a-menu-item key="medical_cards" @click="emit('change-view', 'medical_cards')">
            <medicine-box-outlined />
            <span>Медичні картки</span>
          </a-menu-item>

           <a-menu-item key="calendar" @click="emit('change-view', 'calendar')">
            <calendar-outlined />
            <span>Календар</span>
          </a-menu-item>
          
           <a-menu-item key="inventory" @click="emit('change-view', 'inventory')">
            <InboxOutlined />
            <span>Склад</span>
          </a-menu-item>
      </template>

      <div class="menu-label" style="margin-top: 30px;">СИСТЕМА</div>
      <a-menu-item key="settings" @click="emit('change-view', 'settings')">
          <setting-outlined />
          <span>Налаштування</span>
      </a-menu-item>
    </a-menu>
  </a-layout-sider>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { UserOutlined, SettingOutlined, TagOutlined, HomeOutlined, MedicineBoxOutlined, CalendarOutlined, InboxOutlined } from '@ant-design/icons-vue';

const emit = defineEmits(['change-view']);
const props = defineProps({
  currentView: {
    type: String,
    default: 'animals'
  }
});

const authStore = useAuthStore();
const selectedKeys = ref([props.currentView]);

watch(
  () => props.currentView,
  (next) => {
    selectedKeys.value = [next || 'animals'];
  }
);
</script>

<style scoped>
.modern-sidebar {
  background: var(--color-background-soft) !important;
  border-right: 1px solid var(--color-border);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.logo-container {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}
.logo-icon {
  font-size: 24px;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-right: 12px;
}
.logo-text {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-heading);
  letter-spacing: -0.5px;
}

.menu-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-muted);
  padding: 0 24px;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.modern-menu {
  border-right: none;
  background: transparent;
  padding: 0 12px;
}

:deep(.ant-menu-item) {
  border-radius: 8px;
  margin-bottom: 4px !important;
  color: var(--color-text) !important;
  font-weight: 500;
  height: 44px !important;
  line-height: 44px !important;
}

:deep(.ant-menu-item:hover) {
  color: var(--color-heading) !important;
  background-color: var(--color-background-mute) !important;
}

/* Сучасний градієнт для активного пункту */
:deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
</style>