<template>
  <div class="w-screen h-screen flex text-white bg-[#14131b] font-mono overflow-hidden">
    <div
      id="toolbar"
      class="absolute left-0 top-0 w-screen h-12 z-40
             desktop:text-2xl tablet:text-xl mobile:text-lg
             bg-[#18171f] shadow-md flex flex-row justify-start items-center px-5"
    >
      <div class="flex w-5/6">
        <div
          class="desktop:text-3xl tablet:text-2xl mobile:text-xl font-bold
               text-gray-50 hover:text-gray-400active:text-gray-600
               select-none cursor-pointer"
        @click="mainPage()"
        >
          AVOScript
        </div>
      </div>
      <div class="flex w-1/6 justify-around">
        <div
          class="text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer"
          @click="playgroundPage()"
        >
          PLAYGROUND
        </div>
      </div>
    </div>
    <router-view class="mt-12"/>
  </div>
</template>


<script>

export default {
  name: 'App',
  components: {
  },
  data() {
    return {
    }
  },
  methods: {
    mainPage() {
      this.$router.push("/")
    },
    playgroundPage() {
      this.$router.push("/playground")
    },
  },
  mounted() {
  },
}
</script>


<style>
</style>
