<template>
  <div class="ai-analysis">
    <h2>AI分析</h2>
    <div class="analysis-content">
      <el-table :data="extractedInfo" style="width: 100%">
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="content" label="内容" />
        <el-table-column prop="source" label="来源" />
        <el-table-column prop="extracted_at" label="提取时间" />
      </el-table>
    </div>
    <div v-if="extractedInfo.length === 0" class="empty">
      暂无分析数据
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ai } from '../api/api'

const extractedInfo = ref([])

const loadExtracted = async () => {
  try {
    extractedInfo.value = await ai.getExtracted()
  } catch (error) {
    console.error('Failed to load extracted info:', error)
  }
}

onMounted(() => {
  loadExtracted()
})
</script>

<style scoped>
.ai-analysis {
  padding: 20px;
}

.ai-analysis h2 {
  margin-bottom: 20px;
  color: #333;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
