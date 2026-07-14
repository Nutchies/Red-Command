<template>
  <div class="actions">
    <h2>动作日志</h2>
    <div v-for="action in filteredActions" :key="action.id" class="action-item">
      <div class="action-header">
        <span class="action-type" :class="action.action_type">{{ action.action_type === 'realtime_command' ? '命令' : action.action_type }}</span>
        <span class="action-time">{{ formatTime(action.timestamp) }}</span>
        <span class="action-hostname">{{ action.client_hostname }}</span>
      </div>
      <div class="action-content">
        <pre>{{ action.content }}</pre>
      </div>
      <div v-if="action.result" class="action-result">
        <pre>{{ action.result }}</pre>
      </div>
      <div v-if="action.exit_code !== undefined && action.exit_code !== null" class="action-exit">
        退出码: {{ action.exit_code }}
      </div>
    </div>
    <div v-if="filteredActions.length === 0" class="empty">
      暂无记录
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { actions, clients } from '../api/api'

const route = useRoute()
const allActions = ref([])

const filteredActions = computed(() => {
  return allActions.value.filter(action => action.action_type !== 'collect')
})

const loadActions = async () => {
  try {
    const clientId = route.query.client_id
    if (clientId) {
      allActions.value = await clients.getActions(clientId)
    } else {
      allActions.value = await actions.getAll()
    }
  } catch (error) {
    console.error('Failed to load actions:', error)
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadActions()
})
</script>

<style scoped>
.actions {
  padding: 20px;
}

.actions h2 {
  margin-bottom: 20px;
  color: #333;
}

.action-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.action-header {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.action-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.action-type.realtime_command {
  background-color: #409eff;
  color: white;
}

.action-type.command {
  background-color: #67c23a;
  color: white;
}

.action-type.collect {
  display: none;
}

.action-time {
  color: #999;
  font-size: 12px;
}

.action-hostname {
  color: #666;
  font-size: 12px;
  margin-left: auto;
}

.action-content pre {
  margin: 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-all;
}

.action-result pre {
  margin: 10px 0 0 0;
  padding: 10px;
  background-color: #f0f9eb;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-all;
}

.action-exit {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
