<template>
  <div class="shell text-white">
    <div class="surface-grid">
      <section class="panel-strong">
        <div class="hero-glow"></div>

        <div class="relative z-[1] flex flex-col gap-6">
          <div class="topbar">
            <div class="space-y-4">
              <span class="eyebrow">MuhanjanNews · Панель модерации</span>

              <div class="max-w-4xl">
                <h1 class="surface-title">Проверка предложки без лишнего шума</h1>
                <p class="surface-subtitle">
                  Всё, что нужно модератору, на одном экране: очередь, поиск, фильтры, вложения, действия и понятные подсказки.
                </p>
              </div>

              <div class="meta-strip">
                <span class="badge" :class="moderationEnabled ? 'badge-approved' : 'badge-pending'">
                  {{ moderationEnabled ? 'Материалы идут в очередь' : 'Материалы публикуются сразу' }}
                </span>
                <span class="meta-chip">{{ totalCount }} материалов</span>
                <span class="meta-chip">{{ latestTimestamp }}</span>
              </div>
            </div>

            <div class="topbar-actions">
              <router-link to="/stream" class="btn-secondary" title="Открыть эфирную ленту">
                Открыть эфир
              </router-link>
              <button class="btn-secondary" :disabled="loading" @click="loadAll">
                {{ loading ? 'Обновление...' : 'Обновить' }}
              </button>
              <button class="btn-secondary" @click="toggleModeration">
                {{ moderationEnabled ? 'Выключить очередь' : 'Включить очередь' }}
              </button>
              <button class="btn-ghost" @click="logout">Выйти</button>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div class="kpi">
              <div class="kpi-label">Ждут проверки</div>
              <div class="kpi-value">{{ pending.length }}</div>
              <div class="kpi-text">Новые материалы, по которым нужно решение.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Одобрено</div>
              <div class="kpi-value">{{ approved.length }}</div>
              <div class="kpi-text">Уже готовы для показа в эфире.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Отклонено</div>
              <div class="kpi-value">{{ rejected.length }}</div>
              <div class="kpi-text">Архив отклонённых материалов.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Показано сейчас</div>
              <div class="kpi-value">{{ filteredItems.length }}</div>
              <div class="kpi-text">Результат после поиска и фильтров.</div>
            </div>
          </div>
        </div>
      </section>

      <div v-if="notice.text" class="notice" :class="notice.typeClass">
        {{ notice.text }}
      </div>

      <div class="layout-grid">
        <aside class="sidebar-stack">
          <section class="panel p-5">
            <div class="sidebar-title">Раздел</div>
            <p class="sidebar-text">
              Переключайся между очередями. Число справа показывает количество материалов.
            </p>

            <div class="mt-4 grid gap-3">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-btn w-full justify-between"
                :class="selectedTab === tab.key ? 'tab-btn-active' : ''"
                @click="selectedTab = tab.key"
              >
                <span>{{ tab.label }}</span>
                <span class="meta-chip">{{ tab.count }}</span>
              </button>
            </div>
          </section>

          <section class="panel p-5">
            <div class="sidebar-title">Поиск</div>
            <p class="sidebar-text">
              Ищи по Twitch, Telegram, тексту и ссылкам.
            </p>

            <div class="mt-4">
              <input
                v-model="searchQuery"
                class="input"
                placeholder="Ник, тема, ссылка, текст"
              />
            </div>
          </section>

          <section class="panel p-5">
            <div class="sidebar-title">Быстрые фильтры</div>
            <p class="sidebar-text">
              Помогают быстро отобрать материалы по содержимому.
            </p>

            <div class="mt-4 flex flex-wrap gap-2">
              <button
                v-for="filter in quickFilters"
                :key="filter.key"
                class="filter-chip"
                :class="quickFilter === filter.key ? 'filter-chip-active' : ''"
                @click="quickFilter = filter.key"
              >
                {{ filter.label }}
              </button>
            </div>
          </section>

          <section class="panel p-5">
            <div class="sidebar-title">Что делать модератору</div>

            <ol class="guide-list mt-4">
              <li>Открой материал из очереди.</li>
              <li>Проверь текст, ссылки и файлы.</li>
              <li>Если материал подходит — одобри.</li>
              <li>Если не подходит — отклони с причиной.</li>
            </ol>
          </section>

          <section class="panel p-5">
            <div class="sidebar-title">Сейчас открыто</div>

            <div class="info-list mt-4">
              <div class="info-row">
                <div class="kpi-label">Раздел</div>
                <div class="info-value">{{ currentTitle }}</div>
              </div>
              <div class="info-row">
                <div class="kpi-label">Последний материал</div>
                <div class="info-value">{{ latestSubmissionText }}</div>
              </div>
              <div class="info-row">
                <div class="kpi-label">Режим публикации</div>
                <div class="info-value">
                  {{ moderationEnabled ? 'Через модератора' : 'Сразу в эфир' }}
                </div>
              </div>
            </div>
          </section>
        </aside>

        <section class="space-y-4">
          <div class="panel p-5 md:p-6">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <h2 class="text-2xl font-semibold tracking-tight text-white md:text-3xl">
                  {{ currentTitle }}
                </h2>
                <p class="mt-2 max-w-3xl text-sm leading-7 text-slate-400">
                  {{ currentSubtitle }}
                </p>
              </div>

              <div class="helper-row">
                <span class="helper-pill">{{ filteredItems.length }} материалов</span>
                <span class="helper-pill">{{ searchQuery ? 'Поиск включён' : 'Без поиска' }}</span>
                <span class="helper-pill">{{ quickFilterLabel }}</span>
              </div>
            </div>
          </div>

          <div v-if="loading" class="panel p-6">
            <div class="text-sm text-slate-300">Загружаю материалы...</div>
          </div>

          <div v-else-if="filteredItems.length" class="grid gap-4">
            <SubmissionCard
              v-for="item in filteredItems"
              :key="item.id"
              :item="item"
              :show-actions="selectedTab === 'pending'"
              @approve="approve"
              @reject="reject"
              @ban="ban"
            />
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">∅</div>
            <h3 class="text-xl font-semibold text-white">Материалы не найдены</h3>
            <p class="mt-2 text-sm leading-6 text-slate-400">
              Попробуй очистить поиск, убрать фильтр или открыть другой раздел.
            </p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import SubmissionCard from '../components/SubmissionCard.vue'

