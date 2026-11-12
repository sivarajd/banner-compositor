# Banner sizes

Checked 12 Nov 2026. Platforms change these without notice, so this table is the third
choice. Prefer, in order:

1. the size shown in the platform's upload dialog, as the user reports it
2. the platform's current help page
3. this table
4. the pixel size of the existing banner, which may predate a change

Tell the user which size you used and that you did not test how the site crops it.

How to read "Evidence":

- **Official**: stated on the platform's own page, fetched on the check date.
- **Reported**: stated by a user from the upload dialog, or by a secondary site that cites
  the platform's help page. The official page could not be opened.
- **Unconfirmed**: search-result snippets or blogs only. Treat as a lead.

The figures were read through an automated fetch tool, not from the raw pages. Recheck
before relying on one for anything that matters.

## Sizes

| Where | Size | Evidence | Notes |
|---|---|---|---|
| Reddit community banner, desktop | 1072x128 | Reported | From the upload dialog (user report, Nov 2026); also reported by moda.app citing Reddit Help. |
| Reddit community banner, mobile | 1080x128 | Reported | Same sources. A separate upload from the desktop banner. |
| Reddit community banner, to fill wide monitors | 4000x192 | Official | Reddit for Community quick-start guide: "we recommend a banner size of 4,000 x 192 pixels". |
| YouTube channel banner | 2560x1440 or larger; minimum 2048x1152; 16:9 | Official | 6 MB or smaller. |
| YouTube safe area for text and logos | 1235x338 at the minimum size | Official | Centre of the image. Scaled to 2560x1440 this is about 1544x423; blogs quote 1546x423, which is not on the official page. |
| Facebook page cover | 851x315 | Official | Minimum 400x150. Loads fastest as an sRGB JPG under 100 KB; PNG is better for logos and text. Shown at different shapes on desktop and phone. The profile picture covers part of the left side and overlaps by about 40 px on phones. |
| LinkedIn personal background photo | 1584x396 | Official | JPG or PNG, under 8 MB. |
| Discord server banner | 16:9 (960x540 commonly given) | Official for the ratio; pixel size unconfirmed | Developer docs state only "16:9 png/jpeg". Needs a boosted server. |
| Discord invite splash | 16:9 (1920x1080 commonly given) | Official for the ratio; pixel size unconfirmed | |
| Discord user profile banner | Minimum 680x240 or 600x240 | Unconfirmed | Sources disagree. |
| X (Twitter) profile header | 1500x500 | Unconfirmed | Snippet of the official help page; the top and bottom may be cropped on some screens. |
| Twitch profile banner | 1200x480 | Unconfirmed | Snippet of the official help page. |
| Mastodon profile header | 1500x500 | Unconfirmed | Blogs only. |

No reliable size was found for: Facebook group cover, LinkedIn company page cover, Bluesky
profile banner, Twitch offline banner. Ask the user what the upload dialog says.

Older sizes still in circulation: many Reddit banners were made at 1920x384, and older
Reddit help gave 4000 px wide with heights of 64, 128 or 192 px. An existing banner at
one of these sizes does not mean the platform still wants it.

## Sources

- Reddit for Community, quick-start guide: https://redditforcommunity.com/blog/2-minute-quickstart-guide
- Reddit Help, "Banner" (not reachable when checked): https://support.reddithelp.com/hc/en-us/articles/15484339588884-Banner
- moda.app, Reddit banner sizes (secondary, dated 28 Aug 2026): https://moda.app/resources/sizes/reddit-banner
- YouTube Help, "Manage your channel branding": https://support.google.com/youtube/answer/10456525
- YouTube Help, "Channel banner & profile picture tips": https://support.google.com/youtube/answer/12950272
- Facebook Help, "Page profile picture and cover photo dimensions": https://www.facebook.com/help/125379114252045
- LinkedIn Help, "Add or change the background photo on your profile": https://www.linkedin.com/help/linkedin/answer/a568217
- Discord developer docs, Guild resource: https://docs.discord.com/developers/resources/guild
- Discord support, "Server Banners" (not reachable when checked): https://support.discord.com/hc/en-us/articles/360028716472-Server-Banners
- X Help, "How to customize your profile" (not reachable when checked): https://help.x.com/en/managing-your-account/how-to-customize-your-profile
- Twitch Help, "Channel page setup" (did not load when checked): https://help.twitch.tv/s/article/channel-page-setup

## Habits that survive platform changes

- Keep faces and logos in the middle 60 to 70 percent of the width and away from the
  corners, where avatars and titles are overlaid and phones crop.
- Work at the target size or larger. Do not enlarge a finished banner.
- Keep a PNG master and export a JPEG when the platform limits file size.
- When a platform takes separate desktop and mobile banners, build one layout per size.
