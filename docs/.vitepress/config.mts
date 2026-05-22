import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Zarr Conventions Guidance',
  description: 'Non-normative guidance and worked examples for the Zarr Conventions framework.',
  base: '/zarr-conventions-guidance/',
  cleanUrls: true,
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Spec', link: 'https://github.com/zarr-conventions/zarr-conventions-spec' },
    ],
    sidebar: [
      {
        text: 'Guidance',
        items: [
          { text: 'Implementation Contracts', link: '/implementation-contracts' },
        ],
      },
      {
        text: 'Walkthroughs',
        items: [
          { text: 'Overview', link: '/walkthroughs/' },
          { text: '01. Stable additive covenant', link: '/walkthroughs/01-stable-additive-covenant' },
          { text: '02. Structural inspection', link: '/walkthroughs/02-structural-inspection' },
          { text: '03. URI dispatch', link: '/walkthroughs/03-uri-dispatch' },
          { text: '04. Integer-major with structural pass-through', link: '/walkthroughs/04-integer-major-pass-through' },
          { text: '05. Semver with declared migrators', link: '/walkthroughs/05-semver-with-migrators' },
        ],
      },
      {
        text: 'Posts',
        items: [
          { text: '2026 spec-evolution survey', link: '/posts/2026-survey' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/zarr-conventions/zarr-conventions-guidance' },
    ],
    footer: {
      message: 'Non-normative guidance. For the normative spec, see <a href="https://github.com/zarr-conventions/zarr-conventions-spec">zarr-conventions-spec</a>.',
    },
  },
})
