const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: '/dataviz/',  // Added trailing slash for consistency
  
  chainWebpack: (config) => {
    config.plugin('html').tap((args) => {
      // Set the title for the browser tab
      args[0].title = 'Sunburst 1.0';
      return args;
    });
  },

  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})