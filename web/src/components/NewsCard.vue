<template>
  <div class="news-card">
    <router-link :to="`/news/${article.id}`">
      <h3>{{ article.title }}</h3>
    </router-link>
    <div class="meta">
      <span v-if="article.source_name">{{ article.source_name }}</span>
      <span v-if="article.published_at">{{ fmtDate(article.published_at) }}</span>
      <span v-if="article.tier" :class="`badge badge-${article.tier.toLowerCase()}`">T{{ article.tier }}</span>
      <span v-if="article.category" class="badge badge-tag">{{ article.category }}</span>
    </div>
    <div class="summary" v-if="article.summary_cn">{{ article.summary_cn?.substring(0,150) }}</div>
  </div>
</template>

<script setup>
defineProps({ article: Object })
function fmtDate(d) { return new Date(d).toLocaleDateString('zh-CN') }
</script>
