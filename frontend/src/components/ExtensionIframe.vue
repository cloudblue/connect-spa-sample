<script>
export default {
  data: () => ({
    iframeUrl: null,
    label: null,
    icon: null
  }),

  computed: {
    hasIframeData: (vm) => vm.iframeUrl && vm.label && vm.icon,
    computedIframeUrl: (vm) => (vm.iframeUrl ? `${vm.iframeUrl}?t=${Date.now()}` : '')
  },

  methods: {
    async requestIframeDetails(tierAccountId) {
      try {
        const url = new URL('/iframe_details', window.location.origin)

        if (tierAccountId !== null) {
          const params = { tier_account_id: tierAccountId }
          url.search = new URLSearchParams(params).toString()
        }

        const response = await fetch(url).then((r) => r.json())
        this.iframeUrl = response.url
        this.label = response.label
        this.icon = response.icon
      } catch (error) {
        console.error('Error occurred:', error)
      }
    },

    getIframeDetails() {
      const searchParams = new URLSearchParams(window.location.search)

      this.label = searchParams.get('label') || null
      this.icon = searchParams.get('icon') || null
      this.iframeUrl = searchParams.get('url') || null
      const tierAccountId = searchParams.get('tier_account_id') || null

      if (!this.hasIframeData) this.requestIframeDetails(tierAccountId)
    }
  },

  created() {
    this.getIframeDetails()
  }
}
</script>

<template>
  <div v-if="hasIframeData" class="card">
    <div class="card_header">
      <img v-if="icon" class="card_icon" :src="icon" :alt="label" />
      <h1 class="card_title">{{ label }}</h1>
    </div>
    <div class="card_content">
      <iframe class="card_iframe" :src="computedIframeUrl" />
    </div>
  </div>
</template>

<style scoped>
.card {
  position: fixed;
  top: 256px;
  left: 50%;
  transform: translateX(-50%);
  height: calc(100vh - 296px);
  width: 1200px;
  background: var(--color-background);
  border-radius: 8px;
  box-shadow: 0px 2px 48px 0px rgba(0, 0, 0, 0.15);
}

.card_header {
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 48px;
  background-color: var(--light-background);
  padding: 0 32px;
  border-radius: 8px 8px 0 0;
}

.card_icon {
  height: 24px;
  width: 24px;
  background-color: white;
  border-radius: 4px;
  margin-right: 8px;
}

.card_title {
  color: var(--color-text);
  font-size: 16px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px;
}

.card_content {
  padding: 0 0 40px 0;
  height: 100%;
  width: 100%;
}

.card_iframe {
  display: block;
  height: 100%;
  width: 100%;
  border: none;
  border-radius: 0 0 8px 8px;
}
</style>
