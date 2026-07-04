<template>
  <div class="auth-component">
    <a-form layout="vertical" :model="formState" @finish="handleRegister" class="modern-form">
      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item label="Назва організації" name="name" :rules="[{ required: true, message: 'Обов\'язково' }]">
            <a-input v-model:value="formState.name" placeholder="Pet Hotel" class="modern-input" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="Тип сервісу" name="org_type" :rules="[{ required: true, message: 'Оберіть тип' }]">
            <a-select v-model:value="formState.org_type" placeholder="Оберіть" class="modern-select">
              <a-select-option value="shelter">Притулок</a-select-option>
              <a-select-option value="hotel">Готель</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
      </a-row>

      <a-form-item label="ПІБ Адміністратора" name="full_name">
        <a-input v-model:value="formState.full_name" placeholder="Олександр Петренко" class="modern-input" />
      </a-form-item>

      <a-form-item label="Публічний субдомен" name="subdomain">
        <a-input v-model:value="formState.subdomain" placeholder="Наприклад, my-shelter або my-hotel" class="modern-input" />
        <div style="margin-top: 6px; color: #64748B; font-size: 13px;">Це поле формує URL типу /org/&lt;subdomain&gt;</div>
      </a-form-item>

      <a-form-item label="Email (Логін)" name="admin_email" :rules="[{ required: true, type: 'email' }]">
        <a-input v-model:value="formState.admin_email" placeholder="admin@example.com" class="modern-input" />
      </a-form-item>

      <a-form-item label="Пароль" name="password" :rules="[{ required: true }]">
        <a-input-password v-model:value="formState.password" class="modern-input" />
      </a-form-item>

      <a-button type="primary" html-type="submit" block :loading="loading" class="gradient-btn">
        Створити акаунт
      </a-button>
    </a-form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { authApi } from '@/api';
import { message } from 'ant-design-vue';

const loading = ref(false);
const formState = reactive({ name: '', org_type: undefined, full_name: '', admin_email: '', password: '', subdomain: '' });

const handleRegister = async () => {
  loading.value = true;
  try {
    await authApi.register(formState);
    message.success('Організацію успішно зареєстровано!');
  } catch (error) {
    message.error('Помилка реєстрації');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-component { padding: 5px 0; }
.modern-input, :deep(.ant-select-selector) {
  height: 40px !important;
  border-radius: 8px !important;
}
.gradient-btn {
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%) !important;
  border: none;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
:deep(.ant-form-item) { margin-bottom: 12px; }
:deep(.ant-form-item-label > label) { font-size: 13px; color: #475569; }
</style>