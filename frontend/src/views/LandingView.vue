<template>
  <a-layout class="landing-layout">
    <a-layout-header class="header">
      <div class="logo">
        <span class="logo-icon">🐾</span>
        <span class="logo-text">PetCloud</span>
      </div>
      <a-menu mode="horizontal" :selectable="false" class="nav-menu">
        <a-menu-item key="features" @click="scrollTo('features')">Можливості</a-menu-item>
        <a-menu-item key="benefits" @click="scrollTo('benefits')">Переваги</a-menu-item>
      </a-menu>
      <div class="auth-nav">
        <a-button type="primary" class="btn-gradient" shape="round" @click="scrollTo('auth-section')">
          Почати роботу
        </a-button>
      </div>
    </a-layout-header>

    <a-layout-content>
      <section class="hero">
        <div class="hero-content">
          <div class="badge">SaaS Платформа нового покоління</div>
          <a-typography-title :level="1" class="hero-title">
            Керуйте притулком чи готелем <span class="text-gradient"><b>професійно</b></span>
          </a-typography-title>
          <a-typography-paragraph class="hero-subtitle">
            Автоматизуйте бронювання, ведіть електронні медичні картки та отримайте готовий сайт для залучення клієнтів і волонтерів.
          </a-typography-paragraph>
          <div class="hero-actions">
            <a-button type="primary" class="btn-gradient hero-btn" size="large" @click="scrollTo('auth-section')">
              Створити акаунт організації
            </a-button>
          </div>
        </div>
      </section>

      <section id="features" class="features-tabs">
        <div class="container">
          <div class="section-header">
            <a-typography-title :level="2">Функціональні модулі</a-typography-title>
            <p>Оберіть інструменти, які потрібні саме вашій організації</p>
          </div>

          <a-tabs v-model:activeKey="activeMode" centered class="modern-tabs">
            <a-tab-pane key="shelter" tab="🐕 Для Притулків">
              <a-row :gutter="[32, 32]">
                <a-col :xs="24" :md="8">
                  <div class="feature-card">
                    <div class="f-icon">📋</div>
                    <h3>Електронний реєстр</h3>
                    <p>Повна база підопічних з історією, фото та онлайн-статусами.</p>
                  </div>
                </a-col>
                <a-col :xs="24" :md="8">
                  <div class="feature-card">
                    <div class="f-icon">💉</div>
                    <h3>Медичний облік</h3>
                    <p>Журнал вакцинацій та лікування з нагадуваннями про процедури.</p>
                  </div>
                </a-col>
                <a-col :xs="24" :md="8">
                  <div class="feature-card">
                    <div class="f-icon">✨</div>
                    <h3>Публічна вітрина</h3>
                    <p>Автоматична генерація сторінки тварин, що шукають нову родину.</p>
                  </div>
                </a-col>
              </a-row>
            </a-tab-pane>

            <a-tab-pane key="hotel" tab="🏨 Для Готелів">
              <a-row :gutter="[32, 32]">
                <a-col :xs="24" :md="8">
                  <div class="feature-card">
                    <div class="f-icon">📅</div>
                    <h3>Smart Календар</h3>
                    <p>Наочна шахівниця завантаженості вольєрів з миттєвим бронюванням.</p>
                  </div>
                </a-col>
                <a-col :xs="24" :md="8">
                  <div class="feature-card">
                    <div class="f-icon">🏠</div>
                    <h3>Керування фондом</h3>
                    <p>Облік категорій номерів: від стандартних до люкс-вольєрів.</p>
                  </div>
                </a-col>
                <a-col :xs="24" :md="8">
                  <div class="feature-card">
                    <div class="f-icon">💰</div>
                    <h3>Автоматичні чеки</h3>
                    <p>Розрахунок вартості проживання та додаткових послуг у два кліки.</p>
                  </div>
                </a-col>
              </a-row>
            </a-tab-pane>

            <a-tab-pane key="promo" tab="🌐 Сайт-візитка">
              <div class="promo-banner">
                <div class="promo-text">
                  <h3>Ваш персональний сайт за 1 хвилину</h3>
                  <p>
                    Кожна організація отримує власну сторінку, яку можна редагувати: додавайте опис, контакти та фото. 
                    Це ваш головний інструмент для онлайн-присутності без витрат на розробку.
                  </p>
                  <a-button type="primary" ghost class="promo-btn">Подивитись приклад</a-button>
                </div>
                <div class="promo-visual">
                  <div class="mockup-site">
                    <div class="m-header"></div>
                    <div class="m-grid">
                      <div class="m-item"></div><div class="m-item"></div><div class="m-item"></div>
                    </div>
                  </div>
                </div>
              </div>
            </a-tab-pane>
          </a-tabs>
        </div>
      </section>

      <section id="auth-section" class="auth-section">
        <div class="auth-container">
          <div class="auth-card-wrapper">
            <a-typography-title :level="3" class="auth-title">Почніть зараз</a-typography-title>
            <a-tabs centered v-model:activeKey="authTab" class="auth-tabs">
              <a-tab-pane key="login" tab="Вхід">
                <LoginView />
              </a-tab-pane>
              <a-tab-pane key="register" tab="Реєстрація">
                <RegisterView />
              </a-tab-pane>
            </a-tabs>
          </div>
        </div>
      </section>
    </a-layout-content>

    <a-layout-footer class="footer">
      <div class="footer-content">
        <div class="footer-logo">🐾 PetCloud</div>
        <p>© 2026 Всі права захищені. Платформа для автоматизації зоосфери.</p>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue';
