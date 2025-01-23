const isProd = process.env.NODE_ENV === 'prod';

module.exports = {
 root: true,
 env: {
   node: true,
   browser: true,
   es2021: true
 },
 extends: [
   'plugin:vue/vue3-essential',
   'eslint:recommended'
 ],
 parserOptions: {
   parser: '@babel/eslint-parser',
   sourceType: 'module',
   ecmaVersion: 'latest'
 },
 rules: {
   'no-console': isProd ? 'warn' : 'off',
   'no-debugger': isProd ? 'warn' : 'off'
 }
}