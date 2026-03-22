# 🚀 GitNav v0.1.0

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██╗████████╗███╗   ██╗ █████╗ ██╗   ██╗                           ║
║  ██╔════╝ ██║╚══██╔══╝████╗  ██║██╔══██╗██║   ██║                           ║
║  ██║  ███╗██║   ██║   ██╔██╗ ██║███████║██║   ██║                           ║
║  ██║   ██║██║   ██║   ██║╚██╗██║██╔══██║╚██╗ ██╔╝    v0.1.0                 ║
║  ╚██████╔╝██║   ██║   ██║ ╚████║██║  ██║ ╚████╔╝                            ║
║   ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝                            ║
║                                                                              ║
║              🚀 Enhanced GitHub Repository Navigator                         ║
║        oxbv1 | oxborn3  ·  oxborn3.com  ·  contact@oxborn3.com               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**The Ultimate Command-Line Tool for GitHub Repository Management**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-brightgreen.svg)](https://github.com/0xb0rn3/gitnav)
[![GitHub Issues](https://img.shields.io/badge/Issues-Welcome-red.svg)](https://github.com/0xb0rn3/gitnav/issues)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-orange.svg)](CONTRIBUTING.md)

</div>

---

## 🌟 Overview

GitNav is a powerful, dual-interface command-line tool for exploring, managing, and analyzing GitHub repositories — directly from your terminal.

Choose between a classic **CLI menu mode** or a fully interactive **TUI (full-screen UI)** mode, both packed with the same feature set. On first run, GitNav offers to install itself system-wide so you can call it from anywhere.

Built by **oxbv1 | oxborn3** — [oxborn3.com](https://oxborn3.com) — [contact@oxborn3.com](mailto:contact@oxborn3.com)

---

## ✨ What's New in v0.1.0

- **Dual interface** — `gitnav -cli` for classic menus, `gitnav -ui` for full-screen TUI
- **`gitnav` alone** prompts you to pick CLI or UI at launch
- **Animated splash screen** with streaming ASCII logo and progress bar (UI mode)
- **System-wide install prompt** on first run — places binary in `/usr/local/bin/gitnav`
- **Threaded loader animations** — spinner in-place while API calls run
- **Keyboard-driven TUI** — arrow keys navigate sidebar, Enter/Space selects, PgUp/Dn scrolls
- **Inline input prompts** appear inside the content pane (no terminal break)
- **SIGWINCH resize handling** — TUI redraws cleanly on terminal resize
- **GitHub token support** via `-t TOKEN` for authenticated (5000 req/hr) access
- **Rate limit awareness** — warns when approaching GitHub API limits
- No `.py` extension — runs as `gitnav` after install

---

## ✨ Key Features

### 🎯 Repository Management
- **Smart Listing** — view all repos with stars, forks, language, size
- **Detailed List** — expanded view with descriptions, update timestamps, privacy status
- **Advanced Search** — fuzzy match across names, descriptions, and languages
- **Statistics Dashboard** — aggregate star/fork/size counts, language bar charts

### 📊 Project Insights
- **Issue Tracking** — browse open / closed / all issues with labels and timestamps
- **Release Management** — explore releases, view assets with download counts and sizes
- **README Viewer** — lightweight Markdown rendering with heading highlights
- **User Profiles** — bio, location, followers, repo counts, member since

### 🔧 Developer Experience
- **Repository Cloning** — calls `git clone --progress` with live output streaming
- **Asset Downloading** — streamed downloads with an inline progress bar
- **Browser Integration** — open any repo or profile in your default browser
- **Data Refresh** — clears cache and reloads without restarting

### 🚀 Performance & Reliability
- **In-memory caching** — avoids redundant API calls within a session
- **Timeout protection** — 15 s request timeout prevents hangs
- **Rate limit guard** — detects remaining quota and warns before hitting the wall
- **Full error handling** — actionable messages for 401 / 403 / 404 / connection errors

---

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.7+**
- **`requests` library** — `pip install requests`
- **Git** — for clone functionality
- Internet access

### Quick Install

```bash
# Clone the repository
git clone https://github.com/0xb0rn3/gitnav.git
cd gitnav

# Install dependency
pip install requests

# Make executable
chmod +x gitnav

# Run (will offer system-wide install on first launch)
./gitnav
```

**Direct download:**
```bash
wget https://raw.githubusercontent.com/0xb0rn3/gitnav/main/gitnav
chmod +x gitnav
./gitnav
```

### System-Wide Install (manual)

```bash
sudo cp gitnav /usr/local/bin/gitnav
sudo chmod 755 /usr/local/bin/gitnav
```

Or just run `gitnav` once — it will ask if you want to install automatically.

---

## 🎮 Usage

```
gitnav                  # prompt for CLI or UI mode
gitnav -cli             # start in classic text-menu mode
gitnav -ui              # start in full-screen interactive TUI
gitnav -u octocat       # pre-load a GitHub username
gitnav -t <TOKEN>       # use a personal access token
gitnav --install        # install to /usr/local/bin/gitnav
gitnav --version        # print version
gitnav --help           # show all options
```

### Interface Modes

| Mode | Flag | Best for |
|------|------|----------|
| **CLI** | `gitnav -cli` | Any terminal, SSH sessions, scripting |
| **UI**  | `gitnav -ui`  | Local terminal, interactive exploration |

### TUI Keyboard Controls

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move sidebar selection |
| `Enter` / `Space` | Activate selected menu item |
| `PgUp` / `PgDn` | Scroll content panel |
| `r` | Refresh data (clears cache) |
| `q` | Quit |

### Available Actions (both modes)

| # | Action | Description |
|---|--------|-------------|
| 1 | 📋 List Repositories | Quick overview with stars, forks, language |
| 2 | 📋 Detailed List | Full metadata per repo with descriptions |
| 3 | 🔍 Search Repositories | Filter by name, description, or language |
| 4 | 📊 Repository Statistics | Aggregated analytics + language bar chart |
| 5 | 📥 Clone Repository | Clone with live git progress output |
| 6 | 📖 View README | Render README with basic Markdown formatting |
| 7 | 🐛 View Issues | Browse issues by state (open/closed/all) |
| 8 | 📦 Releases & Downloads | View releases; optionally download assets |
| 9 | 🌐 Open in Browser | Open repo or profile in your web browser |
| 10 | 👤 User Profile | View any GitHub user's profile data |
| 11 | 🔄 Refresh Data | Clear API cache and reload |
| 12 | ❌ Exit | Quit gracefully |

---

## 🔑 GitHub Token (Optional)

Without a token, GitHub allows **60 API requests/hour** per IP. With a token (free):

```bash
gitnav -t ghp_yourTokenHere
```

Create a token at: **GitHub → Settings → Developer settings → Personal access tokens**
Scopes needed: `public_repo` (or `repo` for private repos).

---

## 🛡️ Notes

- GitNav only reads data from GitHub. It never writes, pushes, or modifies repository content.
- All API calls go directly to `api.github.com`. No third-party proxies.
- Token is passed as a header; never logged or stored.

---

## 📬 Developer

| | |
|---|---|
| **Handle** | oxbv1 \| oxborn3 |
| **Site** | [oxborn3.com](https://oxborn3.com) |
| **Email** | [contact@oxborn3.com](mailto:contact@oxborn3.com) |
| **Repo** | [github.com/0xb0rn3/gitnav](https://github.com/0xb0rn3/gitnav) |

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
<sub>Built with 🖤 by oxbv1 | oxborn3 &mdash; your gateway to GitHub, from the terminal.</sub>
</div>
