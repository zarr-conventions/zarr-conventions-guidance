import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Zarr Conventions Guidance',
  description: 'Non-normative guidance and worked examples for the Zarr Conventions framework.',
  base: '/zarr-conventions-guidance/',
  cleanUrls: true,
  ignoreDeadLinks: true,
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
          { text: '01. add-optional', link: '/walkthroughs/01-add-optional' },
          { text: '02. rename', link: '/walkthroughs/02-rename' },
          { text: '03. retype', link: '/walkthroughs/03-retype' },
          { text: '04. semantic-only', link: '/walkthroughs/04-semantic-only' },
          { text: '05. add-with-semantic-shift', link: '/walkthroughs/05-add-with-semantic-shift' },
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
