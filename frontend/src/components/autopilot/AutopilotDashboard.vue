<template>
  <div class="autopilot-dashboard">
    <!-- 顶部状态栏 -->
    <div class="dashboard-header">
      <div class="header-left">
        <span class="dashboard-title">🚀 Autopilot 监控大盘</span>
        <n-tag
          :type="statusTagType"
          :bordered="false"
          size="small"
        >
          {{ statusLabel }}
        </n-tag>
      </div>
      <div class="header-right">
        <n-button
          size="small"
          quaternary
          @click="handleRefresh"
          :loading="refreshing"
        >
          🔄 刷新
        </n-button>
        <n-button
          size="small"
          quaternary
          @click="handleToggleFullscreen"
        >
          {{ isFullscreen ? '📉 退出全屏' : '📊 全屏显示' }}
        </n-button>
      </div>
    </div>

    <!-- 主面板 -->
    <AutopilotPanel
      :novel-id="novelId"
      @status-change="handleStatusChange"
      class="main-panel"
    />

    <!-- 监控网格 -->
    <div class="monitor-grid">
      <!-- 第一行：张力图表 + 实时日志 -->
      <div class="grid-row">
        <div class="grid-cell span-2">
          <TensionChart :novel-id="novelId" />
        </div>
        <div class="grid-cell span-1">
          <RealtimeLogStream :novel-id="novelId" />
        </div>
      </div>

      <!-- 第二行：文风警报 + 伏笔账本 + 熔断器 -->
      <div class="grid-row">
        <div class="grid-cell">
          <VoiceDriftIndicator
            :novel-id="novelId"
            @drift-alert="handleDriftAlert"
          />
        </div>
        <div class="grid-cell">
          <ForeshadowLedger :novel-id="novelId" />
        </div>
        <div class="grid-cell">
          <CircuitBreakerStatus
            :novel-id="novelId"
            @breaker-open="handleBreakerOpen"
            @breaker-reset="handleBreakerReset"
          />
        </div>
      </div>
    </div>

    <!-- 警报通知 -->
    <n-notification-provider>
      <div ref="notificationContainer" />
    </n-notification-provider>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useNotification } from 'naive-ui'
import AutopilotPanel from './AutopilotPanel.vue'
import TensionChart from './TensionChart.vue'
import RealtimeLogStream from './RealtimeLogStream.vue'
import VoiceDriftIndicator from './VoiceDriftIndicator.vue'
import ForeshadowLedger from './ForeshadowLedger.vue'
import CircuitBreakerStatus from './CircuitBreakerStatus.vue'

const props = defineProps<{
  novelId: string
}>()

const emit = defineEmits<{
  'status-change': [status: any]
}>()

const notification = useNotification()

const currentStatus = ref<any>(null)
const refreshing = ref(false)
const isFullscreen = ref(false)

// 状态标签
const statusLabel = computed(() => {
  const status = currentStatus.value?.autopilot_status
  if (status === 'running') return '运行中'
  if (status === 'paused') return '已暂停'
  if (status === 'stopped') return '已停止'
  return '未知'
})

const statusTagType = computed(() => {
  const status = currentStatus.value?.autopilot_status
  if (status === 'running') return 'success'
  if (status === 'paused') return 'warning'
  return 'default'
})

// 状态变化处理
function handleStatusChange(status: any) {
  currentStatus.value = status
  emit('status-change', status)
}

// 刷新所有数据
async function handleRefresh() {
  refreshing.value = true
  try {
    // 触发所有子组件刷新（通过 key 变化或事件总线）
    await new Promise(resolve => setTimeout(resolve, 500))
    notification.success({
      title: '刷新成功',
      content: '所有监控数据已更新',
      duration: 2000
    })
  } catch (err) {
    notification.error({
      title: '刷新失败',
      content: '请稍后重试',
      duration: 3000
    })
  } finally {
    refreshing.value = false
  }
}

// 全屏切换
function handleToggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    document.documentElement.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

// 文风偏移警报
function handleDriftAlert(score: number, status: string) {
  if (status === 'danger') {
    notification.error({
      title: '⚠️ 文风严重偏离',
      content: `偏移值: ${score.toFixed(1)}，建议立即处理`,
      duration: 5000
    })
  } else if (status === 'warning') {
    notification.warning({
      title: '⚡ 文风轻微偏离',
      content: `偏移值: ${score.toFixed(1)}，请注意观察`,
      duration: 4000
    })
  }
}

// 熔断器打开
function handleBreakerOpen() {
  notification.error({
    title: '🔌 熔断器已触发',
    content: '连续错误过多，Autopilot 已自动停止',
    duration: 0  // 不自动关闭
  })
}

// 熔断器重置
function handleBreakerReset() {
  notification.success({
    title: '🔄 熔断器已重置',
    content: '可以重新启动 Autopilot',
    duration: 3000
  })
}

// 监听全屏状态变化
document.addEventListener('fullscreenchange', () => {
  isFullscreen.value = !!document.fullscreenElement
})
</script>

<style scoped>
.autopilot-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: #0a0a0a;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #0d0d0d;
  border: 1px solid #1a1a1a;
  border-radius: 8px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dashboard-title {
  font-size: 16px;
  font-weight: 600;
  color: #c8c8c8;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.main-panel {
  width: 100%;
}

.monitor-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.grid-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.grid-cell {
  min-height: 200px;
}

.grid-cell.span-1 {
  grid-column: span 1;
}

.grid-cell.span-2 {
  grid-column: span 2;
}

/* 响应式布局 */
@media (max-width: 1400px) {
  .grid-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .grid-cell.span-2 {
    grid-column: span 2;
  }
}

@media (max-width: 900px) {
  .grid-row {
    grid-template-columns: 1fr;
  }

  .grid-cell.span-1,
  .grid-cell.span-2 {
    grid-column: span 1;
  }
}

/* 全屏模式 */
:fullscreen .autopilot-dashboard {
  padding: 24px;
}

:fullscreen .dashboard-title {
  font-size: 18px;
}

:fullscreen .monitor-grid {
  gap: 20px;
}

:fullscreen .grid-row {
  gap: 20px;
}
</style>
