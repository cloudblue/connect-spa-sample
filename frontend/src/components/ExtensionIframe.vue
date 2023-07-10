<script>
import axios from 'axios'

export default {
  data() {
    return {
      iframeUrl: null,
      label: null,
      icon: null
    }
  },
  async mounted() {
    try {
      const response = await axios.get('http://localhost:8000/iframe_details')
      this.iframeUrl = response.data.url
      this.label = response.data.label
      this.icon = response.data.icon
    } catch (error) {
      console.error('Error occurred:', error)
    }
  }
}
</script>

<template>
  <div>
    <p>
      Title:<br /><b>{{ label }}</b>
    </p>
    <p>Icon:<br /><img v-if="icon" :src="`${icon}`" :alt="`${label}`" /></p>
    <iframe v-if="iframeUrl" :src="`${iframeUrl}`" width="100%" height="600px"></iframe>
  </div>
</template>

<style scoped></style>
