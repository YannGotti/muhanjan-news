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
                <span class="meta-chip">{{ autoRefreshLabel }}</span>
              </div>
            </div>

            <div class="topbar-actions">
              <router-link to="/stream" class="btn-secondary" title="Открыть эфирную ленту">
                Открыть эфир
              </router-link>

              <button class="btn-secondary" :disabled="loading || refreshInFlight" @click="reloadAll">
                {{ loading || refreshInFlight ? 'Обновление...' : 'Обновить' }}
              </button>

              <button class="btn-secondary" :disabled="actionLoading || refreshInFlight" @click="toggleAutoRefresh">
                {{ autoRefreshEnabled ? 'Пауза автообновления' : 'Включить автообновление' }}
              </button>

              <button class="btn-secondary" :disabled="actionLoading || refreshInFlight" @click="toggleModeration">
                {{ moderationEnabled ? 'Выключить очередь' : 'Включить очередь' }}
              </button>

              <button class="btn-ghost" @click="logout">Выйти</button>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div class="kpi">
              <div class="kpi-label">Ждут проверки</div>
              <div class="kpi-value">{{ counts.pending }}</div>
              <div class="kpi-text">Новые материалы, по которым нужно решение.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Одобрено</div>
              <div class="kpi-value">{{ counts.approved }}</div>
              <div class="kpi-text">Уже готовы для показа в эфире.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Отклонено</div>
              <div class="kpi-value">{{ counts.rejected }}</div>
              <div class="kpi-text">Архив отклонённых материалов.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Показано сейчас</div>
              <div class="kpi-value">{{ items.length }}</div>
              <div class="kpi-text">Карточки на текущей странице после фильтров.</div>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div class="panel p-5">
              <div class="kpi-label">Готовность API</div>
              <div class="mt-2 flex items-center gap-2">
                <span class="badge" :class="monitoring.ready ? 'badge-approved' : 'badge-rejected'">
                  {{ monitoring.ready ? 'READY' : 'DEGRADED' }}
                </span>
              </div>
              <div class="mt-3 text-sm text-slate-400">
                DB: {{ monitoring.database.ok ? 'ok' : 'ошибка' }},
                Redis: {{ monitoring.redis.ok ? 'ok' : 'ошибка' }}
              </div>
            </div>

            <div class="panel p-5">
              <div class="kpi-label">Очередь уведомлений</div>
              <div class="kpi-value text-[1.8rem]">{{ monitoring.notifications.queue_main ?? '—' }}</div>
              <div class="kpi-text">Основная очередь отправки уведомлений.</div>
            </div>

            <div class="panel p-5">
              <div class="kpi-label">Retry очередь</div>
              <div class="kpi-value text-[1.8rem]">{{ monitoring.notifications.queue_retry ?? '—' }}</div>
              <div class="kpi-text">Задачи, которые требуют повторной отправки.</div>
            </div>

            <div class="panel p-5">
              <div class="kpi-label">Worker уведомлений</div>
              <div class="mt-2 flex items-center gap-2">
                <span class="badge" :class="monitoring.notifications.worker_alive ? 'badge-approved' : 'badge-rejected'">
                  {{ monitoring.notifications.worker_alive ? 'жив' : 'не отвечает' }}
                </span>
              </div>
              <div class="mt-3 text-sm text-slate-400">
                Возраст heartbeat: {{ workerAgeLabel }}
              </div>
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
              Переключайся между очередями. Число справа показывает общее количество материалов.
            </p>

            <div class="mt-4 grid gap-3">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-btn w-full justify-between"
                :class="selectedTab === tab.key ? 'tab-btn-active' : ''"
                @click="selectTab(tab.key)"
              >
                <span>{{ tab.label }}</span>
                <span class="meta-chip">{{ tab.count }}</span>
              </button>
            </div>
          </section>

          <section class="panel p-5">
            <div class="sidebar-title">Поиск</div>
            <p class="sidebar-text">
              Ищи по Twitch, Telegram, тексту и ссылкам. Поиск идёт по серверу, а не только по текущей странице.
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
                @click="setQuickFilter(filter.key)"
              >
                {{ filter.label }}
              </button>
            </div>
          </section>

          <section class="panel p-5">
            <div class="sidebar-title">Автообновление</div>
            <p class="sidebar-text">
              Когда вкладка активна, список, счётчики и мониторинг обновляются автоматически.
            </p>

            <div class="mt-4 info-list">
              <div class="info-row">
                <div class="kpi-label">Режим</div>
                <div class="info-value">{{ autoRefreshEnabled ? 'Включён' : 'Выключен' }}</div>
              </div>
              <div class="info-row">
                <div class="kpi-label">Интервал</div>
                <div class="info-value">{{ safeAutoRefreshSeconds }} сек.</div>
              </div>
              <div class="info-row">
                <div class="kpi-label">Последнее обновление</div>
                <div class="info-value">{{ monitoringUpdatedAt }}</div>
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
                <span class="helper-pill">{{ currentTotal }} найдено</span>
                <span class="helper-pill">{{ searchQuery ? 'Поиск включён' : 'Без поиска' }}</span>
                <span class="helper-pill">{{ quickFilterLabel }}</span>
                <span class="helper-pill">Страница {{ page }} / {{ totalPages }}</span>
              </div>
            </div>
          </div>

          <div class="panel p-5 md:p-6">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div class="text-sm text-slate-400">
                Показаны материалы с {{ itemRangeStart }} по {{ itemRangeEnd }} из {{ currentTotal }}.
              </div>

              <div class="flex flex-wrap gap-3">
                <button class="btn-secondary btn-small" :disabled="page <= 1 || loading || refreshInFlight" @click="prevPage">
                  Назад
                </button>
                <button class="btn-secondary btn-small" :disabled="page >= totalPages || loading || refreshInFlight" @click="nextPage">
                  Вперёд
                </button>
              </div>
            </div>
          </div>

          <div v-if="loading" class="panel p-6">
            <div class="text-sm text-slate-300">Загружаю материалы...</div>
          </div>

          <div v-else-if="items.length" class="grid gap-4">
            <SubmissionCard
              v-for="item in items"
              :key="item.id"
              :item="item"
              :show-actions="true"
              @approve="approve"
              @reject="openRejectModal"
              @ban="openBanModal"
              @unban="openUnbanModal"
              @open-user="openUserDetails"
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

    <AdminActionModal
      :open="rejectModal.open"
      title="Отклонить материал"
      description="Укажи понятную причину. Она сохранится в карточке и поможет разобраться позже."
      submit-text="Отклонить материал"
      placeholder="Например: не подходит по теме, недостаточно данных, дубликат, нарушение правил..."
      input-label="Причина отклонения"
      :required="true"
      :danger="true"
      :loading="actionLoading"
      @close="closeRejectModal"
      @submit="submitReject"
    />

    <AdminActionModal
      :open="banModal.open"
      title="Заблокировать автора"
      description="Причина блокировки покажется модераторам и будет доступна в карточке пользователя."
      submit-text="Заблокировать"
      placeholder="Например: спам, флуд, неоднократные нарушения правил..."
      input-label="Причина блокировки"
      :required="true"
      :danger="true"
      :loading="actionLoading"
      @close="closeBanModal"
      @submit="submitBan"
    />

    <AdminActionModal
      :open="unbanModal.open"
      title="Разблокировать автора"
      description="Подтверди снятие блокировки. Причина блокировки будет очищена."
      submit-text="Разблокировать"
      :with-input="false"
      :danger="false"
      :loading="actionLoading"
      @close="closeUnbanModal"
      @submit="submitUnban"
    />

    <UserDetailsModal
      :open="userDetailsModal.open"
      :details="userDetailsModal.details"
      :loading="userDetailsModal.loading"
      @close="closeUserDetails"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import SubmissionCard from '../components/SubmissionCard.vue'
