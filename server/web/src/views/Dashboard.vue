<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_clients }}</div>
        <div class="stat-label">总主机数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value online">{{ stats.online_clients }}</div>
        <div class="stat-label">在线主机</div>
      </div>
      <div class="stat-card">
        <div class="stat-value offline">{{ stats.offline_clients }}</div>
        <div class="stat-label">离线主机</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_actions }}</div>
        <div class="stat-label">总动作数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.actions_today }}</div>
        <div class="stat-label">今日动作</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.credentials_found }}</div>
        <div class="stat-label">发现凭证</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dashboard } from '../api/api'

const stats = ref({
  total_clients: 0,
  online_clients: 0,
  offline_clients: 0,
  total_actions: 0,
  actions_today: 0,
  credentials_found: 0
})

const loadStats = async () => {
  try {
    stats.value = await dashboard.getStats()
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard h2 {
  margin-bottom: 20px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}
</style>
