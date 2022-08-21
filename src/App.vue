<template>
  <div class="w-screen h-screen flex text-white bg-[#14131b] font-mono overflow-hidden">
    <div
      id="toolbar"
      class="absolute left-0 top-0 w-screen h-12 z-40 text-2xl bg-[#18171f] shadow-md flex flex-row justify-start items-center px-5"
    >
      <div class="flex w-5/6">
        <div
          class="text-3xl font-bold text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer"
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
        <div
          class="text-gray-50 hover:text-gray-400 active:text-gray-600 select-none cursor-pointer"
          @click="aboutPage()"
        >
          ABOUT
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
    aboutPage() {
      this.$router.push("/about")
    },
  },
  mounted() {
  },
}
</script>


<style>
</style>
