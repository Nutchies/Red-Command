<template>
  <div class="recordings">
    <h2>终端录制回放</h2>
    
    <el-table :data="videos" style="width: 100%" @row-click="playVideo">
      <el-table-column prop="session_id" label="会话ID" />
      <el-table-column prop="file_size" label="文件大小">
        <template #default="scope">
          {{ formatSize(scope.row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="时长">
        <template #default="scope">
          {{ formatDuration(scope.row.duration) }}
        </template>
      </el-table-column>
      <el-table-column prop="timestamp" label="时间">
        <template #default="scope">
          {{ formatTime(scope.row.timestamp) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button @click.stop="playVideo(scope.row)" type="primary" size="small">播放</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="终端录屏回放" width="800px">
      <div ref="playerContainer" class="player-container"></div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { videos as videosApi } from '../api/api';
const route = useRoute();
const videos = ref([]);
const dialogVisible = ref(false);
const playerContainer = ref(null);
const clientId = route.query.client_id;
const loadVideos = async () => {
 if (!clientId)
 return;
 try {
 videos.value = await videosApi.getByClient(clientId);
 }
 catch (error) {
 console.error('Failed to load videos:', error);
 }
};
const formatSize = (bytes) => {
 if (!bytes)
 return '0 B';
 const k = 1024;
 const sizes = ['B', 'KB', 'MB', 'GB'];
 const i = Math.floor(Math.log(bytes) / Math.log(k));
 return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
const formatDuration = (seconds) => {
 if (!seconds)
 return '--';
 const mins = Math.floor(seconds / 60);
 const secs = Math.floor(seconds % 60);
 return `${mins}:${secs.toString().padStart(2, '0')}`;
};
const formatTime = (timestamp) => {
 if (!timestamp)
 return '--';
 return new Date(timestamp * 1000).toLocaleString();
};
const playVideo = async (video) => {
 dialogVisible.value = true;
 await new Promise(resolve => setTimeout(resolve, 100));
 const container = playerContainer.value;
 container.innerHTML = '<div class="loading">加载中...</div>';
 try {
 const response = await videosApi.download(video.id);
 const blob = response.data;
 const reader = new FileReader();
 reader.onload = async (e) => {
 const encryptedData = new Uint8Array(e.target.result);
 const decryptedData = decrypt(encryptedData, video.nonce);
 const castContent = new TextDecoder().decode(decryptedData);
 renderPlayer(container, castContent);
 };
 reader.readAsArrayBuffer(blob);
 }
 catch (error) {
 container.innerHTML = '<div class="error">加载失败: ' + error.message + '</div>';
 }
};
const decrypt = (encrypted, nonceBase64) => {
 const key = new TextEncoder().encode('redteam2024!@#$%^&*()_+-=[]{}|;\':\",./<>?'.substring(0, 32));
 const nonce = base64ToBytes(nonceBase64);
 const algorithm = { name: 'AES-GCM', iv: nonce };
 return crypto.subtle.decrypt(algorithm, key, encrypted);
};
const base64ToBytes = (base64) => {
 const binaryString = atob(base64);
 const bytes = new Uint8Array(binaryString.length);
 for (let i = 0; i < binaryString.length; i++) {
 bytes[i] = binaryString.charCodeAt(i);
 }
 return bytes;
};
const renderPlayer = (container, castContent) => {
 container.innerHTML = `
 <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/asciinema-player/3.0.1/asciinema-player.min.css">
 <div id="asciinema-player"></div>
 <script src="https://cdnjs.cloudflare.com/ajax/libs/asciinema-player/3.0.1/asciinema-player.min.js"></script>
 <script>
 const player = asciinemaPlayer.create('#asciinema-player', ${JSON.stringify(castContent)}, {
 autoPlay: true,
 speed: 1,
 theme: 'dark'
 });
 </script>
 `;
};
onMounted(() => {
 loadVideos();
});
onUnmounted(() => {
});
</script>

<style scoped>
.recordings {
  padding: 20px;
}

.recordings h2 {
  margin-bottom: 20px;
  color: #333;
}

.player-container {
  width: 100%;
  height: 400px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.loading {
  color: #fff;
  text-align: center;
  padding: 20px;
}

.error {
  color: #ff4d4f;
  text-align: center;
  padding: 20px;
}
</style>
