<template>
  <div>
    <h2 style="margin-bottom:16px">📂 {{ $route.params.name }}</h2>
    <NewsCard v-for="a in items" :key="a.id" :article="a" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import NewsCard from '../components/NewsCard.vue'

const route = useRoute()
const items = ref([])

onMounted(async () => {
  const { data } = await api.getNews({ category: route.params.name, page_size: 50 })
  items.value = data.items
})
</script>
