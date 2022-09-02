<template>
  <div class="w-full h-full pb-12">
    <div class="w-full h-full flex flex-col desktop:text-2xl tablet:text-xl mobile:text-lg overflow-auto scrollbar">
      <div
        ref="titledev"
        class="w-full h-min flex justify-center desktop:text-7xl tablet:text-6xl mobile:text-5xl py-4"

      >
        AVOScript
        <span class="flex desktop:text-2xl tablet:text-xl mobile:text-lg items-end pl-4">{{avoscriptVersion}}</span>
      </div>
      <div
        class="w-full flex justify-center desktop:text-3xl tablet:text-2xl mobile:text-xl pb-12"
      >
        <p>
          Little language just for fun
        </p>
      </div>
      <div
        class="mobile:w-full tablet:w-2/3 desktop:w-1/2 flex flex-col justify-start place-self-center indent-8 text-justify"
      >
        <h1 class="desktop:text-4xl tablet:text-3xl mobile:text-2xl pb-4">Code examples</h1>
        Hello world
        <div ref="helloWorld" class="w-full h-40 indent-0 pl-8 pb-8"></div>
        Variables
        <div ref="variables" class="w-full h-48 indent-0 pl-8 pb-8"></div>
        Functions
        <div ref="functions" class="w-full h-80 indent-0 pl-8 pb-8"></div>
        Classes
        <div ref="classes" class="w-full h-[32rem] indent-0 pl-8 pb-8"></div>
        Enums
        <div ref="enums" class="w-full h-72 indent-0 pl-8 pb-8"></div>
      </div>
    </div>
    <div
      class="absolute right-4 bottom-4 w-min h-min"
      @click="goToUrl('https://github.com/ethosa/avoscript')"
    >
      <svg
        ref="githubButton"
        xmlns="http://www.w3.org/2000/svg"
        x="0px"
        y="0px"
        width="128" height="128"
        viewBox="0 0 32 32"
        class="transition ease-in-out
               desktop:scale-[1] desktop:hover:scale-[1.05] desktop:active:scale-[0.95]
               tablet:scale-[0.8] tablet:hover:scale-[0.85] tablet:active:scale-[0.75]
               mobile:scale-[0.6] mobile:hover:scale-[0.65] mobile:active:scale-[0.55]
               fill-gray-50 hover:fill-gray-400 active:fill-gray-600
               cursor-pointer"
      >
        <path
          d="M 16 4 C 9.371094 4 4 9.371094 4 16 C 4 21.300781 7.4375 25.800781 12.207031 27.386719
            C 12.808594 27.496094 13.027344 27.128906 13.027344 26.808594 C 13.027344 26.523438 13.015625 25.769531 13.011719 24.769531
            C 9.671875 25.492188 8.96875 23.160156 8.96875 23.160156 C 8.421875 21.773438 7.636719 21.402344 7.636719 21.402344
            C 6.546875 20.660156 7.71875 20.675781 7.71875 20.675781 C 8.921875 20.761719 9.554688 21.910156 9.554688 21.910156
            C 10.625 23.746094 12.363281 23.214844 13.046875 22.910156 C 13.15625 22.132813 13.46875 21.605469 13.808594 21.304688
            C 11.144531 21.003906 8.34375 19.972656 8.34375 15.375 C 8.34375 14.0625 8.8125 12.992188 9.578125 12.152344
            C 9.457031 11.851563 9.042969 10.628906 9.695313 8.976563 C 9.695313 8.976563 10.703125 8.65625 12.996094 10.207031
            C 13.953125 9.941406 14.980469 9.808594 16 9.804688 C 17.019531 9.808594 18.046875 9.941406 19.003906 10.207031
            C 21.296875 8.65625 22.300781 8.976563 22.300781 8.976563 C 22.957031 10.628906 22.546875 11.851563 22.421875 12.152344
            C 23.191406 12.992188 23.652344 14.0625 23.652344 15.375 C 23.652344 19.984375 20.847656 20.996094 18.175781 21.296875
            C 18.605469 21.664063 18.988281 22.398438 18.988281 23.515625 C 18.988281 25.121094 18.976563 26.414063 18.976563 26.808594
            C 18.976563 27.128906 19.191406 27.503906 19.800781 27.386719 C 24.566406 25.796875 28 21.300781 28 16
            C 28 9.371094 22.628906 4 16 4 Z"
        >
        </path>
      </svg>
    </div>
  </div>
