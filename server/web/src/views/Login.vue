<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>红队指挥控制系统</h2>
      <el-form @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="密码" prefix-icon="Lock" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-link">
        <el-button link type="primary" @click="showRegister = true">注册新账号</el-button>
      </div>
    </el-card>

    <el-dialog v-model="showRegister" title="注册账号" width="400px">
      <el-form @submit.prevent="handleRegister">
        <el-form-item label="用户名">
          <el-input v-model="regUsername" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="regPassword" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" @click="handleRegister">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { auth } from '../api/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const showRegister = ref(false)
const regUsername = ref('')
const regPassword = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const response = await auth.login(username.value, password.value)
    localStorage.setItem('token', response.access_token)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败：用户名或密码错误')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!regUsername.value || !regPassword.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  try {
    await auth.register(regUsername.value, regPassword.value)
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
    username.value = regUsername.value
    password.value = ''
  } catch (error) {
    ElMessage.error('注册失败：' + (error.response?.data?.detail || '未知错误'))
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-card h2 {
  text-align: center;
  color: #e94560;
  margin-bottom: 30px;
}

.register-link {
  text-align: center;
  margin-top: 10px;
}
</style>
