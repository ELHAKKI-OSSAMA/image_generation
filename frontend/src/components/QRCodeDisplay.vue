<template>
  <div class="flex flex-col items-center justify-center">
    <qrcode-vue :value="value" :size="size" :level="level" />
    <slot />
  </div>
</template>

<script>
import QrcodeVue from 'qrcode.vue';

export default {
  name: 'QRCodeDisplay',
  components: { QrcodeVue },
  props: {
    value: {
      type: String,
      required: true
    },
    size: {
      type: Number,
      default: 192
    },
    level: {
      type: String,
      default: 'M' // L, M, Q, H
    }
  }
};
</script>

<style scoped>
/* Optional: add custom styles here */
</style>
