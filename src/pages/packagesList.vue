<template>
  <div class="flex flex-col w-full h-full p-8 gap-y-6">
    <svg
      v-if="loading"
      width="100px" height="100px" viewBox="0 0 345 345"
      class="flex h-full justify-self-center place-self-center animate-spin fill-white"
    >
      <path d="M 172.5 34.324219 C 240.660156 34.324219 296.679688 87.148438 301.867188 154 L 277.863281
               129.996094 L 271.53125 136.328125 L 303.613281 168.40625 L 309.941406 168.40625 L 345 133.339844
               L 338.671875 127.011719 L 310.902344 154.785156 C 306.078125 82.621094 245.867188 25.375 172.5 25.375
               C 95.988281 25.375 33.746094 87.621094 33.746094 164.125 L 42.699219 164.125 C 42.699219 92.554688
               100.929688 34.324219 172.5 34.324219 Z M 172.5 34.324219 "/>
      <path d="M 172.5 310.675781 C 104.339844 310.675781 48.320312 257.851562 43.132812 191 L 67.136719
               215.003906 L 73.46875 208.671875 L 41.386719 176.59375 L 35.058594 176.59375 L 0 211.65625
               L 6.328125 217.984375 L 34.097656 190.214844 C 38.921875 262.378906 99.132812 319.625 172.5
               319.625 C 249.011719 319.625 311.253906 257.386719 311.253906 180.875 L 302.300781 180.875
               C 302.300781 252.445312 244.070312 310.675781 172.5 310.675781 Z M 172.5 310.675781 "/>
    </svg>
    <div
      v-else
      v-for="(item, index) in items" :key="item.name"
      class="flex flex-col hover:bg-[#27262d] active:bg-[#37363d] transition-colors select-none"
      @click="packagePage(item)"
    >
      <div
        class="flex flex-col desktop:text-4xl tablet:text-3xl mobile:text-2xl gap-y-2"
      >
        {{ item.name[0].toUpperCase() + item.name.slice(1) }}
        <div class="ml-4 desktop:text-xl tablet:text-lg mobile:text-base flex flex-row gap-2">
          <div
            v-for="keyword in item.keywords.split(' ')" :key="keyword"
            class="flex rounded-xl border-2 bg-[#27262d] border-[#37363d] px-4 select-none"
          >
            {{ keyword }}
          </div>
        </div>
      </div>
      <div
        class="w-fit desktop:text-2xl tablet:text-xl mobile:text-lg
               text-gray-50 hover:text-gray-400 active:text-gray-600
               hover:scale-105 active:scale-95 transition-all
               select-none ml-4 mt-8 mb-1 cursor-pointer"
        @click="goToUrl(item.github_url)"
      >
        Source code
      </div>
      <div class="w-full mt-2 bg-white h-[1px]" v-if="index < items.length-1"></div>
    </div>
  </div>
</template>

<script>
import Packages from '@/mixins/pkgs'

export default {
  data() {
    return {
      items: [],
      loading: true
    }
  },
  methods: {
    goToUrl(url) {
      window.open(url, '_blank').focus()
    },
    packagePage(item) {
      this.$router.push({
        path: `/package/${item.name}`,
        query: {
          github_url: item.github_url
        }
      })
    }
  },
  async mounted() {
    Packages.fetchPackages().then(res => {
      this.items = res
      this.loading = false
    })
  }
}
</script>

<style></style>