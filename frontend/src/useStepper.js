import { onBeforeUnmount, ref } from 'vue'

// 三套可视化共用的"步骤播放器"：上一帧 / 下一帧 / 自动播放。
export function useStepper(interval = 900) {
  const steps = ref([])
  const index = ref(0)
  const playing = ref(false)
  let timer = null

  function stop() {
    playing.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function setSteps(list) {
    stop()
    steps.value = list
    index.value = 0
  }

  function go(i) {
    index.value = Math.min(Math.max(i, 0), Math.max(0, steps.value.length - 1))
  }

  function next() {
    if (index.value < steps.value.length - 1) index.value += 1
    else stop()
  }

  function prev() {
    index.value = Math.max(0, index.value - 1)
  }

  function play() {
    if (!steps.value.length) return
    if (index.value >= steps.value.length - 1) index.value = 0
    playing.value = true
    if (timer) clearInterval(timer)
    timer = setInterval(() => {
      if (index.value >= steps.value.length - 1) stop()
      else index.value += 1
    }, interval)
  }

  onBeforeUnmount(stop)

  return { steps, index, playing, setSteps, go, next, prev, play, stop }
}
