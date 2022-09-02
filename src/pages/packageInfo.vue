<template>
  <div class="flex w-full h-full justify-center pb-12">
    <div
      ref="src"
      class="flex flex-col desktop:w-1/3 tablet:w-2/3 mobile:w-full overflow-auto scrollbar py-4"
    >
    </div>
  </div>
</template>

<script>
import Packages from '@/mixins/pkgs'
import { parse } from 'marked'

const hljs = require('highlight.js')

export default {
  data() {
    return {
      source: '',
    }
  },
  async mounted() {
    await Packages.fetchReadme(this.$route.query.github_url).then(value => {
      this.$refs.src.innerHTML = parse(value)
      hljs.highlightAll()
    })
  }
}
</script>

<style>
</style>