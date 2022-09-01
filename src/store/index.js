import { defineStore } from 'pinia'

export const usePlayground = defineStore('playground', {
    state: () => {
        return {
            isPLayground: false,
            code: ''
        }
    },
    actions: {
        toggle() {
            this.isPLayground = !this.isPLayground
        },
        setCode(code) {
            this.code = code
        }
    }
})
