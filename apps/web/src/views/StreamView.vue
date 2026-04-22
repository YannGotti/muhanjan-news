<template>
  <div class="shell text-white" :class="{ 'obs-shell': isCleanMode }">
    <div class="surface-grid" :class="{ 'obs-grid': isCleanMode }">
      <section v-if="!isCleanMode" class="panel-strong">
        <div class="hero-glow"></div>

        <div class="relative z-[1] flex flex-col gap-6">
          <div class="topbar">
            <div class="space-y-4">
              <span class="eyebrow">MuhanjanNews · Эфирная лента</span>

              <div class="max-w-4xl">
                <h1 class="surface-title">Одобренные материалы для стрима</h1>
                <p class="surface-subtitle">
                  Здесь только то, что уже прошло модерацию. Экран чистый, без лишней навигации и без служебного шума.
                </p>
              </div>

              <div class="meta-strip">
                <span class="badge badge-approved">Показываются только одобренные материалы</span>
                <span class="meta-chip">{{ filteredFeed.length }} карточек</span>
                <span class="meta-chip">{{ withMediaCount }} с файлами</span>
                <span class="meta-chip">{{ withLinksCount }} со ссылками</span>
              </div>
            </div>

            <div class="topbar-actions">
              <router-link to="/admin" class="btn-secondary">Вернуться в модерацию</router-link>
              <button class="btn-secondary" :disabled="loading" @click="load">
                {{ loading ? 'Обновление...' : 'Обновить' }}
              </button>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div class="kpi">
              <div class="kpi-label">На экране</div>
              <div class="kpi-value">{{ filteredFeed.length }}</div>
              <div class="kpi-text">Столько карточек проходит через текущие фильтры.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">С файлами</div>
              <div class="kpi-value">{{ withMediaCount }}</div>
              <div class="kpi-text">Карточки, где есть вложения.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Со ссылками</div>
              <div class="kpi-value">{{ withLinksCount }}</div>
              <div class="kpi-text">Карточки, где есть ссылки.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Последнее обновление</div>
              <div class="kpi-value text-[1.6rem]">{{ refreshedAt }}</div>
              <div class="kpi-text">Время последней загрузки ленты.</div>
            </div>
          </div>
        </div>
      </section>

      <div v-if="!isCleanMode" class="panel p-5 md:p-6">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div class="sidebar-title">Фильтры ленты</div>
            <p class="sidebar-text">
              Можно быстро найти карточки по тексту или отобрать только материалы с файлами или ссылками.
            </p>
          </div>

          <div class="flex flex-col gap-3 lg:items-end">
            <input
              v-model="searchQuery"
              class="input min-w-[280px]"
              placeholder="Поиск по тексту, нику или ссылке"
            />

            <div class="flex flex-wrap gap-2">
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
          </div>
        </div>
      </div>

      <section v-if="!isCleanMode && featuredItem" class="panel p-5 md:p-6">
        <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="eyebrow">Первый материал в ленте</div>
            <h2 class="mt-3 text-2xl font-semibold tracking-tight text-white md:text-3xl">
              {{ featuredItem.user?.twitch_nickname || 'Без Twitch-ника' }}
            </h2>
            <p class="mt-3 max-w-4xl text-sm leading-7 text-slate-300">
              {{ featuredItem.message_text || 'У материала нет текста. Ниже можно открыть карточку и посмотреть вложения.' }}
            </p>
          </div>

          <div class="space-y-2 text-left lg:text-right">
            <div class="meta-chip">Материал #{{ featuredItem.id }}</div>
            <div class="text-sm text-slate-400">{{ formatDate(featuredItem.created_at) }}</div>
          </div>
        </div>
      </section>

      <section v-if="loading" class="panel p-6">
        <div class="text-sm text-slate-300">Загружаю эфирную ленту...</div>
      </section>

      <section v-else-if="isObsMode && currentObsItem" class="obs-stage">
        <div class="obs-meta">
          <span class="obs-chip">Эфирный режим</span>
          <span class="obs-chip">Материал #{{ currentObsItem.id }}</span>
          <span class="obs-chip">{{ currentObsItem.user?.twitch_nickname || 'Без Twitch-ника' }}</span>
        </div>

        <SubmissionCard :item="currentObsItem" />

        <div v-if="obsRotationEnabled" class="obs-footer">
          Автопереключение каждые {{ rotationIntervalSeconds }} сек. · Автообновление каждые {{ refreshIntervalSeconds }} сек.
        </div>
      </section>

      <section v-else-if="filteredFeed.length" class="grid gap-4">
        <SubmissionCard v-for="item in filteredFeed" :key="item.id" :item="item" />
      </section>

      <section v-else class="empty-state">
        <div class="empty-icon">○</div>
        <h2 class="text-2xl font-semibold text-white">Лента пока пустая</h2>
        <p class="mt-2 text-sm leading-6 text-slate-400">
          Когда появятся одобренные материалы, они покажутся здесь.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/client'
