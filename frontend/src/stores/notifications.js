import { defineStore } from 'pinia';
import { animalApi, bookingApi } from '@/api';
import { useAuthStore } from './auth';

export const useNotificationsStore = defineStore('notifications', {
    state: () => ({
        dueTasks: [],
        lastFetchedAt: null,
        isLoading: false,
        error: null,
    }),

    getters: {
        count: (state) => state.dueTasks.length,
        todayTasks: (state) => {
            const today = new Date();
            return state.dueTasks.filter(task => {
                const taskDate = new Date(task.date_time);
                return taskDate.getFullYear() === today.getFullYear()
                    && taskDate.getMonth() === today.getMonth()
                    && taskDate.getDate() === today.getDate();
            });
        },
        todayCount: (state) => {
            const today = new Date();
            return state.dueTasks.reduce((count, task) => {
                const taskDate = new Date(task.date_time);
                return count + (taskDate.getFullYear() === today.getFullYear()
                    && taskDate.getMonth() === today.getMonth()
                    && taskDate.getDate() === today.getDate() ? 1 : 0);
            }, 0);
        }
    },

    actions: {
        async fetchDueTasks() {
            const authStore = useAuthStore();
            this.isLoading = true;
            this.error = null;

            try {
                const response = authStore.isHotel
                    ? await bookingApi.getDueHotelTasks()
                    : await animalApi.getDueTasks();

                this.dueTasks = response.data || [];
                this.lastFetchedAt = new Date();
            } catch (error) {
                console.error('Unable to load notification tasks:', error);
                this.error = error;
                this.dueTasks = [];
            } finally {
                this.isLoading = false;
            }
        },
    }
});
