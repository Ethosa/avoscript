<template>
  <div ref='editor' class='editor'></div>
</template>


<script>
import {editor, languages} from 'monaco-editor';

export default {
  name: 'App',
  components: {
  },
  data() {
    return {
      registered: false,
      config: {
        value: `# Example program\nclass Main{\n\tfunc main() {\n\t\techo('Hello world!')\n\t\techo("test", 0.1, 2, true, off)\n\t\tif 0 > 1 or 2 == 2 {\n\t\t\techo("ok")\n\t\t}\n\t}\n}\n\nMain::main()\n`,
        language: 'AVOScript',
        theme: 'AVOScriptTheme',
        wordWrap: 'on',
      },
      AVOScriptTheme: {
        base: 'vs-dark',
        inherit: true,
        rules: [
          {background: '14131b'},
          {token: 'keyword', foreground: 'da4f3b'},
          {token: 'operator', foreground: '8d6695'},
          {token: 'number', foreground: 'e78d0d'},
          {token: 'className', foreground: 'f1a910'},
          {token: 'comment', foreground: '5e4c58'},
          {token: 'builtin', foreground: 'ff37ff'},
          {token: 'function', foreground: '0096bb'},
          {token: 'string', foreground: 'e0cd15'},
          {token: 'boolean', foreground: 'a5552c'},
        ],
        colors: {
          'editor.foreground': '#fbf9f2',
          'editor.background': '#14131b'
        }
      },
      AVOScript: {
        defaultToken: 'text',
        brackets: [
          { open: '(', close: ')', token: 'bracket.parenthesis'},
          { open: '[', close: ']', token: 'bracket.bracket'},
          { open: '{', close: '}', token: 'bracket.curly'},
        ],
        keywords: [
          'abstract', 'class', 'interface', 'of', 'func', 'const', 'var', 'if', 'elif', 'else',
          'for', 'while', 'break', 'continue', 'return', 'switch', 'case',
        ],
        operators: [
          '&&', 'and', '||', 'or', '+', '-', '/', '*', '%', '^', '$', '@', '!',
          '=', '+=', '-=', '/=', '*=', '++', '--', '==', '>=', '<=', '=>', '->',
          '!=', '>', '<', 'in',
        ],
        builtin: [
          'echo', 'read', 'range', 'randf', 'randi', 'length', 'string',
          'int', 'float'
        ],
        booleans: [
          'true', 'false', 'on', 'off', 'enable', 'disable'
        ],
        tokenizer: {
          root: [
            [/'.*'/, 'string'],
            [/".*"/, 'string'],
            [/[a-zA-Z][a-zA-Z0-9_]*(?=\()/, {
              cases: {
                '@builtin': 'builtin',
                '@default': 'function'
              }
            }],
            [/[A-Z][a-zA-Z0-9_]*/, 'className'],
            [/[a-z][a-zA-Z0-9_]*/, {
              cases: {
                '@keywords': 'keyword',
                '@operators': 'operator',
                '@builtin': 'builtin',
                '@booleans': 'boolean',
              }
            }],
            [/[><!=\-/+\-?%$@&^]/, 'operator'],
            [/[0-9]+/, 'number'],
            [/(^#.*$)/, 'comment'],
          ]
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
          insertText: 'switch(${1:data}) {\n\tcase ${2:condition} {\n\t\t${3:# body}\n\t} else {\n\t\t${4:# else body}\n\t}\n}',
          insertTextRules: languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Switch-Case Statement'
        }
      ]
      return {suggestions: s}
    },
  },
  mounted() {
    if (!this.registered) {
      this.registered = true
      languages.register({'id': 'AVOScript'})
      languages.setMonarchTokensProvider('AVOScript', this.AVOScript)
      languages.registerCompletionItemProvider('AVOScript', {provideCompletionItems: this.completions})
      editor.defineTheme('AVOScriptTheme', this.AVOScriptTheme)
    }
    this.editor = editor.create(this.$refs.editor, this.config)
  },
  beforeUnmount() {
    this.editor && this.editor.dispose()
  }
}
</script>


<style>
.editor {
  width: 45em;
  height: 35em;
}
</style>
