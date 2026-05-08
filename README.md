# gitnav
```
 ██████╗ ██╗████████╗███╗   ██╗ █████╗ ██╗   ██╗
██╔════╝ ██║╚══██╔══╝████╗  ██║██╔══██╗██║   ██║
██║  ███╗██║   ██║   ██╔██╗ ██║███████║██║   ██║
██║   ██║██║   ██║   ██║╚██╗██║██╔══██║╚██╗ ██╔╝
╚██████╔╝██║   ██║   ██║ ╚████║██║  ██║ ╚████╔╝
 ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝
```
browse and manage github repos from your terminal. two modes — classic cli menu or a full-screen tui. picks up where the github cli doesn't bother going.

---

## install

```bash
git clone https://github.com/0xb0rn3/gitnav
cd gitnav && chmod +x gitnav
./gitnav
```

first run asks if you want it installed to `/usr/local/bin`. say yes and you're done — after that just type `gitnav` anywhere.

**dependency:** needs `python-requests`. the script tries to sort this out itself across pacman / apt / dnf / zypper / pip. if it fails:

| distro | command |
|---|---|
| arch / archcraft | `sudo pacman -S python-requests` |
| debian / ubuntu | `sudo apt install python3-requests` |
| fedora / rhel | `sudo dnf install python3-requests` |
| opensuse | `sudo zypper install python3-requests` |
| anything else | `pip install requests --break-system-packages` |

---

## usage

```
gitnav                        # prompts: cli or ui?
gitnav -cli                   # straight to text menu
gitnav -ui                    # straight to full-screen tui
gitnav -u <username>          # skip the username prompt
gitnav -t <token>             # use a github PAT
gitnav -t tok1,tok2,tok3      # multiple tokens — round-robin rotation
gitnav --backup-dir ~/repos   # override default backup location
gitnav --install              # (re)install to /usr/local/bin
gitnav --version              # print version and exit
```

---

## what it does

| feature | detail |
|---|---|
| list repos | name, language, star count, backup badge |
| detailed list | description, forks, size, last updated |
| search | filter by name / description / language |
| stats | star/fork/size totals, language bar chart, local backup stats |
| clone | blobless / shallow / treeless / full — with live git output |
| backup all | clone missing + `git fetch --pull` on existing — resumable |
| backup browser | navigate `~/.gitnav_backups/<user>/` from inside the tui |
| view README | rendered in-terminal with basic markdown formatting |
| issues | open / closed / all, with labels and timestamps |
| releases | list assets, download with progress bar |
| open browser | repo or profile page |
| user profile | followers, bio, join date, public repo count |
| refresh | clears api cache, reloads repo list |

---

## clone strategies

picked at runtime whenever you clone or backup:

| strategy | flag | good for |
|---|---|---|
| **blobless** *(default)* | `--filter=blob:none` | most repos — trees and commits local, blobs fetched on demand |
| **shallow** | `--depth 1` | just need the latest snapshot, don't care about history |
| **treeless** | `--filter=tree:0` | huge repos — only commits stored locally |
| **full** | *(none)* | complete history, maximum compatibility |

all strategies support `--jobs N` for parallel pack threads and automatic retry with exponential backoff on transient network errors.

---

## backup

repos land in `~/.gitnav_backups/<username>/` by default — one directory per repo, same structure as a normal `git clone`. state is tracked in `~/.gitnav_backup_state.json` so subsequent runs skip already-cloned repos and only fetch updates on existing ones.

```
~/.gitnav_backups/
└── 0xb0rn3/
    ├── airjail/        [git]
    ├── gitnav/         [git]
    ├── wallpimp/       [git]
    └── ...
```

backup badges `[bk]` appear next to repo names in the list view so you can see at a glance what's been grabbed.

---

## token

without a PAT you get 60 api requests/hour per ip. fine for casual browsing, annoying if you're iterating. a token bumps this to 5000/hr.

generate one at **github → settings → developer settings → personal access tokens (classic)**. only needs the `public_repo` scope unless you want private repos visible too.

for even higher throughput, pass multiple tokens — gitnav rotates through them round-robin and marks exhausted ones until their reset window:

```bash
gitnav -t ghp_token1,ghp_token2,ghp_token3
```

---

## tui keys

```
↑ ↓            navigate sidebar menu
Enter / Space  select item
PgUp / PgDn    scroll content pane
r              refresh (clear cache + reload repos)
b              jump to Backup All Repos
q              quit
```

---

## changelog

### v2.1.0
- **fix:** arrow keys / escape sequences no longer leak into the content pane during backup or clone. terminal echo is suppressed (`ECHO | ICANON` cleared) for the duration of any subprocess call, and stdin is drained on completion so buffered keypresses don't trigger spurious menu actions.
- **fix:** default clone destination is now `~/.gitnav_backups/<username>/` in both cli and tui modes instead of cwd. the destination directory is created automatically if it doesn't exist.
- backup state is recorded on individual clones (`Clone` menu item) as well as full backups.
- download asset default save path updated to match backup dir.

### v2.0.0
- full-screen tui with live rate-limit bar, scrollbar, wider sidebar
- clone rate bypass — blobless / shallow / treeless filters, `--jobs`, retry + backoff
- multi-token pool — comma-separated `-t tok1,tok2,tok3` — round-robin rotation
- backup all repos — full user backup with json state, smart skip / update
- resume backup — only clone missing, `git fetch --pull` on existing
- backup dir browser — navigate local backup dirs from inside the tui

### v1.x
- initial cli-only release

---

**oxbv1 | oxborn3** — [oxborn3.com](https://oxborn3.com) — [contact@oxborn3.com](mailto:contact@oxborn3.com)
