<template>
  <nav class="nav">
    <router-link to="/" class="nav-logo">📰 NewsIntel</router-link>
    <router-link to="/">首页</router-link>
    <router-link to="/admin">后台</router-link>
    <router-link to="/login">登录</router-link>
    <span class="nav-search">
      <input v-model="q" @keyup.enter="search" placeholder="搜索新闻..." />
    </span>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const q = ref('')
const router = useRouter()
function search() {
  if (q.value.trim()) router.push({ name: 'Search', query: { q: q.value } })
}
</script>
