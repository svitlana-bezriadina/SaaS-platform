<template>
  <div class="auth-component">
    <a-form layout="vertical" :model="formState" @finish="handleLogin" class="modern-form">
      <a-form-item label="Електронна пошта" name="email" :rules="[{ required: true, message: 'Введіть email!' }]">
        <a-input v-model:value="formState.email" placeholder="email@example.com" class="modern-input" />
      </a-form-item>

      <a-form-item label="Пароль" name="password" :rules="[{ required: true, message: 'Введіть пароль!' }]">
        <a-input-password v-model:value="formState.password" placeholder="••••••••" class="modern-input" />
      </a-form-item>

      <a-button type="primary" html-type="submit" block :loading="loading" class="gradient-btn">
        Увійти
      </a-button>
    </a-form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const formState = reactive({ email: '', password: '' });

const handleLogin = async () => {
  loading.value = true;
  try {
    await authStore.login(formState);
    message.success(`Вітаємо, ${authStore.userName}!`);
    router.push('/MainPage'); 
  } catch (error) {
    message.error('Невірний логін або пароль');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-component { padding: 10px 0; }
.modern-input {
  height: 42px;
  border-radius: 8px;
  border-color: #E2E8F0;
}
.modern-input:focus { border-color: #2563EB; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1); }

.gradient-btn {
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%) !important;
  border: none !important;
  font-weight: 600;
  margin-top: 10px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
:deep(.ant-form-item-label > label) {
  color: #475569;
  font-weight: 500;
  font-size: 13px;
}
</style>