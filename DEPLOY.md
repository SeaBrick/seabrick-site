# Deploying seabrick.com from this repository

Hosting is GitHub Pages, published by `.github/workflows/pages.yml` from the `dist` folder on every push to `main`.
Nothing is built on GitHub: run `python src/build.py` locally, commit `dist`, push.

## 1. Make the repository public (one time, John)

The SeaBrick organisation is on GitHub's free plan, which only serves Pages from public repositories.
Settings → General → Danger Zone → Change visibility → Public.

Before doing so, confirm you are happy for everything tracked here to be public. `.gitignore` already keeps out
`REVIEW.md`, `src/stories.py` and the 2024 to 2026 evolution renders. The journal drafts and all other pages are in.

## 2. Enable Pages (one time)

Settings → Pages → Build and deployment → Source: **GitHub Actions**. Or from a terminal:

```bash
gh api -X POST repos/SeaBrick/seabrick-site/pages -f build_type=workflow
```

Then re-run the "Deploy site to GitHub Pages" workflow (Actions tab → run workflow). The staging site appears at
https://seabrick.github.io/seabrick-site/ within a minute or two.

The pages use root-relative links sparingly; check the home page, one journal article and the builder on the
staging URL before going further.

## 3. Finish the pre-publish list

See `REVIEW.md` (local only) sections 3 and 4. In `src/build.py`: remove the preview band (`PREVIEW_BAND`), the
`noindex` meta tag, and change `robots.txt` to allow crawling. Rebuild, commit, push.

## 4. Custom domain

Only after step 3, because a `CNAME` file makes the staging URL redirect to seabrick.com.

1. Settings → Pages → Custom domain: `seabrick.com`. Save. (This commits a `dist/CNAME` file; pull it afterwards, or
   add the file yourself containing the single line `seabrick.com`.)
2. Tick **Enforce HTTPS** once the certificate has issued (can take up to an hour after DNS is right).

## 5. DNS at GoDaddy (nameservers ns41/ns42.domaincontrol.com)

Mail is on Google Workspace (MX → aspmx.l.google.com). Do not touch MX or TXT records.

Replace the current A record (67.215.15.226, the WordPress host) with the four GitHub Pages addresses, and point
`www` at the organisation's Pages host:

| Type  | Name | Value                  | TTL  |
|-------|------|------------------------|------|
| A     | @    | 185.199.108.153        | 600  |
| A     | @    | 185.199.109.153        | 600  |
| A     | @    | 185.199.110.153        | 600  |
| A     | @    | 185.199.111.153        | 600  |
| CNAME | www  | seabrick.github.io     | 600  |

Optional IPv6: AAAA @ → 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153.

Delete any existing CNAME or A record for `www` that points at the old host. Check with:

```bash
nslookup seabrick.com
```

```bash
nslookup www.seabrick.com
```

## 6. Before the old host is switched off

- Export WordPress (Tools → Export, all content) and download `wp-content/uploads` for the archive.
- List the old URLs (`https://seabrick.com/wp-json/wp/v2/pages` and `/posts` give them) and decide which need a
  landing page here. GitHub Pages has no server-side redirects; `dist/404.html` is what visitors to dead links see.
- Keep the old hosting a week past cutover, then cancel.