const router = useRouter()

const pending = ref([])
const approved = ref([])
const rejected = ref([])
const moderationEnabled = ref(true)
const selectedTab = ref('pending')
const searchQuery = ref('')
const quickFilter = ref('all')
const loading = ref(false)

const notice = ref({
  text: '',
  typeClass: 'notice-success',
})

let noticeTimeout = null

const setNotice = (text, type = 'success') => {
  clearTimeout(noticeTimeout)

  const typeMap = {
    success: 'notice-success',
    warning: 'notice-warning',
    error: 'notice-error',
  }

  notice.value = {
    text,
    typeClass: typeMap[type] || 'notice-success',
  }

  noticeTimeout = setTimeout(() => {
    notice.value = { text: '', typeClass: 'notice-success' }
  }, 2600)
}

const loadAll = async () => {
  loading.value = true
  try {
    const [p1, p2, p3, s] = await Promise.all([
      api.get('/admin/submissions?status=pending'),
      api.get('/admin/submissions?status=approved'),
      api.get('/admin/submissions?status=rejected'),
      api.get('/admin/settings/moderation'),
    ])

    pending.value = p1.data
    approved.value = p2.data
    rejected.value = p3.data
    moderationEnabled.value = s.data.moderation_enabled
  } finally {
    loading.value = false
  }
}

const datasetMap = computed(() => ({
  pending: pending.value,
  approved: approved.value,
  rejected: rejected.value,
}))

const baseItems = computed(() => datasetMap.value[selectedTab.value] || [])

const filteredItems = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()

  let items = baseItems.value.filter((item) => {
    const haystack = [
      item?.user?.twitch_nickname,
      item?.user?.username,
      item?.user?.first_name,
      item?.user?.last_name,
      item?.message_text,
      ...(item?.links || []),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return !q || haystack.includes(q)
  })

  if (quickFilter.value === 'withText') {
    items = items.filter((item) => item?.message_text)
  }

  if (quickFilter.value === 'withMedia') {
    items = items.filter((item) => item?.attachments?.length)
  }

  if (quickFilter.value === 'withLinks') {
    items = items.filter((item) => item?.links?.length)
  }

  return items
})

