const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,

  chainWebpack: (config) => {
    config.plugin('html').tap((args) => {
      // Set the title for the browser tab
      args[0].title = 'Sunburst 1.0';
      return args;
    });
  },
})