import SubmissionCard from '../components/SubmissionCard.vue'

const route = useRoute()

const feed = ref([])
const searchQuery = ref('')
const refreshedAt = ref('—')
const quickFilter = ref('all')
const loading = ref(false)
const rotationIndex = ref(0)

let refreshTimer = null
let rotationTimer = null

const quickFilters = [
  { key: 'all', label: 'Все' },
  { key: 'withText', label: 'С текстом' },
  { key: 'withMedia', label: 'С файлами' },
  { key: 'withLinks', label: 'Со ссылками' },
]

const parseBool = (value) => ['1', 'true', 'yes', 'on'].includes(String(value || '').toLowerCase())
const clamp = (value, min, max, fallback) => {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return fallback
  return Math.min(max, Math.max(min, Math.floor(numeric)))
}

const isObsMode = computed(() => parseBool(route.query.obs) || parseBool(route.query.live))
const isCleanMode = computed(() => isObsMode.value || parseBool(route.query.clean))
const obsRotationEnabled = computed(() => parseBool(route.query.rotate) || isObsMode.value)
const refreshIntervalSeconds = computed(() => clamp(route.query.refresh, 5, 300, isObsMode.value ? 15 : 30))
const rotationIntervalSeconds = computed(() => clamp(route.query.interval, 3, 120, 12))
const queryLimit = computed(() => clamp(route.query.limit, 1, 300, 100))
const obsOnlyMedia = computed(() => parseBool(route.query.only_media))
const obsOnlyLinks = computed(() => parseBool(route.query.only_links))

const load = async () => {
  loading.value = true
  try {
    const { data } = await api.get(`/stream/feed?limit=${queryLimit.value}`)
    feed.value = data
    if (rotationIndex.value >= data.length) {
      rotationIndex.value = 0
    }
    refreshedAt.value = new Date().toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
      second: isObsMode.value ? '2-digit' : undefined,
    })
  } finally {
    loading.value = false
  }
}

const filteredFeed = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()

  let items = feed.value.filter((item) => {
    const haystack = [
      item?.user?.twitch_nickname,
      item?.user?.username,
      item?.user?.first_name,
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

  if (obsOnlyMedia.value) {
    items = items.filter((item) => item?.attachments?.length)
  }

  if (obsOnlyLinks.value) {
    items = items.filter((item) => item?.links?.length)
  }

  return items
})

const featuredItem = computed(() => filteredFeed.value[0] || null)
const currentObsItem = computed(() => {
  if (!filteredFeed.value.length) return null
  return filteredFeed.value[rotationIndex.value % filteredFeed.value.length]
})
const withMediaCount = computed(() => feed.value.filter((item) => item.attachments?.length).length)
const withLinksCount = computed(() => feed.value.filter((item) => item.links?.length).length)
const formatDate = (value) => new Date(value).toLocaleString('ru-RU')

const restartRefreshTimer = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(() => {
    load()
  }, refreshIntervalSeconds.value * 1000)
}

const restartRotationTimer = () => {
  if (rotationTimer) clearInterval(rotationTimer)
  if (!obsRotationEnabled.value) return

  rotationTimer = setInterval(() => {
    if (!filteredFeed.value.length) return
    rotationIndex.value = (rotationIndex.value + 1) % filteredFeed.value.length
  }, rotationIntervalSeconds.value * 1000)
}

watch(
  () => [route.query.obs, route.query.live, route.query.clean, route.query.rotate, route.query.interval, route.query.refresh, route.query.limit, route.query.only_media, route.query.only_links],
  async () => {
    await load()
    restartRefreshTimer()
    restartRotationTimer()
  },
)

watch(filteredFeed, (items) => {
  if (!items.length) {
    rotationIndex.value = 0
    return
  }
  if (rotationIndex.value >= items.length) {
    rotationIndex.value = 0
  }
})

onMounted(async () => {
  await load()
  restartRefreshTimer()
  restartRotationTimer()
})

onBeforeUnmount(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (rotationTimer) clearInterval(rotationTimer)
})
</script>

<style scoped>
.obs-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.06), transparent 30%),
    linear-gradient(180deg, #050816 0%, #02040b 100%);
}

.obs-grid {
  gap: 0;
}

.obs-stage {
  display: grid;
  gap: 1rem;
  min-height: calc(100vh - 3rem);
  align-content: start;
}

.obs-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.obs-chip {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(15, 23, 42, 0.72);
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  font-size: 0.82rem;
  color: rgba(226, 232, 240, 0.88);
}

.obs-footer {
  color: rgba(148, 163, 184, 0.9);
  font-size: 0.85rem;
}
</style>