const labels = {
  pending: {
    title: 'Ждут проверки',
    subtitle: 'Новые материалы, по которым нужно принять решение.',
  },
  approved: {
    title: 'Одобренные материалы',
    subtitle: 'Эти карточки уже готовы для показа в эфирной ленте.',
  },
  rejected: {
    title: 'Отклонённые материалы',
    subtitle: 'Архив материалов, которые не прошли модерацию.',
  },
}

const quickFilters = [
  { key: 'all', label: 'Все' },
  { key: 'withText', label: 'С текстом' },
  { key: 'withMedia', label: 'С файлами' },
  { key: 'withLinks', label: 'Со ссылками' },
]

const quickFilterLabelMap = {
  all: 'Все материалы',
  withText: 'Только с текстом',
  withMedia: 'Только с файлами',
  withLinks: 'Только со ссылками',
}

const quickFilterLabel = computed(() => quickFilterLabelMap[quickFilter.value] || 'Все материалы')

const tabs = computed(() => [
  { key: 'pending', label: 'Ждут проверки', count: pending.value.length },
  { key: 'approved', label: 'Одобренные', count: approved.value.length },
  { key: 'rejected', label: 'Отклонённые', count: rejected.value.length },
])

const currentTitle = computed(() => labels[selectedTab.value]?.title || '')
const currentSubtitle = computed(() => labels[selectedTab.value]?.subtitle || '')
const totalCount = computed(() => pending.value.length + approved.value.length + rejected.value.length)

const latestSubmission = computed(() => {
  return [...pending.value, ...approved.value, ...rejected.value]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0] || null
})

const latestSubmissionText = computed(() => {
  if (!latestSubmission.value) return 'Пока материалов нет.'
  return latestSubmission.value.message_text?.slice(0, 120)
    || `Материал от ${latestSubmission.value.user?.twitch_nickname || 'пользователя'} без текста.`
})

const latestTimestamp = computed(() => {
  if (!latestSubmission.value) return 'Новых поступлений пока нет'
  return `Последнее поступление: ${new Date(latestSubmission.value.created_at).toLocaleString('ru-RU')}`
})

const approve = async (item) => {
  try {
    await api.post(`/admin/submissions/${item.id}/approve`, { comment: null })
    await loadAll()
    setNotice(`Материал #${item.id} одобрен.`, 'success')
  } catch (e) {
    setNotice(e?.response?.data?.detail || 'Не удалось одобрить материал.', 'error')
  }
}

const reject = async (item) => {
  const comment = window.prompt('Укажи причину отклонения:', '')
  if (comment === null) return

  try {
    await api.post(`/admin/submissions/${item.id}/reject`, { comment })
    await loadAll()
    setNotice(`Материал #${item.id} отклонён.`, 'warning')
  } catch (e) {
    setNotice(e?.response?.data?.detail || 'Не удалось отклонить материал.', 'error')
  }
}

const ban = async (user) => {
  const reason = window.prompt('Причина блокировки:', 'Нарушение правил')
  if (reason === null) return

  try {
    await api.post(`/admin/users/${user.id}/ban`, { reason })
    await loadAll()
    setNotice(`Пользователь ${user?.twitch_nickname || user?.telegram_id} заблокирован.`, 'warning')
  } catch (e) {
    setNotice(e?.response?.data?.detail || 'Не удалось заблокировать пользователя.', 'error')
  }
}

const toggleModeration = async () => {
  try {
    await api.post('/admin/settings/moderation', { moderation_enabled: !moderationEnabled.value })
    await loadAll()
    setNotice(
      moderationEnabled.value
        ? 'Очередь модерации включена.'
        : 'Очередь модерации выключена. Материалы публикуются сразу.',
      'success',
    )
  } catch (e) {
    setNotice(e?.response?.data?.detail || 'Не удалось переключить режим публикации.', 'error')
  }
}

const logout = () => {
  localStorage.removeItem('mn_token')
  router.push('/login')
}

onMounted(async () => {
  try {
    await loadAll()
  } catch {
    logout()
  }
})
</script>