import AdminActionModal from '../components/AdminActionModal.vue'
import UserDetailsModal from '../components/UserDetailsModal.vue'

const router = useRouter()

const items = ref([])
const moderationEnabled = ref(true)
const selectedTab = ref('pending')
const searchQuery = ref('')
const quickFilter = ref('all')
const loading = ref(false)
const actionLoading = ref(false)
const refreshInFlight = ref(false)
const page = ref(1)
const pageSize = 20
const currentTotal = ref(0)
const counts = ref({
  pending: 0,
  approved: 0,
  rejected: 0,
})

const monitoring = ref({
  ready: false,
  database: { ok: false },
  redis: { ok: false },
  notifications: {
    queue_main: 0,
    queue_retry: 0,
    worker_alive: false,
    worker_age_seconds: null,
  },
})

const monitoringUpdatedAt = ref('—')
const autoRefreshEnabled = ref(true)
const autoRefreshSeconds = ref(15)

const notice = ref({
  text: '',
  typeClass: 'notice-success',
})

const rejectModal = ref({ open: false, item: null })
const banModal = ref({ open: false, user: null })
const unbanModal = ref({ open: false, user: null })
const userDetailsModal = ref({ open: false, details: null, loading: false })

let noticeTimeout = null
let searchDebounce = null
let activeController = null
let autoRefreshTimer = null

