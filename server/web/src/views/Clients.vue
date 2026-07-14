<template>
  <div class="clients">
    <h2>主机列表</h2>
    <el-table :data="clients" style="width: 100%">
      <el-table-column prop="hostname" label="主机名" />
      <el-table-column prop="ip" label="IP地址" />
      <el-table-column prop="client_id" label="Client ID" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'online' ? 'success' : 'danger'">
            {{ scope.row.status === 'online' ? '在线' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_heartbeat" label="最后心跳" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button @click="viewActions(scope.row.client_id)" type="primary" size="small">查看动作</el-button>
          <el-button @click="viewRecordings(scope.row.client_id)" type="success" size="small">查看录屏</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { clients } from '../api/api'

const router = useRouter()
const clients = ref([])

const loadClients = async () => {
  try {
    clients.value = await clients.getAll()
  } catch (error) {
    console.error('Failed to load clients:', error)
  }
}

const viewActions = (clientId) => {
  router.push(`/actions?client_id=${clientId}`)
}

const viewRecordings = (clientId) => {
  router.push(`/recordings?client_id=${clientId}`)
}

onMounted(() => {
  loadClients()
})
</script>

<style scoped>
.clients {
  padding: 20px;
}

.clients h2 {
  margin-bottom: 20px;
  color: #333;
}
</style>
