<template>
  <div>
    <h1>Configuration</h1>
    <form @submit.prevent="saveConfig">
      <div v-for="(value, key) in config" :key="key">
        <label :for="key">{{ key }}</label>
        <input v-if="typeof value !== 'boolean'" :id="key" v-model="config[key]" />
        <input v-else type="checkbox" :id="key" v-model="config[key]" />
      </div>
      <button type="submit">Save</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const config = ref({})

onMounted(async () => {
  const response = await fetch('/api/config')
  config.value = await response.json()
})

const saveConfig = async () => {
  await fetch('/api/config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(config.value),
  })
}
</script>
