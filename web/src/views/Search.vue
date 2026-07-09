<template>
  <div>
    <h2 style="margin-bottom:16px">搜索: "{{ q }}" ({{ total }} 条)</h2>
    <NewsCard v-for="a in items" :key="a.id" :article="a" />
    <div v-if="total > pageSize" class="pagination">
      <button v-for="p in Math.ceil(total/pageSize)" :key="p"
              :class="{ active: p === page }" @click="goPage(p)">{{ p }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import NewsCard from '../components/NewsCard.vue'

const route = useRoute()
const q = ref(route.query.q || '')
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20

async function load() {
  const { data } = await api.search(q.value, page.value)
  items.value = data.items; total.value = data.total
}
function goPage(p) { page.value = p; load() }

watch(() => route.query.q, v => { q.value = v; page.value = 1; load() })
onMounted(load)
</script>
