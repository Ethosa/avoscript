<template>
  <div ref="src" class="text-base">
  </div>
</template>

<script>
import Packages from '@/mixins/pkgs'
import { parse } from 'marked'

export default {
  data() {
    return {
      source: '',
    }
  },
  async mounted() {
    this.$refs.src.innerHTML = parse(await Packages.fetchReadme(this.$route.query.github_url))
  }
}
</script>

<style>
</style>