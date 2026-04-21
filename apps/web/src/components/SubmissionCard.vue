<template>
  <article class="card">
    <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
      <div class="space-y-3">
        <div class="flex flex-wrap items-center gap-2">
          <span class="badge" :class="statusClass">{{ statusLabel }}</span>
          <span class="badge">Материал #{{ item.id }}</span>
          <span class="badge">{{ attachmentLabel }}</span>
          <span v-if="item.links?.length" class="badge">Есть ссылки</span>
          <span v-if="item.message_text" class="badge">Есть текст</span>
          <span v-if="item.user?.is_banned" class="badge badge-rejected">Автор заблокирован</span>
        </div>

        <div>
          <h3 class="text-xl font-semibold text-white">
            {{ item.user?.twitch_nickname || 'Twitch не указан' }}
          </h3>

          <div class="mt-2 flex flex-wrap gap-2 text-sm text-zinc-400">
            <span class="badge">
              Telegram: {{ item.user?.username || item.user?.first_name || item.user?.telegram_id }}
            </span>
            <span class="badge">ID {{ item.user?.telegram_id }}</span>
          </div>
        </div>
      </div>

      <div class="space-y-2 text-left xl:text-right">
        <div class="text-sm text-zinc-300">{{ formattedDate }}</div>
        <div v-if="item.review_comment" class="hint-box max-w-[320px] text-left">
          <div class="hint-title">Комментарий модератора</div>
          <div class="hint-text">{{ item.review_comment }}</div>
        </div>
        <div v-if="item.user?.ban_reason" class="hint-box max-w-[320px] text-left">
          <div class="hint-title">Причина блокировки</div>
          <div class="hint-text">{{ item.user.ban_reason }}</div>
        </div>
      </div>
    </div>

    <section v-if="item.message_text" class="content-block">
      <div class="content-block-head">
        <div>
          <div class="content-block-label">Текст сообщения</div>
          <div class="content-block-tip">Это текст, который отправил пользователь.</div>
        </div>

        <button
          type="button"
          class="btn-ghost btn-small"
          title="Скопировать текст сообщения"
          @click="copyMessageText"
        >
          {{ copiedText ? 'Скопировано' : 'Копировать текст' }}
        </button>
      </div>

      <div class="preview-text whitespace-pre-wrap">
        {{ item.message_text }}
      </div>
    </section>

    <section v-if="item.links?.length" class="space-y-3">
      <div class="section-title-row">
        <div>
          <div class="content-block-label">Ссылки</div>
          <div class="content-block-tip">Открываются в новой вкладке.</div>
        </div>
      </div>

      <div class="grid gap-3 lg:grid-cols-2">
        <div v-for="link in item.links" :key="link" class="link-wrap">
          <a
            :href="link"
            target="_blank"
            rel="noreferrer"
            class="link-tile break-all"
          >
            {{ link }}
          </a>

          <button
            type="button"
            class="btn-ghost btn-small mt-2"
            title="Скопировать ссылку"
            @click="copyLink(link)"
          >
            {{ copiedLink === link ? 'Скопировано' : 'Копировать ссылку' }}
          </button>
        </div>
      </div>
    </section>

    <section v-if="item.attachments?.length" class="space-y-3">
      <div class="section-title-row">
        <div>
          <div class="content-block-label">Вложения</div>
          <div class="content-block-tip">Изображения можно открыть, остальные файлы — скачать.</div>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
        <div v-for="att in item.attachments" :key="att.id" class="media-tile">
          <template v-if="isImage(att) && resolveAttachmentUrl(att)">
            <a :href="resolveAttachmentUrl(att)" target="_blank" rel="noreferrer" class="media-preview-link">
              <img
                :src="resolveAttachmentUrl(att)"
                :alt="att.original_name || 'attachment'"
                class="media-preview"
                loading="lazy"
              />
            </a>
          </template>

          <div v-else class="media-placeholder">
            <div class="media-placeholder-icon">
              {{ fileTypeLabel(att) }}
            </div>
            <div class="media-placeholder-name">{{ att.original_name || 'Файл' }}</div>
          </div>

          <div class="media-meta">
            <div>
              <div class="font-medium break-words text-white">{{ att.original_name || 'Вложение' }}</div>
              <div class="mt-1 text-xs text-zinc-400">
                {{ att.mime_type || att.file_type || 'Файл' }}
                <span v-if="att.file_size">· {{ formatFileSize(att.file_size) }}</span>
              </div>
            </div>

            <div v-if="resolveAttachmentUrl(att)" class="flex flex-wrap gap-2">
              <a
                :href="resolveAttachmentUrl(att)"
                target="_blank"
                rel="noreferrer"
                class="btn-secondary btn-small"
                title="Открыть вложение"
              >
                Открыть
              </a>

              <a
                :href="resolveDownloadUrl(att)"
                :download="att.original_name || true"
                class="btn-primary btn-small"
                title="Скачать вложение"
              >
                Скачать
              </a>
            </div>

            <div v-else class="text-sm text-zinc-500">
              Ссылка на файл пока недоступна.
            </div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showActions" class="action-panel">
      <div class="action-panel-text">
        <div class="font-medium text-white">Решение по материалу</div>
        <div class="text-sm text-zinc-400">
          Сначала проверь текст и вложения, затем выбери одно действие.
        </div>
      </div>

      <div class="flex flex-wrap gap-3">
        <button
          v-if="item.status === 'pending'"
          class="btn-primary"
          title="Одобрить материал и отправить его в эфирную ленту"
          @click="$emit('approve', item)"
        >
          Одобрить
        </button>
        <button
          v-if="item.status === 'pending'"
          class="btn-danger"
          title="Отклонить материал с причиной"
          @click="$emit('reject', item)"
        >
          Отклонить
        </button>
        <button
          v-if="!item.user?.is_banned"
          class="btn-secondary"
          title="Заблокировать пользователя"
          @click="$emit('ban', item.user)"
        >
          Заблокировать автора
        </button>
        <button
          v-else
          class="btn-secondary"
          title="Снять блокировку пользователя"
          @click="$emit('unban', item.user)"
        >
          Разблокировать автора
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  showActions: { type: Boolean, default: false },
})

