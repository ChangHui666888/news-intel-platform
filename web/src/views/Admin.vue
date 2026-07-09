<template>
  <div>
    <h2 style="margin-bottom:16px">📊 后台 Dashboard</h2>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px">
      <div class="stat-card"><h3>{{ stats.articles_total }}</h3><small>总文章</small></div>
      <div class="stat-card"><h3>{{ stats.articles_published }}</h3><small>已发布</small></div>
      <div class="stat-card"><h3>{{ stats.users_total }}</h3><small>用户</small></div>
      <div class="stat-card"><h3>{{ stats.ads_active }}</h3><small>活跃广告</small></div>
    </div>

    <div v-if="stats.articles_by_tier" style="margin-bottom:24px">
      <h4>Tier 分布</h4>
      <p v-for="(cnt, tier) in stats.articles_by_tier" :key="tier">
        Tier {{ tier }}: {{ cnt }}篇
      </p>
    </div>

    <h3>📰 文章管理</h3>
    <table style="width:100%;border-collapse:collapse">
      <tr v-for="a in articles" :key="a.id" style="border-bottom:1px solid #eee">
        <td style="padding:6px">{{ a.id }}</td>
        <td>{{ a.title?.substring(0,50) }}</td>
        <td>{{ a.tier }}</td>
        <td><button @click="toggleArticle(a)">{{ a.is_published ? '下架' : '上架' }}</button></td>
        <td><button @click="deleteArticle(a.id)">删除</button></td>
      </tr>
    </table>

    <h3 style="margin-top:24px">📢 广告管理</h3>
    <button @click="showAdForm=!showAdForm">+ 新建广告</button>
    <div v-if="showAdForm" style="margin:12px 0">
      <input v-model="newAd.title" placeholder="标题" style="margin-right:8px" />
      <input v-model="newAd.image_url" placeholder="图片URL" style="margin-right:8px" />
      <input v-model="newAd.link_url" placeholder="链接" style="margin-right:8px" />
      <button @click="createAd">保存</button>
    </div>
    <table style="width:100%;border-collapse:collapse;margin-top:8px">
      <tr v-for="ad in ads" :key="ad.id" style="border-bottom:1px solid #eee">
        <td style="padding:6px">{{ ad.title }}</td>
        <td>{{ ad.position }}</td>
        <td>{{ ad.is_active ? '✅' : '❌' }}</td>
        <td><button @click="toggleAd(ad)">{{ ad.is_active ? '停用' : '启用' }}</button></td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const token = localStorage.getItem('token')

const stats = ref({})
const articles = ref([])
const ads = ref([])
const showAdForm = ref(false)
const newAd = ref({ title: '', image_url: '', link_url: '', position: 'sidebar' })

async function fetch(url, opts = {}) {
  return (await import('axios')).default({ ...opts, url: '/api' + url, headers: { Authorization: 'Bearer ' + token } })
}

onMounted(async () => {
  const [d, a, adsData] = await Promise.all([
    fetch('/admin/dashboard'), fetch('/admin/articles'), fetch('/admin/ads')
  ])
  stats.value = d.data; articles.value = a.data.items; ads.value = adsData.data
})

async function toggleArticle(a) { await fetch(`/admin/articles/${a.id}/toggle`, { method: 'PUT' }); a.is_published = !a.is_published }
async function deleteArticle(id) { await fetch(`/admin/articles/${id}`, { method: 'DELETE' }); articles.value = articles.value.filter(a => a.id !== id) }
async function createAd() { await fetch('/admin/ads', { method: 'POST', data: newAd.value }); showAdForm.value = false; const r = await fetch('/admin/ads'); ads.value = r.data }
async function toggleAd(ad) { await fetch(`/admin/ads/${ad.id}/toggle`, { method: 'PUT' }); ad.is_active = !ad.is_active }
</script>

<style scoped>
.stat-card { background:#fff; padding:16px; border-radius:8px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.1); }
.stat-card h3 { font-size:28px; color:#2563eb; }
button { padding:4px 10px; border:1px solid #ddd; background:#fff; border-radius:4px; cursor:pointer; font-size:12px; }
button:hover { background:#f0f0f0; }
input { padding:4px 8px; border:1px solid #ddd; border-radius:4px; }
</style>
