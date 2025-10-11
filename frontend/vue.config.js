const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env.dev') });

module.exports = {
  devServer: {
    port: process.env.FRONTEND_PORT || 3000,
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src/'),
      }
    }
  }
};
