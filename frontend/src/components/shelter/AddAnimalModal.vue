<template>
  <a-modal
    :open="open"
    :title="animalToEdit ? 'Редагувати тварину' : 'Додати нову тварину'"
    @ok="handleOk"
    @cancel="$emit('update:open', false)"
    :confirm-loading="confirmLoading"
    ok-text="Зберегти"
    cancel-text="Скасувати"
  >
    <a-form layout="vertical" :model="formState">
      <a-form-item label="Кличка" required>
        <a-input v-model:value="formState.name" placeholder="Наприклад: Джавелін" />
      </a-form-item>
      
      <a-form-item label="Вид" required>
        <a-select v-model:value="formState.species" placeholder="Оберіть вид">
          <a-select-option value="Кіт">Кіт</a-select-option>
          <a-select-option value="Собака">Собака</a-select-option>
          <a-select-option value="Інше">Інше</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="Вік (років)" required>
        <a-input-number v-model:value="formState.age" :min="0" style="width: 100%" />
      </a-form-item>

      <a-form-item label="Опис">
        <a-textarea v-model:value="formState.description" :rows="3" />
      </a-form-item>

      <a-form-item label="Показувати на публічному сайті" valuePropName="checked">
        <a-switch v-model:checked="formState.is_public" />
      </a-form-item>

      <a-form-item label="Фото тварини">
          <a-upload
            name="file"
            list-type="picture-card"
            :show-upload-list="false"
            :custom-request="uploadToCloudinary"
          >
            <img v-if="formState.photo_url" :src="formState.photo_url" alt="avatar" style="width: 100%" />
            <div v-else>
              <PlusOutlined />
              <div style="margin-top: 8px">Завантажити</div>
            </div>
          </a-upload>
        </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { ref, watch } from 'vue';
import { message } from 'ant-design-vue';
import { PlusOutlined } from '@ant-design/icons-vue';
import { animalApi } from '@/api';
const props = defineProps(['open', 'animalToEdit']);
const emit = defineEmits(['update:open', 'success']);

const confirmLoading = ref(false);
const formState = ref({
  name: '',
  species: 'Кіт',
  age: 0,
  description: '',
  photo_url: '',
  is_public: false
});

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    if (props.animalToEdit) {
      // Якщо редагуємо — копіюємо дані
      formState.value = { ...props.animalToEdit };
    } else {
      // Якщо створюємо нову — очищуємо форму
      formState.value = {
        name: '',
        species: 'Кіт',
        age: 0,
        description: '',
        photo_url: '',
        is_public: false
      };
    }
  }
});

const handleOk = async () => {
  if (!formState.value.name) return message.warning('Будь ласка, введіть кличку');
  
  confirmLoading.value = true;
  try {
    
    if (props.animalToEdit) {
      // РЕДАГУВАННЯ
      await animalApi.updateAnimal(props.animalToEdit.id, formState.value);
      message.success('Дані оновлено!');
    } else {
      // СТВОРЕННЯ
      await animalApi.createAnimal(formState.value);
      message.success('Тварину додано!');
    }
    
    emit('success');
    emit('update:open', false);
  } catch (error) {
    message.error('Помилка при збереженні');
  } finally {
    confirmLoading.value = false;
  }
};

const uploadToCloudinary = async ({ file, onSuccess, onError }) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await animalApi.uploadAnimalImage(formData);
    formState.value.photo_url = res.data.url;
    message.success('Фото тварини завантажено!');
    onSuccess(res.data);
  } catch (err) {
    console.error('Upload Error:', err);
    message.error('Не вдалося завантажити фото');
    onError(err);
  }
};
</script>