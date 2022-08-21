<template>
  <div class="w-full h-full">
    <div ref="editor" class="w-full h-2/3">

    </div>
    <div ref="output" class="w-full h-1/3">

    </div>
    <div
      class="transition ease-in-out hover:scale-[1.05] active:scale-[0.95]
             absolute flex z-50 right-16 bottom-16
             text-5xl text-gray-50 hover:text-gray-300 active:text-gray-500
             cursor-pointer select-none"
      @click="exec()"
    >
      <span
        class="material-symbols-outlined scale-[5]"
      >play_circle</span>
    </div>
  </div>
</template>


<script>
import {editor, languages} from 'monaco-editor';
import AVOScript from '../mixins/avoscript.js'
import API from '../mixins/api.js'

export default {
  name: 'App',
  components: {
  },
  mixins: [AVOScript, API],
  data() {
    return {
      registered: false,
      loaderStates: [
        'Executing \\',
        'Executing |',
        'Executing /',
        'Executing -',
      ],
      loaderState: 0,
      loaderInterval: null,
      editorConfig: {
        value: `# Example program\nclass Main{\n\tfunc main() {\n\t\techo('Hello world!')\n\t}\n}\n\nMain::main()\n`,
        language: 'AVOScript',
        theme: 'AVOScriptTheme',
        wordWrap: 'on',
        fontSize: 24,
        automaticLayout: true,
      },
      outputConfig: {
        value: `Output will here`,
        language: 'shell',
        theme: 'AVOScriptTheme',
        wordWrap: 'on',
        lineNumbers: 'off',
        fontSize: 20,
        readOnly: true,
        automaticLayout: true,
        minimap: {
          enabled: false
        }
      }
    }
  },
  methods: {
    completions() {
      var s = [
        {
          label: 'ifelse',
          kind: languages.CompletionItemKind.Snippet,
          insertText: 'if ${1:condition} {\n\t$2\n} else {\n\t$3\n}',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'If-Else Statement'
        }, {
          label: 'if',
          kind: languages.CompletionItemKind.Snippet,
          insertText: 'if ${1:condition} {\n\t$2\n}',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'If Statement'
        }, {
          label: 'echo',
          kind: languages.CompletionItemKind.Function,
          insertText: 'echo(${1:data})',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Echo Function'
        }, {
          label: 'read',
          kind: languages.CompletionItemKind.Function,
          insertText: 'read(${1:"Write your name"})',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Read Function'
        }, {
          label: 'switch',
          kind: languages.CompletionItemKind.Snippet,
          insertText: 'switch(${1:data}) {\n\tcase ${2:condition} {\n\t\t${3:# body}\n\t} else {\n\t\t${4:# body}\n\t}\n}',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Switch-Case Statement'
        }, {
          label: 'for',
          kind: languages.CompletionItemKind.Keyword,
          insertText: 'for var i = ${1:0}; ${2:condition}; ${3:++i) {\n\t${4:# body}\n}',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'For Statement'
        }, {
          label: 'foreach',
          kind: languages.CompletionItemKind.Keyword,
          insertText: 'for i in ${1:range(100)} {\n\t{$2:# body}\n}',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Foreach Statement'
        }, {
          label: 'trycatch',
          kind: languages.CompletionItemKind.Keyword,
          insertText: 'try {\n\t${1:# error code here}\n} catch ${2:e} {\n\t${3:# catch error here}\n}',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Try Catch'
        }
      ]
      return {suggestions: s}
    },
    loader() {
      if (this.loaderState == 3)
        this.loaderState = 0
      else
        this.loaderState++
      this.output.setValue(this.loaderStates[this.loaderState])
    },
    async exec() {
      if (this.loaderInterval == null)
        this.loaderInterval = setInterval(this.loader, 100)
      var code = this.editor.getValue()
      var res = await API.exec(code)
      if (this.loaderInterval != null)
        clearInterval(this.loaderInterval)
        this.loaderInterval = null
      if ('response' in res)
        this.output.setValue(res.response)
      else
        this.output.setValue(res.error)
    },
  },
  mounted() {
    if (!this.registered) {
      this.registered = true
      languages.register({'id': 'AVOScript'})
      languages.setMonarchTokensProvider('AVOScript', AVOScript.AVOScript)
      languages.registerCompletionItemProvider('AVOScript', {provideCompletionItems: this.completions})
      editor.defineTheme('AVOScriptTheme', AVOScript.AVOScriptTheme)
    }
    if (this.editor)
      this.editor.dispose()
    if (this.output)
      this.output.dispose()
    this.editor = editor.create(this.$refs.editor, this.editorConfig)
    this.output = editor.create(this.$refs.output, this.outputConfig)
  },
  beforeUnmount() {
    this.editor && this.editor.dispose()
    this.output && this.output.dispose()
  }
}
</script>


<style>
</style>
