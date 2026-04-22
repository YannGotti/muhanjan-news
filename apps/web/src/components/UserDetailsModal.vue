<template>
  <div
    v-if="open"
    class="fixed inset-0 z-[80] flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm"
    @click.self="$emit('close')"
  >
    <div class="panel w-full max-w-6xl border border-white/10 bg-slate-950/95 p-6 shadow-2xl">
      <div class="flex flex-col gap-6">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="eyebrow">Профиль автора</div>
            <h3 class="mt-3 text-2xl font-semibold tracking-tight text-white">
              {{ details?.user?.twitch_nickname || 'Twitch не указан' }}
            </h3>
            <div class="mt-3 flex flex-wrap gap-2 text-sm text-slate-300">
              <span class="badge">Telegram ID {{ details?.user?.telegram_id }}</span>
              <span class="badge">Username {{ details?.user?.username || 'не указан' }}</span>
              <span class="badge" :class="details?.user?.is_banned ? 'badge-rejected' : 'badge-approved'">
                {{ details?.user?.is_banned ? 'Заблокирован' : 'Активен' }}
              </span>
            </div>
            <div v-if="details?.user?.ban_reason" class="hint-box mt-4 max-w-2xl">
              <div class="hint-title">Причина блокировки</div>
              <div class="hint-text">{{ details.user.ban_reason }}</div>
            </div>
          </div>

          <button class="btn-ghost" @click="$emit('close')">Закрыть</button>
        </div>

        <div v-if="loading" class="panel p-6">
          <div class="text-sm text-slate-300">Загружаю подробности по пользователю...</div>
        </div>

        <template v-else-if="details">
          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div class="kpi">
              <div class="kpi-label">Всего материалов</div>
              <div class="kpi-value">{{ details.stats.total_submissions }}</div>
              <div class="kpi-text">Все отправки пользователя.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Ждут проверки</div>
              <div class="kpi-value">{{ details.stats.pending }}</div>
              <div class="kpi-text">Материалы в очереди.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Одобрено</div>
              <div class="kpi-value">{{ details.stats.approved }}</div>
              <div class="kpi-text">Уже прошли модерацию.</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Отклонено</div>
              <div class="kpi-value">{{ details.stats.rejected }}</div>
              <div class="kpi-text">Не прошли модерацию.</div>
            </div>
          </div>

          <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <section class="panel p-5">
              <div class="sidebar-title">Последние материалы</div>
              <p class="sidebar-text">Здесь видны последние карточки этого автора.</p>

              <div v-if="details.recent_submissions?.length" class="mt-4 grid gap-4">
                <article v-for="item in details.recent_submissions" :key="item.id" class="card-soft">
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="badge">#{{ item.id }}</span>
                    <span class="badge" :class="statusClass(item.status)">{{ statusLabel(item.status) }}</span>
                    <span class="badge">{{ new Date(item.created_at).toLocaleString('ru-RU') }}</span>
                  </div>

                  <div v-if="item.message_text" class="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-200">
                    {{ item.message_text }}
                  </div>
                  <div v-else class="mt-4 text-sm text-slate-400">Без текста</div>

                  <div v-if="item.review_comment" class="hint-box mt-4">
                    <div class="hint-title">Комментарий модератора</div>
                    <div class="hint-text">{{ item.review_comment }}</div>
                  </div>
                </article>
              </div>

              <div v-else class="mt-4 text-sm text-slate-400">
                У пользователя пока нет материалов.
              </div>
            </section>

            <section class="panel p-5">
              <div class="sidebar-title">История действий</div>
              <p class="sidebar-text">Лента модераторских действий по этому автору.</p>

              <div v-if="details.actions?.length" class="mt-4 space-y-3">
                <article v-for="action in details.actions" :key="action.id" class="hint-box">
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="badge">{{ action.action_type }}</span>
                    <span class="badge">Модератор: {{ action.actor_username }}</span>
                    <span class="badge">{{ new Date(action.created_at).toLocaleString('ru-RU') }}</span>
                    <span v-if="action.submission_id" class="badge">Материал #{{ action.submission_id }}</span>
                  </div>

                  <div v-if="action.comment" class="mt-3 text-sm leading-6 text-slate-200">
                    {{ action.comment }}
                  </div>
                </article>
              </div>

              <div v-else class="mt-4 text-sm text-slate-400">
                История действий по пользователю пока пустая.
              </div>
            </section>
          </div>
        </template>

        <div v-else class="text-sm text-slate-400">
          Не удалось загрузить детали по пользователю.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  open: { type: Boolean, default: false },
  details: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

defineEmits(['close'])

const statusLabel = (status) => {
  const labels = {
    pending: 'Ждёт проверки',
    approved: 'Одобрено',
    rejected: 'Отклонено',
  }
  return labels[status] || status
}

const statusClass = (status) => {
  const classes = {
    pending: 'badge-pending',
    approved: 'badge-approved',
    rejected: 'badge-rejected',
  }
  return classes[status] || ''
}
</script>
