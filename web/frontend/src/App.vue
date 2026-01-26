<template>
  <div id="app-layout">
    <div id="sidebar">
      <h1>Console</h1>
      <nav>
        <router-link to="/">Dashboard</router-link>
        <router-link to="/news">News</router-link>
        <router-link to="/analysis">Analysis</router-link>
        <router-link to="/configuration">Configuration</router-link>
        <router-link to="/trading">Trading</router-link>
        <router-link to="/backtester">Backtester</router-link>
      </nav>
    </div>
    <main id="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
#app-layout {
  display: flex;
  height: 100vh;
}

#sidebar {
  width: 200px;
  background-color: #f4f4f4;
  padding: 20px;
}

#sidebar h1 {
  margin-top: 0;
}

#sidebar nav {
  display: flex;
  flex-direction: column;
}

#sidebar nav a {
  margin: 10px 0;
  text-decoration: none;
  color: #333;
}

#sidebar nav a.router-link-exact-active {
  font-weight: bold;
  color: #007bff;
}

#main-content {
  flex: 1;
  padding: 20px;
}
</style>
