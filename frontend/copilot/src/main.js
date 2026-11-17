import { createApp } from 'vue';
import App from './App.vue';
import OnboardingEmbed from './OnboardingEmbed.vue';
import './style.css';
import './persistent-shell.css';

const root = document.getElementById('potiguar-copilot');
if (root) {
  createApp(root.dataset.embed === 'onboarding' ? OnboardingEmbed : App, { csrf: root.dataset.csrfToken || '' }).mount(root);
}
