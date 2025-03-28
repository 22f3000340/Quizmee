<template>
  <div id="app">
    <Navbar />

    <div class="container mt-4">
      <router-view />
    </div>
    
    <footer class="py-3 mt-5 bg-light">
      <div class="container text-center">
        <p class="mb-0">Quiz Master V2 &copy; 2024</p>
      </div>
    </footer>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';

export default {
  name: 'App',
  components: {
    Navbar
  }
}
</script>

<style>
body {
  min-height: 100vh;
  font-family: 'Lexend', sans-serif;
}
#app {
  font-family: 'Lexend', sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.container {
  flex: 1;
}
.router-link-exact-active {
  font-weight: bold;
}
/* Add some custom styling for headings with Lexend font */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Lexend', sans-serif;
  font-weight: 600;
}
</style>