const isCanceledError = (error) => error?.code === 'ERR_CANCELED' || error?.name === 'CanceledError'
const isAuthError = (error) => [401, 403].includes(error?.response?.status)
const errorMessage = (error, fallback) => error?.response?.data?.detail || fallback

const safeAutoRefreshSeconds = computed(() => {
  const value = Number(autoRefreshSeconds.value)
  if (!Number.isFinite(value) || value < 5) {
    return 15
  }
  return Math.floor(value)
})

const abortActiveRequest = () => {
  if (activeController) {
    activeController.abort()
    activeController = null
  }
}

const clearAutoRefresh = () => {
  if (autoRefreshTimer) {
    clearTimeout(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

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

const quickFilters = [
  { key: 'all', label: 'Все' },
  { key: 'withText', label: 'С текстом' },
  { key: 'withMedia', label: 'С файлами' },
  { key: 'withLinks', label: 'Со ссылками' },
]

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

const quickFilterLabelMap = {
  all: 'Все материалы',
  withText: 'Только с текстом',
  withMedia: 'Только с файлами',
  withLinks: 'Только со ссылками',
}

const tabs = computed(() => [
  { key: 'pending', label: 'Ждут проверки', count: counts.value.pending },
  { key: 'approved', label: 'Одобренные', count: counts.value.approved },
  { key: 'rejected', label: 'Отклонённые', count: counts.value.rejected },
])

const currentTitle = computed(() => labels[selectedTab.value]?.title || '')
const currentSubtitle = computed(() => labels[selectedTab.value]?.subtitle || '')
const quickFilterLabel = computed(() => quickFilterLabelMap[quickFilter.value] || 'Все материалы')
const totalCount = computed(() => counts.value.pending + counts.value.approved + counts.value.rejected)
const totalPages = computed(() => Math.max(Math.ceil(currentTotal.value / pageSize), 1))
const itemRangeStart = computed(() => (currentTotal.value ? (page.value - 1) * pageSize + 1 : 0))
const itemRangeEnd = computed(() => Math.min(page.value * pageSize, currentTotal.value))

const latestTimestamp = computed(() => {
  const firstItem = items.value[0]
  if (!firstItem) return 'Новых поступлений на этой странице нет'
  return `Последнее поступление: ${new Date(firstItem.created_at).toLocaleString('ru-RU')}`
})

const autoRefreshLabel = computed(() => {
  return autoRefreshEnabled.value
    ? `Автообновление: каждые ${safeAutoRefreshSeconds.value} сек.`
    : 'Автообновление отключено'
})

const workerAgeLabel = computed(() => {
  const age = monitoring.value?.notifications?.worker_age_seconds
  if (age === null || age === undefined) return 'нет данных'
  return `${age} сек.`
})

const buildFilterParams = () => {
  const params = new URLSearchParams()

  const q = searchQuery.value.trim()
  if (q) params.set('q', q)

  if (quickFilter.value === 'withText') params.set('has_text', 'true')
  if (quickFilter.value === 'withMedia') params.set('has_attachments', 'true')
  if (quickFilter.value === 'withLinks') params.set('has_links', 'true')

  return params
}

const buildListParams = (statusKey) => {
  const params = buildFilterParams()
  params.set('status', statusKey)
  params.set('limit', String(pageSize))
  params.set('offset', String((page.value - 1) * pageSize))
  return params
}

const loadStats = async (signal) => {
  const { data } = await api.get(`/admin/submissions/stats?${buildFilterParams().toString()}`, { signal })
  counts.value = {
    pending: data.pending || 0,
    approved: data.approved || 0,
    rejected: data.rejected || 0,
  }
}

const loadMonitoring = async (signal) => {
  const { data } = await api.get('/admin/monitoring/summary', { signal })
  monitoring.value = data
  monitoringUpdatedAt.value = new Date().toLocaleTimeString('ru-RU')
}

const loadCurrentPage = async (signal) => {
  loading.value = true
  try {
    const [listRes, moderationRes] = await Promise.all([
      api.get(`/admin/submissions?${buildListParams(selectedTab.value).toString()}`, { signal }),
      api.get('/admin/settings/moderation', { signal }),
    ])

    items.value = listRes.data.items || []
    currentTotal.value = listRes.data.total || 0
    moderationEnabled.value = moderationRes.data.moderation_enabled
  } finally {
    loading.value = false
  }
}

const performReload = async (mode = 'all') => {
  if (refreshInFlight.value) return

  refreshInFlight.value = true
  const controller = new AbortController()
  activeController = controller

  try {
    if (mode === 'page') {
      await Promise.all([
        loadCurrentPage(controller.signal),
        loadMonitoring(controller.signal),
      ])
    } else {
      await Promise.all([
        loadStats(controller.signal),
        loadCurrentPage(controller.signal),
        loadMonitoring(controller.signal),
      ])
    }
  } catch (error) {
    if (isCanceledError(error)) return
    if (isAuthError(error)) {
      logout()
      return
    }
    setNotice(errorMessage(error, 'Не удалось обновить данные панели.'), 'error')
  } finally {
    if (activeController === controller) {
      activeController = null
    }
    refreshInFlight.value = false
  }
}

const reloadAll = async () => {
  await performReload('all')
}

const reloadPageOnly = async () => {
  await performReload('page')
}

const runSearchRefresh = () => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(async () => {
    page.value = 1
    await reloadAll()
  }, 350)
}

const scheduleNextAutoRefresh = () => {
  clearAutoRefresh()

  if (!autoRefreshEnabled.value) return

  autoRefreshTimer = setTimeout(async () => {
    if (document.visibilityState === 'visible' && !refreshInFlight.value && !actionLoading.value) {
      await reloadAll()
    }
    scheduleNextAutoRefresh()
  }, safeAutoRefreshSeconds.value * 1000)
}

const startAutoRefresh = () => {
  scheduleNextAutoRefresh()
}

const toggleAutoRefresh = () => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
}

const selectTab = async (tabKey) => {
  selectedTab.value = tabKey
  page.value = 1
  await reloadPageOnly()
}

const setQuickFilter = (filterKey) => {
  quickFilter.value = filterKey
}

const openUserDetails = async (user) => {
  if (!user?.id) return

  userDetailsModal.value = {
    open: true,
    details: null,
    loading: true,
  }

  try {
    const { data } = await api.get(`/admin/users/${user.id}/details`)
    userDetailsModal.value = {
      open: true,
      details: data,
      loading: false,
    }
  } catch (e) {
    if (isAuthError(e)) {
      logout()
      return
    }

    userDetailsModal.value = {
      open: true,
      details: null,
      loading: false,
    }
    setNotice(errorMessage(e, 'Не удалось загрузить профиль автора.'), 'error')
  }
}

const closeUserDetails = () => {
  userDetailsModal.value = {
    open: false,
    details: null,
    loading: false,
  }
}

const approve = async (item) => {
  actionLoading.value = true
  try {
    await api.post(`/admin/submissions/${item.id}/approve`, { comment: null })
    await reloadAll()
    if (userDetailsModal.value.open && userDetailsModal.value.details?.user?.id === item.user?.id) {
      await openUserDetails(item.user)
    }
    setNotice(`Материал #${item.id} одобрен.`, 'success')
  } catch (e) {
    if (isAuthError(e)) {
      logout()
      return
    }
    setNotice(errorMessage(e, 'Не удалось одобрить материал.'), 'error')
  } finally {
    actionLoading.value = false
  }
}

const openRejectModal = (item) => {
  rejectModal.value = { open: true, item }
}

const closeRejectModal = () => {
  rejectModal.value = { open: false, item: null }
}

const submitReject = async (comment) => {
  const currentItem = rejectModal.value.item
  if (!currentItem) return

  actionLoading.value = true
  try {
    await api.post(`/admin/submissions/${currentItem.id}/reject`, { comment })
    closeRejectModal()
    await reloadAll()
    if (userDetailsModal.value.open && userDetailsModal.value.details?.user?.id === currentItem.user?.id) {
      await openUserDetails(currentItem.user)
    }
    setNotice(`Материал #${currentItem.id} отклонён.`, 'warning')
  } catch (e) {
    if (isAuthError(e)) {
      logout()
      return
    }
    setNotice(errorMessage(e, 'Не удалось отклонить материал.'), 'error')
  } finally {
    actionLoading.value = false
  }
}

const openBanModal = (user) => {
  banModal.value = { open: true, user }
}

const closeBanModal = () => {
  banModal.value = { open: false, user: null }
}

const submitBan = async (reason) => {
  const currentUser = banModal.value.user
  if (!currentUser) return

  actionLoading.value = true
  try {
    await api.post(`/admin/users/${currentUser.id}/ban`, { reason })
    closeBanModal()
    await reloadAll()
    if (userDetailsModal.value.open && userDetailsModal.value.details?.user?.id === currentUser.id) {
      await openUserDetails(currentUser)
    }
    setNotice(`Пользователь ${currentUser?.twitch_nickname || currentUser?.telegram_id} заблокирован.`, 'warning')
  } catch (e) {
    if (isAuthError(e)) {
      logout()
      return
    }
    setNotice(errorMessage(e, 'Не удалось заблокировать пользователя.'), 'error')
  } finally {
    actionLoading.value = false
  }
}

const openUnbanModal = (user) => {
  unbanModal.value = { open: true, user }
}

const closeUnbanModal = () => {
  unbanModal.value = { open: false, user: null }
}

const submitUnban = async () => {
  const currentUser = unbanModal.value.user
  if (!currentUser) return

  actionLoading.value = true
  try {
    await api.post(`/admin/users/${currentUser.id}/unban`)
    closeUnbanModal()
    await reloadAll()
    if (userDetailsModal.value.open && userDetailsModal.value.details?.user?.id === currentUser.id) {
      await openUserDetails(currentUser)
    }
    setNotice(`Пользователь ${currentUser?.twitch_nickname || currentUser?.telegram_id} разблокирован.`, 'success')
  } catch (e) {
    if (isAuthError(e)) {
      logout()
      return
    }
    setNotice(errorMessage(e, 'Не удалось разблокировать пользователя.'), 'error')
  } finally {
    actionLoading.value = false
  }
}

const toggleModeration = async () => {
  actionLoading.value = true
  try {
    const newValue = !moderationEnabled.value
    await api.post('/admin/settings/moderation', { moderation_enabled: newValue })
    moderationEnabled.value = newValue
    setNotice(
      newValue
        ? 'Очередь модерации включена.'
        : 'Очередь модерации выключена. Материалы публикуются сразу.',
      'success',
    )
  } catch (e) {
    if (isAuthError(e)) {
      logout()
      return
    }
    setNotice(errorMessage(e, 'Не удалось переключить режим публикации.'), 'error')
  } finally {
    actionLoading.value = false
  }
}

const prevPage = async () => {
  if (page.value <= 1) return
  page.value -= 1
  await reloadPageOnly()
}

const nextPage = async () => {
  if (page.value >= totalPages.value) return
  page.value += 1
  await reloadPageOnly()
}

const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    scheduleNextAutoRefresh()
  }
}

const logout = () => {
  abortActiveRequest()
  clearAutoRefresh()
  localStorage.removeItem('mn_token')
  router.push('/login')
}

watch(searchQuery, runSearchRefresh)
watch(quickFilter, runSearchRefresh)
watch(autoRefreshEnabled, () => {
  scheduleNextAutoRefresh()
})
watch(safeAutoRefreshSeconds, () => {
  scheduleNextAutoRefresh()
})

onMounted(async () => {
  await reloadAll()
  scheduleNextAutoRefresh()
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  abortActiveRequest()
  clearAutoRefresh()
  clearTimeout(searchDebounce)
  clearTimeout(noticeTimeout)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>