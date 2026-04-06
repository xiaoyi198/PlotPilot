<template>
  <div class="autopilot-monitor-page">
    <AutopilotDashboard :novel-id="novelId" @status-change="handleStatusChange" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AutopilotDashboard from '../components/autopilot/AutopilotDashboard.vue'

const route = useRoute()
const novelId = computed(() => route.params.slug as string)

function handleStatusChange(status: any) {
  console.log('Autopilot status changed:', status)
}
</script>

<style scoped>
.autopilot-monitor-page {
  min-height: 100vh;
  background: #0a0a0a;
}
</style>
