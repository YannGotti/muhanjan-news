<template>
  <div class="shell shell-center">
    <div class="surface-grid">
      <div class="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <section class="panel-strong hero-panel">
          <div class="hero-glow"></div>

          <div class="relative z-[1] flex h-full flex-col justify-between gap-8">
            <div class="space-y-6">
              <span class="eyebrow">Горбатые новости</span>

              <div class="max-w-3xl">
                <h1 class="surface-title">
                  Понятная панель для предложки, модерации и эфирной ленты
                </h1>
                <p class="surface-subtitle">
                  Без перегруженной админки. Сразу видно, что пришло, что нужно проверить и что уже можно показывать в эфире.
                </p>
              </div>

              <div class="grid gap-4 md:grid-cols-3">
                <div class="kpi">
                  <div class="kpi-label">Проверка</div>
                  <div class="kpi-text">Очередь с понятными статусами</div>
                </div>
                <div class="kpi">
                  <div class="kpi-label">Работа с контентом</div>
                  <div class="kpi-text">Текст, ссылки и файлы в одном месте</div>
                </div>
                <div class="kpi">
                  <div class="kpi-label">Эфир</div>
                  <div class="kpi-text">Одобренные материалы без мусора</div>
                </div>
              </div>
            </div>

            <div class="guide-card">
              <div class="guide-title">Как пользоваться</div>
              <ol class="guide-list">
                <li>Войди в панель.</li>
                <li>Открой очередь «Ждут проверки».</li>
                <li>Проверь текст, ссылки и вложения.</li>
                <li>Нажми «Одобрить» или «Отклонить».</li>
              </ol>
            </div>
          </div>
        </section>

        <section class="panel auth-panel">
          <div class="auth-wrap">
            <div>
              <span class="eyebrow">Вход</span>
              <h2 class="mt-4 text-3xl font-semibold tracking-tight text-white md:text-4xl">
                Панель модератора
              </h2>
              <p class="mt-3 text-sm leading-7 text-slate-400">
                Войди под администратором, чтобы проверять материалы и управлять режимом публикации.
              </p>
            </div>

            <div class="helper-row mt-6">
              <span class="helper-pill">Понятные подсказки</span>
              <span class="helper-pill">Быстрые действия</span>
              <span class="helper-pill">Лента для стрима</span>
            </div>

            <form class="mt-8 space-y-5" @submit.prevent="submit">
              <div class="field">
                <label class="field-label">Логин</label>
                <input
                  v-model="username"
                  class="input"
                  placeholder="Введите логин"
                  autocomplete="username"
                />
                <div class="field-hint">Обычно это учётная запись администратора.</div>
              </div>

              <div class="field">
                <label class="field-label">Пароль</label>
                <input
                  v-model="password"
                  class="input"
                  type="password"
                  placeholder="Введите пароль"
                  autocomplete="current-password"
                />
                <div class="field-hint">После входа откроется рабочая панель модерации.</div>
              </div>

              <button class="btn-primary w-full" :disabled="loading">
                {{ loading ? 'Вход...' : 'Войти в панель' }}
              </button>

              <div v-if="error" class="notice notice-error">
                {{ error }}
              </div>
            </form>

            <div class="mt-8 grid gap-3 sm:grid-cols-2">
              <div class="hint-box">
                <div class="hint-title">Что внутри</div>
                <div class="hint-text">Очередь, поиск, фильтры, карточки материалов и эфирная лента.</div>
              </div>
              <div class="hint-box">
                <div class="hint-title">Главная цель</div>
                <div class="hint-text">Быстро понять материал и принять решение без лишних переходов.</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const submit = async () => {
  error.value = ''
  loading.value = true

  try {
    const { data } = await api.post('/auth/login', {
      username: username.value,
      password: password.value,
    })

    localStorage.setItem('mn_token', data.access_token)
    router.push('/admin')
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Не удалось войти. Проверь логин и пароль.'
  } finally {
    loading.value = false
  }
}
</script>