defineEmits(['approve', 'reject', 'ban', 'unban'])

const copiedText = ref(false)
const copiedLink = ref('')
let copiedTextTimeout = null
let copiedLinkTimeout = null

const statusLabelMap = {
  pending: 'Ждёт проверки',
  approved: 'Одобрено',
  rejected: 'Отклонено',
}

const statusClassMap = {
  pending: 'badge-pending',
  approved: 'badge-approved',
  rejected: 'badge-rejected',
}

const statusLabel = computed(() => statusLabelMap[props.item.status] || props.item.status)
const statusClass = computed(() => statusClassMap[props.item.status] || '')
const attachmentLabel = computed(() => `${props.item.attachments?.length || 0} вложений`)
const formattedDate = computed(() => new Date(props.item.created_at).toLocaleString('ru-RU'))

const isImage = (att) => String(att?.mime_type || '').startsWith('image/')

const resolveAttachmentUrl = (att) => att?.public_url || att?.download_url || null
const resolveDownloadUrl = (att) => att?.download_url || att?.public_url || null

const fileTypeLabel = (att) => {
  const map = {
    document: 'DOC',
    audio: 'AUD',
    voice: 'VOICE',
    video: 'VID',
    animation: 'GIF',
    photo: 'IMG',
  }
  return map[att?.file_type] || 'FILE'
}

const formatFileSize = (bytes) => {
  if (!bytes && bytes !== 0) return ''
  if (bytes < 1024) return `${bytes} Б`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`
}

const copyToClipboard = async (value) => {
  try {
    await navigator.clipboard.writeText(value)
    return true
  } catch {
    window.prompt('Скопируй вручную:', value)
    return false
  }
}

const copyMessageText = async () => {
  if (!props.item?.message_text) return
  const ok = await copyToClipboard(props.item.message_text)
  if (!ok) return

  copiedText.value = true
  clearTimeout(copiedTextTimeout)
  copiedTextTimeout = setTimeout(() => {
    copiedText.value = false
  }, 1800)
}

const copyLink = async (link) => {
  const ok = await copyToClipboard(link)
  if (!ok) return

  copiedLink.value = link
  clearTimeout(copiedLinkTimeout)
  copiedLinkTimeout = setTimeout(() => {
    copiedLink.value = ''
  }, 1800)
}
</script>
