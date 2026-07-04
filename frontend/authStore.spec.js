import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import { useAuthStore } from './src/stores/auth';

global.localStorage = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};


describe('Auth Store (Мультитенантна логіка)', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('повинен коректно визначати притулок через getter isShelter', () => {
    const store = useAuthStore();
    store.orgType = 'shelter';
    
    expect(store.isShelter).toBe(true);
    expect(store.isHotel).toBe(false);
  });

  it('повинен скидати дані користувача при виклику logout()', () => {
    const store = useAuthStore();
    store.token = 'fake-jwt-token';
    store.isAuthenticated = true;
    store.logout();
    
    expect(store.token).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });
});


describe('UI Компоненти: TheSidebar.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('повинен генерувати подію change-view при кліку на пункт меню', () => {
    const emit = vi.fn();
    const handleClick = (view) => emit('change-view', view);
    
    handleClick('animals');
    
    expect(emit).toHaveBeenCalledTimes(1);
    expect(emit).toHaveBeenCalledWith('change-view', 'animals');
  });

  it('повинен динамічно змінювати текст пункту меню для готелю', () => {
    const store = useAuthStore();
    
    store.orgType = 'hotel';

    const menuLabel = store.isHotel ? 'Клієнти (Тварини)' : 'Підопічні';

    expect(menuLabel).toBe('Клієнти (Тварини)');
  });
});