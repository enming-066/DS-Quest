<script setup>
// Monaco 编辑器封装。
// 加载失败（比如没装依赖）时自动退化成普通 textarea，保证判题功能不会因为它挂掉。
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'cpp' },
  height: { type: Number, default: 420 },
  readOnly: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'submit'])
const container = ref(null)
const fallback = ref(false)
const loading = ref(true)
const editor = shallowRef(null)
let monacoRef = null
let monacoPromise = null

const loadingPromise = (async () => {
  const monaco = await import('monaco-editor')
  const EditorWorker = await import('monaco-editor/esm/vs/editor/editor.worker?worker')
  self.MonacoEnvironment = {
    getWorker() {
      return new EditorWorker.default()
    }
  }
  return monaco
})()

function loadMonaco() {
  if (!monacoPromise) monacoPromise = loadingPromise
  return monacoPromise
}

onMounted(async () => {
  try {
    const monaco = await loadMonaco()
    monacoRef = monaco
    monaco.editor.defineTheme('dsq-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '75719b', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'b39cf8' },
        { token: 'string', foreground: '8fd6a9' },
        { token: 'number', foreground: 'f0b48a' },
        { token: 'type', foreground: '8ec7f0' }
      ],
      colors: {
        'editor.background': '#1c1b2b',
        'editorGutter.background': '#1c1b2b',
        'editor.lineHighlightBackground': '#262338',
        'editorLineNumber.foreground': '#57547a',
        'editorLineNumber.activeForeground': '#a9a4d6',
        'editorCursor.foreground': '#a78bfa',
        'editor.selectionBackground': '#3f3a63',
        'editorIndentGuide.background1': '#2c2942',
        'editorWidget.background': '#232136'
      }
    })

    editor.value = monaco.editor.create(container.value, {
      value: props.modelValue,
      language: props.language,
      theme: 'dsq-dark',
      fontSize: 14,
      fontFamily: '"Cascadia Code", "JetBrains Mono", Consolas, monospace',
      fontLigatures: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 4,
      insertSpaces: true,
      renderLineHighlight: 'line',
      padding: { top: 14, bottom: 14 },
      readOnly: props.readOnly,
      scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10 },
      wordWrap: 'off'
    })

    editor.value.onDidChangeModelContent(() => {
      emit('update:modelValue', editor.value.getValue())
    })

    // Ctrl / Cmd + Enter 直接提交
    editor.value.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      emit('submit')
    })
    loading.value = false
  } catch (err) {
    console.warn('Monaco 加载失败，改用普通输入框', err)
    fallback.value = true
    loading.value = false
  }
})

watch(
  () => props.modelValue,
  (value) => {
    if (editor.value && value !== editor.value.getValue()) {
      editor.value.setValue(value)
    }
  }
)

watch(
  () => props.language,
  (language) => {
    const model = editor.value?.getModel()
    if (model && monacoRef) monacoRef.editor.setModelLanguage(model, language)
  }
)

onBeforeUnmount(() => {
  editor.value?.dispose()
  editor.value = null
})
</script>

<template>
  <div class="editor-wrap" :style="{ height: height + 'px' }">
    <div v-if="loading" class="editor-loading">编辑器加载中…</div>
    <textarea
      v-if="fallback"
      class="editor-fallback"
      :value="modelValue"
      spellcheck="false"
      @input="emit('update:modelValue', $event.target.value)"
      @keydown.ctrl.enter.prevent="emit('submit')"
    ></textarea>
    <div v-show="!fallback" ref="container" class="editor-host"></div>
  </div>
</template>

<style scoped>
.editor-wrap {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #302d48;
  background: #1c1b2b;
}
.editor-host {
  width: 100%;
  height: 100%;
}
.editor-loading {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #8d89b3;
  font-size: 13px;
  background: #1c1b2b;
  z-index: 1;
}
.editor-fallback {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  padding: 14px;
  background: #1c1b2b;
  color: #e6e4f7;
  font-family: var(--font-mono);
  font-size: 14px;
  line-height: 1.7;
  tab-size: 4;
}
</style>
