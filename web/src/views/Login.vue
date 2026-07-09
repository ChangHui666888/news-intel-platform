<template>
  <div class="login-box">
    <h2 style="text-align:center;margin-bottom:20px">登录</h2>
    <input v-model="email" placeholder="邮箱" type="email" />
    <input v-model="password" placeholder="密码" type="password" />
    <button @click="login">登录</button>
    <p v-if="error" style="color:#dc2626;margin-top:8px">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const email = ref('')
const password = ref('')
const error = ref('')

async function login() {
  try {
    const { data } = await api.login(email.value, password.value)
    localStorage.setItem('token', data.access_token)
    window.location.href = '/'
  } catch (e) {
    error.value = '登录失败'
  }
}
</script>
