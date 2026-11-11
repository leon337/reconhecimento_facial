import { createApp } from 'vue';
import App from './App.vue';
import './style.css';

const root = document.getElementById('potiguar-copilot');
if (root) {
  createApp(App, { csrf: root.dataset.csrfToken || '' }).mount(root);
}
