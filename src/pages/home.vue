<template>
    <div class="w-full h-full pb-16">
        <div class="w-full h-full flex flex-col text-2xl overflow-auto scrollbar">
            <div class="text-7xl w-full h-min flex justify-center pt-4 pb-8">AVOScript</div>
            <div class="w-1/3 flex flex-col justify-start place-self-center indent-8 text-justify">
                <h1 class="text-4xl pb-4">Code examples</h1>
                Hello world
                <div ref="helloWorld" class="w-full h-40 indent-0 pl-8 pb-8"></div>
                Variables
                <div ref="variables" class="w-full h-48 indent-0 pl-8 pb-8"></div>
                Functions
                <div ref="functions" class="w-full h-80 indent-0 pl-8 pb-8"></div>
            </div>
        </div>
    </div>
</template>

<script>
import {editor, languages} from 'monaco-editor';
import AVOScript from '../mixins/avoscript.js'

export default {
  mixins: [
    AVOScript
  ],
  data() {
    return {
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
  mounted() {
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
      'const PI = 3.14159  # float const',
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
      'main()  # function calling',
      'other(1, 2)',
      'other(true, false, 10)',
      'other(0, 0, c="hi")', ''
    ].join('\n'))

  },
  beforeUnmount() {
    this.helloWorldExample && this.helloWorldExample.dispose()
  }
}
</script>

<style>
.scrollbar::-webkit-scrollbar {
  width: 20px;
}

.scrollbar::-webkit-scrollbar-track {
  background: #f7f4ed;
}

.scrollbar::-webkit-scrollbar-thumb {
  background: #e0cbcb;
}

.scrollbar::-webkit-scrollbar-thumb:hover {
  background: #c0a0b9;
}
</style>