<template>
  <div id="app">
    <el-container v-if="$route.path !== '/login'">
      <el-header height="60px">
        <div class="header-content">
          <h2>红队指挥控制系统</h2>
          <el-menu mode="horizontal" :default-active="$route.path" router>
            <el-menu-item index="/">Dashboard</el-menu-item>
            <el-menu-item index="/clients">主机列表</el-menu-item>
            <el-menu-item index="/actions">动作日志</el-menu-item>
            <el-menu-item index="/recordings">终端录屏</el-menu-item>
            <el-menu-item index="/pen-test">成果汇总</el-menu-item>
            <el-menu-item index="/ai">AI分析</el-menu-item>
          </el-menu>
          <el-button @click="logout" type="danger" size="small">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}

.el-header {
  background-color: #1a1a2e;
  color: #fff;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 20px;
}

.header-content h2 {
  color: #e94560;
  margin-right: 40px;
}

.el-main {
  background-color: #f5f5f5;
  padding: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #e94560;
}

.stat-label {
  color: #666;
  margin-top: 8px;
}
</style>
