<template>
  <div v-if="article" class="article">
    <h1>{{ article.title }}</h1>
    <div class="byline">
      {{ article.source_name }} · {{ fmtDate(article.published_at) }}
      <span v-if="article.tier" :class="`badge badge-${article.tier.toLowerCase()}`">T{{ article.tier }}</span>
    </div>

    <div class="content" v-html="renderMd(article.content_md || article.summary_cn || '')" />

    <div v-if="article.analysis" class="analysis-box">
      <h4>📊 AI 分析</h4>
      <p v-if="article.analysis.event"><b>事件:</b> {{ article.analysis.event }}</p>
      <p v-if="article.analysis.impact"><b>影响:</b> {{ article.analysis.impact }}</p>
      <p v-if="article.analysis.market_signal"><b>信号:</b> {{ article.analysis.market_signal }}</p>
      <p v-if="article.analysis.risk_level"><b>风险:</b> {{ article.analysis.risk_level }}</p>
    </div>
  </div>
  <div v-else style="text-align:center;padding:60px">加载中...</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const article = ref(null)

onMounted(async () => {
  const { data } = await api.getNewsById(route.params.id)
  article.value = data
})

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '' }
function renderMd(md) {
  return (md || '').replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>').replace(/^/, '<p>').replace(/$/, '</p>')
}
</script>
