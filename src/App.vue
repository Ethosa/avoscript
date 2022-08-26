<template>
  <div class="w-screen h-screen flex text-white bg-[#14131b] font-mono overflow-hidden">
    <div
      id="toolbar"
      class="absolute left-0 top-0 w-screen h-12 z-40
             desktop:text-2xl tablet:text-xl mobile:text-lg
             bg-[#18171f] shadow-md flex flex-row justify-start items-center px-5"
    >
      <div class="flex w-4/5">
        <div
          class="desktop:text-3xl tablet:text-2xl mobile:text-xl font-bold
               text-gray-50 hover:text-gray-400active:text-gray-600
               select-none cursor-pointer"
        @click="mainPage()"
        >
          AVOScript
        </div>
      </div>
      <div class="flex w-1/5 justify-around">
        <div
          class="text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer"
          @click="playgroundPage()"
        >
          PLAYGROUND
        </div>
        <div
          v-if="playground.isPlayground"
          class="text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer"
          @click="saveCode()"
        >
          SHARE
        </div>
      </div>
    </div>
    <router-view class="mt-12"/>
  </div>
</template>


<script>
import { usePlayground } from './mixins/store.js'
import API from './mixins/api.js'

export default {
  name: 'App',
  mixins: [API],
  data() {
    return {
      playground: usePlayground()
    }
  },
  methods: {
    mainPage() {
      this.$router.push("/")
    },
    playgroundPage() {
      this.$router.push("/playground")
    },
    async saveCode() {
      const res = await API.save(this.playground.code)
      console.log(res)
      alert(`Saved code available on https://ethosa.github.io/avoscript/#/code${res.response}`)
    }
  },
  mounted() {
  },
}
</script>


<style>
</style>
