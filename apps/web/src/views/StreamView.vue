<template>
  <div class="shell text-white">
    <div class="surface-grid">
      <section class="panel-strong">
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

      <div class="panel p-5 md:p-6">
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

      <section v-if="featuredItem" class="panel p-5 md:p-6">
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
import { computed, onMounted, ref } from 'vue'
import api from '../api/client'
import SubmissionCard from '../components/SubmissionCard.vue'

const feed = ref([])
const searchQuery = ref('')
const refreshedAt = ref('—')
const quickFilter = ref('all')
const loading = ref(false)

const quickFilters = [
  { key: 'all', label: 'Все' },
  { key: 'withText', label: 'С текстом' },
  { key: 'withMedia', label: 'С файлами' },
  { key: 'withLinks', label: 'Со ссылками' },
]

const load = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/stream/feed')
    feed.value = data
    refreshedAt.value = new Date().toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
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

  return items
})

const featuredItem = computed(() => filteredFeed.value[0] || null)
const withMediaCount = computed(() => feed.value.filter((item) => item.attachments?.length).length)
const withLinksCount = computed(() => feed.value.filter((item) => item.links?.length).length)
const formatDate = (value) => new Date(value).toLocaleString('ru-RU')

onMounted(load)
</script>