</template>

<script>
import {editor, languages} from 'monaco-editor';
import AVOScript from '@/mixins/avoscript'
import API from '@/mixins/api'

export default {
  mixins: [
    AVOScript
  ],
  data() {
    return {
      avoscriptVersion: '',
      registered: false,
      codeExampleConfig: {
        value: ``,
        language: 'AVOScript',
        theme: 'AVOScriptTheme',
        wordWrap: 'off',
        fontSize: 16,
        automaticLayout: true,
        readOnly: true,
        scroll: {
          horizontal: 'visible',
          vertical: 'hidden'
        },
        minimap: {
          enabled: false
        },
      },
    }
  },
  methods: {
    goToUrl(url) {
      window.open(url, '_blank').focus()
    },
    async getVersion() {
    try {
        const res = await API.version()
        this.avoscriptVersion = res.response
      } catch (e) {
        this.avoscriptVersion = ''
      }
    }
  },
  async mounted() {
    await this.getVersion()
    if (!this.registered) {
      this.registered = true
      languages.register({'id': 'AVOScript'})
      languages.setMonarchTokensProvider('AVOScript', AVOScript.AVOScript)
      languages.registerCompletionItemProvider('AVOScript', {provideCompletionItems: this.completions})
      editor.defineTheme('AVOScriptTheme', AVOScript.AVOScriptTheme)
    }

    this.helloWorld && this.helloWorld.dispose()
    this.helloWorld = editor.create(this.$refs.helloWorld, this.codeExampleConfig)
    this.helloWorld.setValue([
      '# Hello world program',
      'echo("Hello, world!")',
      '# \'Hello, world!\' also available', ''
    ].join('\n'))

    this.variables && this.variables.dispose()
    this.variables = editor.create(this.$refs.variables, this.codeExampleConfig)
    this.variables.setValue([
      'let PI = 3.14159  # float immutable',
      'var i = 0  # integer',
      'var s = "my string"',
      'var arr = [PI, i, s, 1, true, off]',
      'var b_true = true  # true/on/enable',
      'var b_false = false  # false/off/disable', ''
    ].join('\n'))

    this.functions && this.functions.dispose()
    this.functions = editor.create(this.$refs.functions, this.codeExampleConfig)
    this.functions.setValue([
      'func main() {  # define function',
      '  echo("Main function")',
      '}',
      '',
      'func other(a, b, c = 0) {  # function with args',
      '  echo("args of other is $a, $b, $c")  # string formatting',
      '}',
      '',
      '# function calling',
      'main()',
      'other(1, 2)',
      'other(true, false, 10)',
      'other(0, 0, c="hi")', ''
    ].join('\n'))

    this.classes && this.classes.dispose()
    this.classes = editor.create(this.$refs.classes, this.codeExampleConfig)
    this.classes.setValue([
      'interface Animal {',
      '  func say()',
      '}', '',
      'class Cat of Animal {',
      '  func say() {',
      '    echo("meow")',
      '  }',
      '}', '',
      'class Pet : Cat {',
      '  var name = "Barsik"',
      '  init(name = "") {',
      '    if name != "" {',
      '      this::name = name',
      '    }',
      '  }',
      '}', '',
      'var cat = Pet()',
      'echo(cat::name)', ''
    ].join('\n'))

    this.enums && this.enums.dispose()
    this.enums = editor.create(this.$refs.enums, this.codeExampleConfig)
    this.enums.setValue([
      'enum Week {',
      '  MONDAY, TUESDAY, WEDNESDAY,',
      '  THURSDAY = "thursday", FRIDAY,',
      '  SATURDAY, SUNDAY',
      '}', '',
      'echo(Week::MONDAY, Week::SUNDAY)',
      'echo(Week::THURSDAY)', ''
    ].join('\n'))

  },
  beforeUnmount() {
    this.helloWorldExample && this.helloWorldExample.dispose()
  }
}
</script>

<style>
</style>