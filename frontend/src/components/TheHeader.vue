<template>
  <a-layout-header class="modern-header">
    <div class="header-title">
      {{ title }}
    </div>
    <div class="header-actions">
      <a-popover trigger="click" placement="bottomRight">
        <template #content>
          <div class="notifications-popover">
            <div class="popover-header">
              <div class="popover-title">Сповіщення</div>
              <div class="popover-subtitle">Термін завдань підходить найближчим часом</div>
            </div>

            <a-spin :spinning="notificationStore.isLoading">
              <a-list :data-source="todayTasks" size="small" bordered>
                <template #renderItem="{ item }">
                  <a-list-item>
                    <div class="notification-item">
                      <div class="notification-title">{{ item.title }}</div>
                      <div class="notification-meta">
                        <span>{{ formatTaskTime(item.date_time) }}</span>
                        <span v-if="item.pet_name"> · {{ item.pet_name }}</span>
                        <span v-else-if="item.animal_name"> · {{ item.animal_name }}</span>
                      </div>
                    </div>
                  </a-list-item>
                </template>
              </a-list>
            </a-spin>

            <div v-if="!notificationStore.dueTasks.length && !notificationStore.isLoading" class="empty-notifications">
              Немає нагальних завдань
            </div>

            <div class="popover-footer">
              Оновлено {{ notificationStore.lastFetchedAt ? formatRelativeTime(notificationStore.lastFetchedAt) : 'зараз' }}
            </div>
          </div>
        </template>

        <a-badge :count="notificationCount" :overflow-count="9">
          <a-button type="text" class="notification-button">🔔</a-button>
        </a-badge>
      </a-popover>

      <span class="greeting"><b>{{ authStore.userName }}</b></span>
      <div class="avatar">{{ authStore.userName.charAt(0).toUpperCase() }}</div>
      <a-button type="link" class="logout-btn" @click="handleLogout">Вийти</a-button>
    </div>
  </a-layout-header>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import { useNotificationsStore } from '../stores/notifications';
import { useRouter } from 'vue-router';
import { computed, onBeforeUnmount, onMounted, watch } from 'vue';
import { notification } from 'ant-design-vue';

defineProps({ title: { type: String, default: 'CRM System' } });

const authStore = useAuthStore();
const notificationStore = useNotificationsStore();
const router = useRouter();
let refreshTimer = null;
let lastNotifiedIds = [];

const notificationCount = computed(() => notificationStore.todayCount);
const todayTasks = computed(() => notificationStore.todayTasks);

const formatTaskTime = (value) => {
  const date = new Date(value);
  return new Intl.DateTimeFormat('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

const formatRelativeTime = (dateValue) => {
  const date = new Date(dateValue);
  return new Intl.DateTimeFormat('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

const showDuePopup = () => {
  const tasks = todayTasks.value;
  if (!tasks.length) {
    lastNotifiedIds = [];
    return;
  }

  const currentIds = tasks.map((task) => task.id).sort((a, b) => a - b);
  const sameAsLast = currentIds.length === lastNotifiedIds.length
    && currentIds.every((id, index) => id === lastNotifiedIds[index]);

  if (sameAsLast) {
    return;
  }

  const description = tasks
    .map((task) => `${formatTaskTime(task.date_time)} — ${task.title}`)
    .join('\n');

  notification.open({
    message: 'Термін виконання завдання сьогодні',
    description: description || 'Є завдання на сьогодні',
    placement: 'bottomRight',
    duration: 6,
  });

  lastNotifiedIds = currentIds;
};

const refreshNotifications = async () => {
  if (!authStore.isAuthenticated) {
    notificationStore.dueTasks = [];
    return;
  }

  await notificationStore.fetchDueTasks();
  showDuePopup();
};

onMounted(() => {
  refreshNotifications();
  refreshTimer = setInterval(refreshNotifications, 60000);
});

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});

watch(() => authStore.orgType, async () => {
  await refreshNotifications();
});

const handleLogout = () => { authStore.logout(); router.push('/'); }
</script>

<style scoped>
.modern-header {
  background: var(--color-background-soft) ;
  backdrop-filter: blur(10px);
  padding: 0 32px; 
  height: 80px;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid var(--color-border);
  position: sticky; top: 0; z-index: 9;
}
.header-title {
  font-size: 22px; font-weight: 700; color: var(--color-heading);
}
.header-actions {
  display: flex; align-items: center; gap: 16px;
}
.greeting { color: var(--color-muted); }
.greeting b { color: var(--color-heading); }
.notification-button {
  font-size: 18px;
  padding: 0 10px;
  height: 38px;
}
.notifications-popover {
  min-width: 300px;
  max-width: 360px;
}
.popover-header {
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 10px;
}
.popover-title {
  font-weight: 700;
  color: var(--color-heading);
}
.popover-subtitle {
  font-size: 12px;
  color: var(--color-muted);
}
.notification-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.notification-title {
  font-size: 14px;
  color: var(--color-text);
  font-weight: 600;
}
.notification-meta {
  font-size: 12px;
  color: var(--color-muted);
}
.empty-notifications {
  padding: 16px 0;
  text-align: center;
  color: var(--color-muted);
}
.popover-footer {
  margin-top: 10px;
  font-size: 12px;
  color: var(--color-muted);
}
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-surface);
  color: var(--color-text);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px;
}
.logout-btn { color: var(--color-muted); font-weight: 500; }
.logout-btn:hover { color: var(--color-danger); }
</style>