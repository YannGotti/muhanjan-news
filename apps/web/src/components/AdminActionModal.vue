<template>
  <div
    v-if="open"
    class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
    @click.self="$emit('close')"
  >
    <div class="panel w-full max-w-xl border border-white/10 bg-slate-950/95 p-6 shadow-2xl">
      <div class="space-y-3">
        <div class="eyebrow">Действие модератора</div>
        <h3 class="text-2xl font-semibold tracking-tight text-white">
          {{ title }}
        </h3>
        <p v-if="description" class="text-sm leading-7 text-slate-400">
          {{ description }}
        </p>
      </div>

      <div v-if="withInput" class="mt-6 space-y-3">
        <label class="field-label">{{ inputLabel }}</label>
        <textarea
          v-model="modelValue"
          class="input min-h-[150px] resize-y"
          :placeholder="placeholder"
        />
      </div>

      <div class="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button class="btn-ghost" :disabled="loading" @click="$emit('close')">
          Отмена
        </button>
        <button
          class="btn-primary"
          :class="danger ? 'btn-danger' : 'btn-primary'"
          :disabled="loading || (required && withInput && !modelValue.trim())"
          @click="$emit('submit', modelValue.trim())"
        >
          {{ loading ? 'Сохраняю...' : submitText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  submitText: { type: String, default: 'Сохранить' },
  placeholder: { type: String, default: '' },
  inputLabel: { type: String, default: 'Комментарий' },
  initialValue: { type: String, default: '' },
  withInput: { type: Boolean, default: true },
  required: { type: Boolean, default: false },
  danger: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})

defineEmits(['close', 'submit'])

const modelValue = ref('')

watch(
  () => [props.open, props.initialValue],
  () => {
    modelValue.value = props.initialValue || ''
  },
  { immediate: true },
)
</script>
