import axios from 'axios';

// Єдина точка входу - наш API Gateway
const API_URL = 'http://127.0.0.1:8000';

axios.interceptors.request.use((config) => {
    // Дістаємо токен з localStorage (або вашого Pinia store, якщо ви зберігаєте його в localStorage)
    const token = localStorage.getItem('token'); // Або інший ключ, під яким ви зберігаєте токен
    
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// ==========================================
// 1. AUTH SERVICE (Авторизація та Команда)
// ==========================================
export const authApi = {
    // Вхід та реєстрація
    login: (credentials) => axios.post(`${API_URL}/login`, credentials),
    register: (data) => axios.post(`${API_URL}/register`, data),
    getOrgInfo: (subdomain) => axios.get(`${API_URL}/org-info/${subdomain}`),
    getCurrentOrg: () => axios.get(`${API_URL}/auth/org`),
    updateOrgSubdomain: (data) => axios.put(`${API_URL}/auth/org/subdomain`, data),
    
    // Управління командою
    getWorkers: () => axios.get(`${API_URL}/auth/workers`),
    createWorker: (data) => axios.post(`${API_URL}/auth/workers`, data),
    updateWorker: (id, data) => axios.put(`${API_URL}/auth/workers/${id}`, data),
    deleteWorker: (id) => axios.delete(`${API_URL}/auth/workers/${id}`),
};

// ==========================================
// 2. ANIMAL SERVICE (Притулок)
// ==========================================
export const animalApi = {
    // Облік тварин притулку
    getAllAnimal: () => axios.get(`${API_URL}/animals`),
    createAnimal: (data) => axios.post(`${API_URL}/animals`, data),
    updateAnimal: (id, data) => axios.put(`${API_URL}/animals/${id}`, data),
    deleteAnimal: (id) => axios.delete(`${API_URL}/animals/${id}`),

    // Медичні картки тварин
    getAllMedCard: () => axios.get(`${API_URL}/medical-records`),
    createMedCard: (data) => axios.post(`${API_URL}/medical-records`, data),
    updateMedCard: (id, data) => axios.put(`${API_URL}/medical-records/${id}`, data),
    deleteMedCard: (id) => axios.delete(`${API_URL}/medical-records/${id}`),

    // Завдання для працівників притулку
    getAllTasks: () => axios.get(`${API_URL}/tasks`),
    getDueTasks: () => axios.get(`${API_URL}/tasks/due_soon`),
    createTask: (data) => axios.post(`${API_URL}/tasks`, data),
    updateTask: (id, data) => axios.put(`${API_URL}/tasks/${id}`, data),
    deleteTask: (id) => axios.delete(`${API_URL}/tasks/${id}`),
    deleteRecurrence: (id) => axios.delete(`${API_URL}/tasks/${id}/recurrence`),

    // Облік корму та інших ресурсів
    getAllInventory: () => axios.get(`${API_URL}/inventory`),
    createInventory: (data) => axios.post(`${API_URL}/inventory`, data),
    updateInventory: (id, data) => axios.put(`${API_URL}/inventory/${id}`, data),
    deleteInventory: (id) => axios.delete(`${API_URL}/inventory/${id}`),
    uploadAnimalImage: (formData) => axios.post(`${API_URL}/animals/upload`, formData),
    getSettings: () => axios.get(`${API_URL}/settings`),
    updateSettings: (data) => axios.put(`${API_URL}/settings`, data),
    uploadSiteImage: (formData) => axios.post(`${API_URL}/settings/upload`, formData),
    getPublicSite: (schemaName) => axios.get(`${API_URL}/public/site?schema_name=${schemaName}`),
    getPublicAviaries: (schemaName) => axios.get(`${API_URL}/public/aviaries?schema_name=${schemaName}`),
    getPublicAvailableAviaries: (start, end, schemaName) => axios.get(`${API_URL}/public/aviaries/available?start_date=${start}&end_date=${end}&schema_name=${schemaName}`),
    getPublicServices: (schemaName) => axios.get(`${API_URL}/public/services?schema_name=${schemaName}`),
    createPublicBooking: (schemaName, data) => axios.post(`${API_URL}/public/bookings/full?schema_name=${schemaName}`, data),
};



// ==========================================
// 3. BOOKING SERVICE (Готель)
// ==========================================
export const bookingApi = {
    // --- Бронювання ---
    getAll: () => axios.get(`${API_URL}/bookings`),
    createFullBooking: (data) => axios.post(`${API_URL}/bookings/full`, data),
    updateBooking: (id, data) => axios.put(`${API_URL}/bookings/${id}`, data),
    deleteBooking: (id) => axios.delete(`${API_URL}/bookings/${id}`),
    getBookingServices: (id) => axios.get(`${API_URL}/bookings/${id}/services`),
    
    // --- Вольєри ---
    getAviaries: () => axios.get(`${API_URL}/aviaries`),
    getAvailableAviaries: (start, end) => axios.get(`${API_URL}/aviaries/available?start_date=${start}&end_date=${end}`),
    createAviary: (data) => axios.post(`${API_URL}/aviaries`, data),
    updateAviary: (id, data) => axios.put(`${API_URL}/aviaries/${id}`, data),
    deleteAviary: (id) => axios.delete(`${API_URL}/aviaries/${id}`),
    getPublicAviaries: (schemaName) => axios.get(`${API_URL}/public/aviaries?schema_name=${schemaName}`),
    getPublicAvailableAviaries: (start, end, schemaName) => axios.get(`${API_URL}/public/aviaries/available?start_date=${start}&end_date=${end}&schema_name=${schemaName}`),
    getPublicServices: (schemaName) => axios.get(`${API_URL}/public/services?schema_name=${schemaName}`),
    createPublicBooking: (schemaName, data) => axios.post(`${API_URL}/public/bookings/full?schema_name=${schemaName}`, data),
    updateBookingStatus: (id, data) => axios.patch(`${API_URL}/bookings/${id}/status`, data),

    // --- Клієнти готелю (Тварини власників) ---
    getHotelPets: () => axios.get(`${API_URL}/hotel_pets`),
    createHotelPet: (data) => axios.post(`${API_URL}/hotel_pets`, data),
    searchHotelPetsByPhone: (phone) => axios.get(`${API_URL}/hotel_pets/search?phone=${phone}`),

    // --- Завдання для готелю ---
    getHotelTasks: () => axios.get(`${API_URL}/hotel_tasks`),
    getDueHotelTasks: () => axios.get(`${API_URL}/hotel_tasks/due_soon`),
    createHotelTask: (data) => axios.post(`${API_URL}/hotel_tasks`, data),
    updateHotelTask: (id, data) => axios.put(`${API_URL}/hotel_tasks/${id}`, data),
    deleteHotelTask: (id) => axios.delete(`${API_URL}/hotel_tasks/${id}`),
    deleteHotelTaskRecurrence: (id) => axios.delete(`${API_URL}/hotel_tasks/${id}/recurrence`),

    // --- Додаткові послуги (Прайс-лист) ---
    getAllServices: () => axios.get(`${API_URL}/services/all`), // Для сторінки налаштування прайсу
    getActiveServices: () => axios.get(`${API_URL}/services`),   // Тільки активні (для модалки бронювання)
    createService: (data) => axios.post(`${API_URL}/services`, data),
    updateService: (id, data) => axios.put(`${API_URL}/services/${id}`, data),
    deleteService: (id) => axios.delete(`${API_URL}/services/${id}`),

    // --- Налаштування готелю ---
    getSettings: () => axios.get(`${API_URL}/settings`),
    updateSettings: (data) => axios.put(`${API_URL}/settings`, data),
    uploadHotelImage: (formData) => axios.post(`${API_URL}/settings/upload`, formData),
    getPublicSite: (schemaName) => axios.get(`${API_URL}/public/hotel/site?schema_name=${schemaName}`),

    // --- Заявки на бронювання (Booking Requests) ---
    createBookingRequest: (schemaName, data) => axios.post(`${API_URL}/public/booking-requests?schema_name=${schemaName}`, data),
    getBookingRequests: () => axios.get(`${API_URL}/booking-requests`),
    getPendingBookingRequests: () => axios.get(`${API_URL}/booking-requests/pending`),
    updateBookingRequest: (id, data) => axios.put(`${API_URL}/booking-requests/${id}`, data),
    approveBookingRequest: (id) => axios.patch(`${API_URL}/booking-requests/${id}/approve`),
    rejectBookingRequest: (id) => axios.patch(`${API_URL}/booking-requests/${id}/reject`),
};