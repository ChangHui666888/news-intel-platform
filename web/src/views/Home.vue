<template>
  <div>
    <div class="tag-cloud">
      <router-link v-for="cat in categories" :key="cat.name" :to="`/category/${cat.name}`">
        {{ cat.name }} ({{ cat.count }})
      </router-link>
    </div>

    <h2 style="margin-bottom:12px">🔥 热门新闻</h2>
    <NewsCard v-for="a in hot" :key="a.id" :article="a" />

    <h2 style="margin:24px 0 12px">🕐 最新新闻</h2>
    <NewsCard v-for="a in latest" :key="a.id" :article="a" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import NewsCard from '../components/NewsCard.vue'

const categories = ref([])
const hot = ref([])
const latest = ref([])

onMounted(async () => {
  const [c, h, l] = await Promise.all([
    api.getCategories(), api.getHot(10), api.getLatest(20)
  ])
  categories.value = c.data
  hot.value = h.data
  latest.value = l.data
})
</script>
