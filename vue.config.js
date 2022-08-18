const { defineConfig } = require('@vue/cli-service')
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: process.env.NODE_ENV === 'production' ? '/avoscript/' : '/',
  configureWebpack: (config) => {
    config.plugins.push(new MonacoWebpackPlugin());
  }
})
