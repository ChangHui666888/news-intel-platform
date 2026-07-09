<template>
  <div id="app">
    <NavBar />
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>
