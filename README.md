# gitnav

```
 ██████╗ ██╗████████╗███╗   ██╗ █████╗ ██╗   ██╗
██╔════╝ ██║╚══██╔══╝████╗  ██║██╔══██╗██║   ██║
██║  ███╗██║   ██║   ██╔██╗ ██║███████║██║   ██║
██║   ██║██║   ██║   ██║╚██╗██║██╔══██║╚██╗ ██╔╝
╚██████╔╝██║   ██║   ██║ ╚████║██║  ██║ ╚████╔╝
 ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝
```

browse github repos from your terminal. two modes — classic cli menu or a full-screen tui. picks up where the github cli doesn't bother going.

---

## install

```bash
git clone https://github.com/0xb0rn3/gitnav
cd gitnav && chmod +x gitnav
./gitnav
```

first run asks if you want it installed to `/usr/local/bin`. say yes and you're done.

**dependency:** needs `python-requests`. the script tries to sort this out itself, but if it can't:

| distro | command |
|--------|---------|
| arch / archcraft | `sudo pacman -S python-requests` |
| debian / ubuntu | `sudo apt install python3-requests` |
| fedora | `sudo dnf install python3-requests` |
| anything else | `pip install requests --break-system-packages` |

---

## usage

```
gitnav               # prompts: cli or ui?
gitnav -cli          # straight to text menu
gitnav -ui           # straight to full-screen tui
gitnav -u <user>     # skip the username prompt
gitnav -t <token>    # use a pat (5000 req/hr vs 60)
gitnav --install     # (re)install to /usr/local/bin
```

---

## what it does

- list / search repos — name, description, language filter
- stats — star/fork/size totals, language breakdown bar chart
- clone with live git output
- view issues (open / closed / all)
- view releases and download assets
- render readme in-terminal with basic markdown
- open any repo or profile in browser
- user profile lookup

---

## tui keys

```
↑ ↓          navigate sidebar
Enter/Space  select
PgUp PgDn    scroll content
r            refresh (clears cache)
q            quit
```

---

## token

without one you get 60 api requests/hour per ip. fine for casual use, annoying if you're iterating fast. generate one at github → settings → developer settings → personal access tokens. only needs `public_repo` scope unless you want private repos.

---

**oxbv1 | oxborn3** — [oxborn3.com](https://oxborn3.com) — [contact@oxborn3.com](mailto:contact@oxborn3.com)
