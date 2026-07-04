import { defineStore } from 'pinia';
import { authApi } from '../api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: JSON.parse(localStorage.getItem('user')) || null,
        token: localStorage.getItem('token') || null,
        orgType: localStorage.getItem('orgType') || null,
        role: localStorage.getItem('role') || null,
    }),

    actions: {
        async login(credentials) {
            try {
                const response = await authApi.login(credentials);
                const { access_token, user_name, organization_id, org_type } = response.data;
                
                this.token = access_token;
                localStorage.setItem('token', access_token);

                this.user = { full_name: user_name, organization_id };
                localStorage.setItem('user', JSON.stringify(this.user));
                
                this.orgType = org_type;
                localStorage.setItem('orgType', org_type);

                this.role = response.data.role;
                localStorage.setItem('role', this.role);

                return true;
            } catch (error) {
                console.error(error);
                throw error;
            }
        },

        logout() {
            this.user = null;
            this.token = null;
            this.role = null;
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            localStorage.removeItem('orgType');
            localStorage.removeItem('role');
        }
    },

    getters: {
        isShelter: (state) => state.orgType === 'shelter',
        isHotel: (state) => state.orgType === 'hotel',
        isAuthenticated: (state) => !!state.token,
        userName: (state) => state.user ? state.user.full_name : 'Гість',
        isAdmin: (state) => state.role === 'admin'
    }
});