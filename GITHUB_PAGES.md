# Hosting on GitHub Pages

This guide explains how to host **personal**, **organization**, or **project** pages from a GitHub repository — and how SmartApp is already wired up to do exactly that.

---

## Table of Contents

1. [What is GitHub Pages?](#1-what-is-github-pages)
2. [Types of GitHub Pages sites](#2-types-of-github-pages-sites)
3. [How SmartApp generates its static site](#3-how-smartapp-generates-its-static-site)
4. [Automated deployment with GitHub Actions](#4-automated-deployment-with-github-actions)
5. [Enable GitHub Pages in your repository settings](#5-enable-github-pages-in-your-repository-settings)
6. [Custom domain (optional)](#6-custom-domain-optional)
7. [Quick-start checklist](#7-quick-start-checklist)

---

## 1. What is GitHub Pages?

GitHub Pages is a free static-site hosting service built into every GitHub repository.  
Pages are served from:
- a dedicated `gh-pages` branch, **or**
- the `main` / `master` branch (root or `/docs` folder).

Because GitHub Pages only serves **static files** (HTML, CSS, JS, images), the Flask application itself cannot run there. SmartApp solves this by pre-rendering the public-facing login page into plain HTML before deployment.

---

## 2. Types of GitHub Pages sites

| Type | Repository name required | Default URL |
|---|---|---|
| **User** (personal) | `<username>.github.io` | `https://<username>.github.io` |
| **Organization** | `<org-name>.github.io` | `https://<org-name>.github.io` |
| **Project** | any name | `https://<username>.github.io/<repo-name>` |

SmartApp lives in `hamzap-ux/SmartApp`, so it is a **project page** and is served at:

```
https://hamzap-ux.github.io/SmartApp/
```

> **Tip:** To turn it into a user/personal site, rename the repository to `hamzap-ux.github.io`. The site will then be served at the root URL `https://hamzap-ux.github.io/`.

---

## 3. How SmartApp generates its static site

Because GitHub Pages cannot execute Python, a helper script (`freeze_static.py`) pre-renders the Jinja2 templates into static HTML and copies all CSS/JS/image assets.

### What the script does

1. Uses a minimal Jinja2 environment (no Flask runtime needed).
2. Renders `templates/login.html` → `build/index.html` (the public landing page).
3. Copies `static/` → `build/static/` (CSS, JS, images).

### Run it locally

```bash
pip install Jinja2
python freeze_static.py
# Output is in the build/ directory
open build/index.html   # macOS
xdg-open build/index.html   # Linux
```

---

## 4. Automated deployment with GitHub Actions

The file `.github/workflows/gh-pages-deploy.yml` automates the entire build-and-publish pipeline.

```yaml
name: Build & deploy static login to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install Jinja2
      - run: python freeze_static.py
      - uses: peaceiris/actions-gh-pages@v3
        with:
          personal_token: ${{ secrets.GH_PAGES_PAT || github.token }}
          publish_dir: ./build
```

**How it works:**

1. Triggered on every push to `main` (or manually via the GitHub UI → *Actions → Run workflow*).
2. Checks out the code and installs only Jinja2 (no heavy dependencies).
3. Runs `freeze_static.py` to produce the `build/` directory.
4. The `peaceiris/actions-gh-pages` action force-pushes `build/` to the `gh-pages` branch.

### Optional: `GH_PAGES_PAT` secret

If the repository's default `GITHUB_TOKEN` does not have write access to the `gh-pages` branch (common in organizations with restricted permissions), add a Personal Access Token:

1. Go to **GitHub → Settings → Developer settings → Personal access tokens**.
2. Create a token with the `repo` scope.
3. In the repository go to **Settings → Secrets and variables → Actions → New repository secret**.
4. Name it `GH_PAGES_PAT` and paste the token.

---

## 5. Enable GitHub Pages in your repository settings

After the first successful workflow run (which creates the `gh-pages` branch), activate the site:

1. Open the repository on GitHub.
2. Go to **Settings → Pages**.
3. Under **Source**, select:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
4. Click **Save**.

GitHub will display the live URL (e.g., `https://hamzap-ux.github.io/SmartApp/`) once the site is published — usually within 1–2 minutes.

---

## 6. Custom domain (optional)

You can serve GitHub Pages from your own domain:

1. In **Settings → Pages → Custom domain**, enter your domain (e.g., `smartapp.example.com`).
2. Add a `CNAME` file to the `publish_dir` (`build/`) containing just your domain:

   ```
   smartapp.example.com
   ```

   Or let the `peaceiris/actions-gh-pages` action create it automatically:

   ```yaml
   - uses: peaceiris/actions-gh-pages@v3
     with:
       personal_token: ${{ secrets.GH_PAGES_PAT || github.token }}
       publish_dir: ./build
       cname: smartapp.example.com   # add this line
   ```

3. At your DNS provider, create a `CNAME` record pointing `smartapp.example.com` → `hamzap-ux.github.io`.
4. Enable **Enforce HTTPS** in **Settings → Pages** once the DNS propagates.

---

## 7. Quick-start checklist

- [ ] Push your code to the `main` branch.
- [ ] Confirm `.github/workflows/gh-pages-deploy.yml` is present.
- [ ] (If needed) Add `GH_PAGES_PAT` to repository secrets.
- [ ] Trigger the workflow: push a commit **or** go to *Actions → Build & deploy static login to GitHub Pages → Run workflow*.
- [ ] Go to **Settings → Pages**, set source to branch `gh-pages` / root, and save.
- [ ] Visit `https://hamzap-ux.github.io/SmartApp/` — your static login page is live!
- [ ] (Optional) Configure a custom domain and add a `CNAME` entry.