import LoginView from './LoginView.vue';
import RegisterView from './RegisterView.vue';

const activeMode = ref('shelter');
const authTab = ref('register');

const scrollTo = (id) => {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth' });
};
</script>

<style scoped>
.landing-layout {
  background: #ffffff;
  color: #1E293B;
  font-family: 'Inter', -apple-system, sans-serif;
}

/* Header */
.header {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  position: sticky; top: 0; z-index: 1000;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 50px; height: 72px;
  border-bottom: 1px solid #E2E8F0;
}
.logo { display: flex; align-items: center; gap: 10px; }
.logo-icon { font-size: 24px; }
.logo-text { font-size: 22px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px; }

.nav-menu { border: none; flex: 1; justify-content: center; background: transparent; }

/* Hero Section */
.hero {
  padding: 120px 24px;
  background: radial-gradient(circle at 100% 0%, #F0F9FF 0%, #ffffff 100%);
  text-align: center;
}
.badge {
  display: inline-block;
  padding: 6px 16px;
  background: #E0E7FF;
  color: #4338CA;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 24px;
}
.hero-title { font-size: 3.5rem !important; font-weight: 900 !important; color: #0F172A !important; }
.text-gradient {
  background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-subtitle { font-size: 20px; color: #64748B; max-width: 700px; margin: 20px auto 40px; }

/* Buttons */
.btn-gradient {
  background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%) !important;
  border: none !important;
  height: 44px; padding: 0 30px; font-weight: 600;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
}
.hero-btn { height: 56px; padding: 0 40px; font-size: 18px; }

/* Features */
.features-tabs { padding: 100px 24px; background: #ffffff; }
.section-header { text-align: center; margin-bottom: 60px; }
.section-header h2 { font-weight: 800 !important; color: #0F172A !important; }

.feature-card {
  background: #ffffff;
  padding: 40px 32px;
  border-radius: 24px;
  border: 1px solid #F1F5F9;
  transition: all 0.3s ease;
  height: 100%;
}
.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
  border-color: #E2E8F0;
}
.f-icon { font-size: 40px; margin-bottom: 24px; }
.feature-card h3 { font-weight: 700; color: #0F172A; }
.feature-card p { color: #64748B; line-height: 1.6; }

/* Promo Banner (Сайт-візитка) */
.promo-banner {
  background: #0F172A;
  border-radius: 32px;
  padding: 60px;
  display: flex; align-items: center; gap: 40px;
  color: white; text-align: left;
  margin-top: 40px;
}
.promo-text h3 { color: white; font-size: 28px; font-weight: 800; }
.promo-text p { color: #94A3B8; font-size: 17px; margin: 20px 0; }
.mockup-site {
  width: 300px; height: 200px; background: #1E293B; border-radius: 12px;
  padding: 15px; border: 4px solid #334155;
}
.m-header { height: 20px; background: #334155; border-radius: 4px; margin-bottom: 15px; }
.m-item { height: 40px; background: #334155; border-radius: 4px; margin-bottom: 10px; }

/* Auth Section */
.auth-section { padding: 120px 24px; background: #F8FAFC; border-top: 1px solid #E2E8F0; }
.auth-card-wrapper {
  max-width: 500px; margin: 0 auto;
  background: white; padding: 40px; border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08);
  border: 1px solid #E2E8F0;
}
.auth-title { text-align: center; margin-bottom: 30px !important; font-weight: 800 !important; }

/* Tabs Customization */
:deep(.ant-tabs-nav::before) { border: none; }
:deep(.ant-tabs-tab) { font-weight: 600; font-size: 16px; color: #64748B; }
:deep(.ant-tabs-tab-active .ant-tabs-tab-btn) { color: #2563EB !important; }
:deep(.ant-tabs-ink-bar) { background: #2563EB !important; height: 3px !important; }

/* Footer */
.footer { background: #0F172A; color: #94A3B8; padding: 60px 24px; text-align: center; }
.footer-logo { font-size: 24px; font-weight: 800; color: white; margin-bottom: 16px; }
</style>