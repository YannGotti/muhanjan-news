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
              <button class="btn-secondary" :disabled="loading" @click="reloadAll">
                {{ loading ? 'Обновление...' : 'Обновить' }}
              </button>
              <button class="btn-secondary" :disabled="actionLoading" @click="toggleModeration">
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
            <div class="sidebar-title">Что делать модератору</div>

            <ol class="guide-list mt-4">
              <li>Открой материал из очереди.</li>
              <li>Проверь текст, ссылки и файлы.</li>
              <li>Открой профиль автора, если нужно больше контекста.</li>
              <li>Прими решение и при необходимости заблокируй пользователя.</li>
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
                <div class="kpi-label">Всего найдено</div>
                <div class="info-value">{{ currentTotal }} материалов</div>
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
                <button class="btn-secondary btn-small" :disabled="page <= 1 || loading" @click="prevPage">
                  Назад
                </button>
                <button class="btn-secondary btn-small" :disabled="page >= totalPages || loading" @click="nextPage">
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'
import AdminActionModal from '../components/AdminActionModal.vue'
import SubmissionCard from '../components/SubmissionCard.vue'
import UserDetailsModal from '../components/UserDetailsModal.vue'

const router = useRouter()

const items = ref([])
const moderationEnabled = ref(true)
const selectedTab = ref('pending')
const searchQuery = ref('')
const quickFilter = ref('all')
const loading = ref(false)
const actionLoading = ref(false)
const page = ref(1)
const pageSize = 20
const currentTotal = ref(0)
const counts = ref({
  pending: 0,
  approved: 0,
  rejected: 0,
})

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

const isCanceledError = (error) => error?.code === 'ERR_CANCELED' || error?.name === 'CanceledError'

const abortActiveRequest = () => {
  if (activeController) {
    activeController.abort()
    activeController = null
  }
}

const createRequestSignal = () => {
  abortActiveRequest()
  activeController = new AbortController()
  return activeController.signal
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

const reloadAll = async () => {
  const signal = createRequestSignal()
  try {
    await Promise.all([loadStats(signal), loadCurrentPage(signal)])
  } catch (error) {
    if (isCanceledError(error)) return
    logout()
  }
}

const reloadPageOnly = async () => {
  const signal = createRequestSignal()
  try {
    await loadCurrentPage(signal)
  } catch (error) {
    if (isCanceledError(error)) return
    logout()
  }
}

const runSearchRefresh = () => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(async () => {
    page.value = 1
    await reloadAll()
  }, 320)
}

const selectTab = async (tabKey) => {
  selectedTab.value = tabKey
  page.value = 1
  await reloadPageOnly()
}

const setQuickFilter = async (filterKey) => {
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
    userDetailsModal.value = {
      open: true,
      details: null,
      loading: false,
    }
    setNotice(e?.response?.data?.detail || 'Не удалось загрузить профиль автора.', 'error')
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
    setNotice(e?.response?.data?.detail || 'Не удалось одобрить материал.', 'error')
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
    setNotice(e?.response?.data?.detail || 'Не удалось отклонить материал.', 'error')
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
    setNotice(e?.response?.data?.detail || 'Не удалось заблокировать пользователя.', 'error')
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
    setNotice(e?.response?.data?.detail || 'Не удалось разблокировать пользователя.', 'error')
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
    setNotice(e?.response?.data?.detail || 'Не удалось переключить режим публикации.', 'error')
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

const logout = () => {
  abortActiveRequest()
  localStorage.removeItem('mn_token')
  router.push('/login')
}

watch(searchQuery, runSearchRefresh)
watch(quickFilter, runSearchRefresh)

onMounted(async () => {
  await reloadAll()
})
</script>
