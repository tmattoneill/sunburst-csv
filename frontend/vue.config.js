const path = require('path');
const webpack = require('webpack');
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
    },
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false)
      })
    ]
  }
};
