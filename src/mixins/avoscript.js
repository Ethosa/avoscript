export default {
    AVOScriptTheme: {
        base: 'vs-dark',
        inherit: true,
        rules: [
            {background: '14131b'},
            {token: 'keyword', foreground: 'dd3968'},
            {token: 'string.curly', foreground: 'da4f3b'},
            {token: 'operator', foreground: '8d6695'},
            {token: 'number', foreground: 'e78d0d'},
            {token: 'className', foreground: 'f1a910'},
            {token: 'comment', foreground: '56696b'},
            {token: 'builtin', foreground: 'ff37ff'},
            {token: 'function', foreground: '0096bb'},
            {token: 'string', foreground: 'e0cd15'},
            {token: 'boolean', foreground: 'a5552c'},
            {token: 'let', foreground: '96f6df'},
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
            'abstract', 'class', 'interface', 'of', 'func', 'let', 'var', 'if', 'elif', 'else',
            'for', 'while', 'break', 'continue', 'return', 'switch', 'case', 'try', 'catch', 'import',
            'from', 'this', 'with', 'super', 'enum',
        ],
        operators: [
            '&&', 'and', '||', 'or', '+', '-', '/', '*', '%', '^', '$', '@', '!',
            '=', '+=', '-=', '/=', '*=', '++', '--', '==', '>=', '<=', '=>', '->',
            '!=', '>', '<', 'in',
        ],
        builtin: [
            'echo', 'read', 'range', 'randf', 'randi', 'length', 'string', 'int', 'float'
        ],
        booleans: [
            'true', 'false', 'on', 'off', 'enable', 'disable'
        ],
        tokenizer: {
            root: [
                [/'/, 'string', '@string1'],
                [/"/, 'string', '@string2'],
                {include: '@common'},
                [/#\[/, 'comment', '@comment'],
                [/(^#.*$)/, 'comment'],
            ],
            common: [
                [/@[a-zA-Z][a-zA-Z0-9_]*/, 'function'],
                [/[a-zA-Z][a-zA-Z0-9_]*(?=\()/, {
                    cases: {
                    '@builtin': 'builtin',
                    '@default': 'function'
                    }
                }],
                [/[A-Z][A-Z0-9_]+/, 'let'],
                [/[A-Z][a-zA-Z0-9_]*/, 'className'],
                [/[a-z][a-zA-Z0-9_]*/, {
                    cases: {
                    '@keywords': 'keyword',
                    '@operators': 'operator',
                    '@builtin': 'builtin',
                    '@booleans': 'boolean',
                    }
                }],
                [/[><!=\-/+\-?*%$@&^:~]/, 'operator'],
                [/[0-9]+/, 'number'],
            ],
            comment: [
                [/\]#/, 'comment', '@pop'],
                [/[\s\S]/, 'comment'],
            ],
            string1: [
                [/'/, 'string', '@pop'],
                [/\\\S/, 'operator'],
                [/\$[a-zA-Z][a-zA-Z0-9_]*/, 'keyword'],
                [/\$\{/, 'string.curly', '@stringCurly'],
                [/./, 'string'],
            ],
            string2: [
                [/"/, 'string', '@pop'],
                [/\\\S/, 'operator'],
                [/\$[a-zA-Z][a-zA-Z0-9_]*/, 'keyword'],
                [/\$\{/, 'string.curly', '@stringDoubleCurly'],
                [/./, 'string'],
            ],
            stringCurly: [
                [/"/, 'string', '@string2'],
                [/\}/, 'string.curly', '@pop'],
                {include: '@common'},
            ],
            stringDoubleCurly: [
                [/'/, 'string', '@string1'],
                [/\}/, 'string.curly', '@pop'],
                {include: '@common'},
            ],
        }
    }
}