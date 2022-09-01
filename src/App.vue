<template>
  <div class="w-screen h-screen flex text-white bg-[#14131b] font-mono overflow-hidden">
    <div
      id="toolbar"
      class="absolute left-0 top-0 w-screen h-12 z-40
             desktop:text-2xl tablet:text-xl mobile:text-lg
             bg-[#18171f] shadow-md flex flex-row justify-start items-center px-5"
    >
      <div class="flex w-3/4">
        <div
          class="desktop:text-3xl tablet:text-2xl mobile:text-xl font-bold
               text-gray-50 hover:text-gray-400 active:text-gray-600
               select-none cursor-pointer transition-all"
        @click="mainPage()"
        >
          AVOScript
        </div>
      </div>
      <div class="flex w-1/4 justify-around">
        <div
          class="text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer transition-all"
          @click="packagesPage()"
        >
          PACKAGES
        </div>
        <div
          class="text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer transition-all"
          @click="playgroundPage()"
        >
          PLAYGROUND
        </div>
        <div
          v-show="playground.isPlayground"
          class="text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer transition-all"
          @click="saveCode()"
        >
          SHARE
        </div>
      </div>
    </div>
    <v-snackbar
      v-model="saved"
      multi-line
      vertical
      :timeout="2000"
      variant="tonal"
      color="primary"
    >
      <span class="text-white text-xl">
        shared code available on
        <a :href="sharedURL">{{ sharedURL }}</a>
      </span>
      <template v-slot:actions>
        <v-btn
          variant="tonal"
          @click="saved = false"
          class="text-xl text-white"
        >
          CLOSE
        </v-btn>
      </template>
    </v-snackbar>
    <router-view class="mt-12"/>
  </div>
</template>


<script>
import { usePlayground } from '@/store'
import API from '@/mixins/api'

export default {
  name: 'App',
  mixins: [API],
  data() {
    return {
      playground: usePlayground(),
      saved: false,
      sharedURL: ''
    }
  },
  methods: {
    mainPage() {
      this.playground.isPLayground = false
      this.$router.push("/")
    },
    playgroundPage() {
      this.$router.push("/playground")
    },
    packagesPage() {
      this.playground.isPLayground = false
      this.$router.push("/packages")
    },
    async saveCode() {
      const res = await API.save(this.playground.code)
      console.log(res)
      this.sharedURL = `https://ethosa.github.io/avoscript/#/code/${res.response}`
      this.saved = true
    }
  },
  mounted() {
  },
}
</script>


<style>
</style>
