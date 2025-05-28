#!/usr/bin/env python3
"""
GitNav v0.0.2 - Enhanced GitHub Navigator
A comprehensive tool for exploring and managing GitHub repositories
"""

import requests
import subprocess
import base64
import webbrowser
import json
from datetime import datetime
import os

# Configuration
API_BASE = "https://api.github.com"
VERSION = "0.0.2"

class GitHubAPI:
    """Handles all GitHub API interactions with improved error handling"""
    
    def __init__(self):
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
    
    def make_request(self, url, params=None):
        """Make API request with comprehensive error handling"""
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print("❌ Error: Resource not found (user/repo doesn't exist)")
            elif response.status_code == 403:
                print("❌ Error: API rate limit exceeded or access forbidden")
                if 'X-RateLimit-Reset' in response.headers:
                    reset_time = datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
                    print(f"   Rate limit resets at: {reset_time}")
            elif response.status_code == 422:
                print("❌ Error: Invalid request parameters")
            else:
                print(f"❌ Error: HTTP {response.status_code} - {response.reason}")
            
            return None
            
        except requests.exceptions.Timeout:
            print("❌ Error: Request timed out")
        except requests.exceptions.ConnectionError:
            print("❌ Error: Connection failed - check your internet connection")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: Request failed - {e}")
        
        return None

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def format_date(date_string):
    """Format ISO date string to readable format"""
    if not date_string:
        return "Never"
    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime("%Y-%m-%d %H:%M")
    except:
        return date_string

def fetch_user_profile(api, username):
    """Fetch detailed user profile information"""
    url = f"{API_BASE}/users/{username}"
    return api.make_request(url)

def display_user_profile(profile):
    """Display user profile in a formatted way"""
    if not profile:
        return
    
    print(f"\n👤 User Profile: {profile['login']}")
    print("=" * 50)
    
    if profile.get('name'):
        print(f"Name: {profile['name']}")
    if profile.get('bio'):
        print(f"Bio: {profile['bio']}")
    if profile.get('company'):
        print(f"Company: {profile['company']}")
    if profile.get('location'):
        print(f"Location: {profile['location']}")
    if profile.get('blog'):
        print(f"Website: {profile['blog']}")
    
    print(f"Public Repos: {profile['public_repos']}")
    print(f"Followers: {profile['followers']}")
    print(f"Following: {profile['following']}")
    print(f"Account Created: {format_date(profile['created_at'])}")

def fetch_repos(api, username, sort='updated', per_page=100):
    """Fetch repositories with sorting options"""
    url = f"{API_BASE}/users/{username}/repos"
    params = {'sort': sort, 'per_page': per_page}
    return api.make_request(url, params)

def display_repo_stats(repos):
    """Display aggregate statistics about repositories"""
    if not repos:
        return
    
    total_repos = len(repos)
    total_stars = sum(repo['stargazers_count'] for repo in repos)
    total_forks = sum(repo['forks_count'] for repo in repos)
    total_size = sum(repo['size'] * 1024 for repo in repos)  # GitHub size is in KB
    
    languages = {}
    for repo in repos:
        lang = repo.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    
    print(f"\n📊 Repository Statistics")
    print("=" * 30)
    print(f"Total Repositories: {total_repos}")
    print(f"Total Stars: {total_stars}")
    print(f"Total Forks: {total_forks}")
    print(f"Total Size: {format_size(total_size)}")
    
    if languages:
        print(f"Top Languages: {', '.join(sorted(languages.keys(), key=languages.get, reverse=True)[:5])}")

def list_repos(repos, show_details=False):
    """List repositories with optional detailed information"""
    if not repos:
        print("No repositories found.")
        return
    
    for i, repo in enumerate(repos, 1):
        description = repo.get('description', 'No description')
        stars = repo['stargazers_count']
        forks = repo['forks_count']
        language = repo.get('language', 'Unknown')
        
        if show_details:
            size = format_size(repo['size'] * 1024)
            updated = format_date(repo['updated_at'])
            print(f"{i:2d}. 📁 {repo['name']}")
            print(f"     {description}")
            print(f"     ⭐ {stars} | 🍴 {forks} | 💻 {language} | 📦 {size} | 🕒 {updated}")
            if repo['private']:
                print("     🔒 Private")
            print()
        else:
            print(f"{i:2d}. 📁 {repo['name']} - {description}")
            print(f"     ⭐ {stars} | 🍴 {forks} | 💻 {language}")

def search_repos(repos):
    """Search repositories by name or description"""
    term = input("🔍 Enter search term: ").lower().strip()
    if not term:
        print("Search term cannot be empty.")
        return
    
    matches = []
    for repo in repos:
        name_match = term in repo['name'].lower()
        desc_match = repo.get('description') and term in repo['description'].lower()
        lang_match = repo.get('language') and term in repo['language'].lower()
        
        if name_match or desc_match or lang_match:
            matches.append(repo)
    
    if matches:
        print(f"\n🎯 Found {len(matches)} matching repositories:")
        list_repos(matches, show_details=True)
    else:
        print("❌ No matching repositories found.")

def clone_repo(clone_url, repo_name):
    """Clone repository with better feedback"""
    try:
        print(f"📥 Cloning {repo_name}...")
        result = subprocess.run(
            ["git", "clone", clone_url], 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ Repository '{repo_name}' cloned successfully!")
        
        # Check if directory was created
        if os.path.exists(repo_name):
            print(f"📁 Files saved to: {os.path.abspath(repo_name)}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone repository: {e.stderr}")
    except FileNotFoundError:
        print("❌ Git is not installed or not in PATH.")
        print("   Please install Git from: https://git-scm.com/")

def clone_repository(repos):
    """Handle repository cloning with user selection"""
    if not repos:
        print("No repositories available to clone.")
        return
    
    list_repos(repos)
    try:
        repo_num = int(input("\n📥 Enter repository number to clone: "))
        if 1 <= repo_num <= len(repos):
            repo = repos[repo_num - 1]
            clone_url = repo['clone_url']
            repo_name = repo['name']
            clone_repo(clone_url, repo_name)
        else:
            print("❌ Invalid repository number.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")

def view_readme(api, repos, username):
    """View README content with better formatting"""
    if not repos:
        print("No repositories available.")
        return
    
    list_repos(repos)
    try:
        repo_num = int(input("\n📖 Enter repository number to view README: "))
        if 1 <= repo_num <= len(repos):
            repo_name = repos[repo_num - 1]['name']
            url = f"{API_BASE}/repos/{username}/{repo_name}/readme"
            readme_data = api.make_request(url)
            
            if readme_data:
                try:
                    content = base64.b64decode(readme_data['content']).decode('utf-8')
                    print(f"\n📖 README for {repo_name}")
                    print("=" * 60)
                    print(content)
                    print("=" * 60)
                except Exception as e:
                    print(f"❌ Error decoding README content: {e}")
            else:
                print("❌ README not found or not accessible.")
        else:
            print("❌ Invalid repository number.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")

def fetch_issues(api, username, repo_name, state='open'):
    """Fetch repository issues"""
    url = f"{API_BASE}/repos/{username}/{repo_name}/issues"
    params = {'state': state, 'per_page': 50}
    return api.make_request(url, params)

def view_issues(api, repos, username):
    """View repository issues"""
    if not repos:
        print("No repositories available.")
        return
    
    list_repos(repos)
    try:
        repo_num = int(input("\n🐛 Enter repository number to view issues: "))
        if 1 <= repo_num <= len(repos):
            repo_name = repos[repo_num - 1]['name']
            
            print("\nSelect issue state:")
            print("1. Open issues")
            print("2. Closed issues")
            print("3. All issues")
            
            state_choice = input("Enter choice (1-3): ").strip()
            state_map = {'1': 'open', '2': 'closed', '3': 'all'}
            state = state_map.get(state_choice, 'open')
            
            issues = fetch_issues(api, username, repo_name, state)
            
            if issues:
                print(f"\n🐛 Issues for {repo_name} ({state}):")
                print("=" * 50)
                
                for i, issue in enumerate(issues, 1):
                    title = issue['title']
                    number = issue['number']
                    user = issue['user']['login']
                    created = format_date(issue['created_at'])
                    labels = ', '.join([label['name'] for label in issue.get('labels', [])])
                    
                    print(f"{i:2d}. #{number} - {title}")
                    print(f"     👤 {user} | 🕒 {created}")
                    if labels:
                        print(f"     🏷️  {labels}")
                    print()
            else:
                print(f"❌ No {state} issues found for this repository.")
        else:
            print("❌ Invalid repository number.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")

def fetch_releases(api, username, repo_name):
    """Fetch repository releases"""
    url = f"{API_BASE}/repos/{username}/{repo_name}/releases"
    return api.make_request(url)

def download_assets(api, repos, username):
    """Download release assets with improved UX"""
    if not repos:
        print("No repositories available.")
        return
    
    list_repos(repos)
    try:
        repo_num = int(input("\n📦 Enter repository number: "))
        if 1 <= repo_num <= len(repos):
            repo = repos[repo_num - 1]
            repo_name = repo['name']
            releases = fetch_releases(api, username, repo_name)
            
            if releases:
                print(f"\n📦 Releases for {repo_name}:")
                for i, release in enumerate(releases, 1):
                    tag = release['tag_name']
                    name = release.get('name', tag)
                    published = format_date(release['published_at'])
                    assets_count = len(release['assets'])
                    
                    print(f"{i:2d}. {name} ({tag}) - {assets_count} assets | 🕒 {published}")
                
                release_num = int(input("\nEnter release number: "))
                if 1 <= release_num <= len(releases):
                    release = releases[release_num - 1]
                    assets = release['assets']
                    
                    if assets:
                        print(f"\n📎 Assets in {release['tag_name']}:")
                        for j, asset in enumerate(assets, 1):
                            name = asset['name']
                            size = format_size(asset['size'])
                            downloads = asset['download_count']
                            print(f"{j:2d}. {name} | 📦 {size} | ⬇️  {downloads} downloads")
                        
                        asset_num = int(input("\nEnter asset number to download: "))
                        if 1 <= asset_num <= len(assets):
                            asset = assets[asset_num - 1]
                            download_url = asset['browser_download_url']
                            asset_name = asset['name']
                            
                            print(f"⬇️  Downloading {asset_name}...")
                            response = requests.get(download_url, stream=True)
                            
                            if response.status_code == 200:
                                with open(asset_name, 'wb') as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                print(f"✅ Download complete: {asset_name}")
                            else:
                                print(f"❌ Download failed: HTTP {response.status_code}")
                        else:
                            print("❌ Invalid asset number.")
                    else:
                        print("❌ No assets in this release.")
                else:
                    print("❌ Invalid release number.")
            else:
                print("❌ No releases found for this repository.")
        else:
            print("❌ Invalid repository number.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")

def open_in_browser(repos):
    """Open repository in browser"""
    if not repos:
        print("No repositories available.")
        return
    
    list_repos(repos)
    try:
        repo_num = int(input("\n🌐 Enter repository number to open: "))
        if 1 <= repo_num <= len(repos):
            repo_url = repos[repo_num - 1]['html_url']
            webbrowser.open(repo_url)
            print(f"🌐 Opening {repos[repo_num - 1]['name']} in browser...")
        else:
            print("❌ Invalid repository number.")
    except ValueError:
        print("❌ Invalid input. Please enter a number.")

def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 50)
    print("📋 GitNav Menu")
    print("=" * 50)
    print("1.  📋 List repositories")
    print("2.  📋+ List repositories (detailed)")
    print("3.  🔍 Search repositories")
    print("4.  📊 Show repository statistics")
    print("5.  📥 Clone a repository")
    print("6.  📖 View README")
    print("7.  🐛 View issues")
    print("8.  📦 Download release assets")
    print("9.  🌐 Open in browser")
    print("10. 👤 Show user profile")
    print("11. 🔄 Refresh repositories")
    print("12. ❌ Exit")
    print("=" * 50)

def menu_loop(api, repos, username):
    """Main menu loop with enhanced options"""
    user_profile = None
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-12): ").strip()
        
        if choice == '1':
            list_repos(repos)
        elif choice == '2':
            list_repos(repos, show_details=True)
        elif choice == '3':
            search_repos(repos)
        elif choice == '4':
            display_repo_stats(repos)
        elif choice == '5':
            clone_repository(repos)
        elif choice == '6':
            view_readme(api, repos, username)
        elif choice == '7':
            view_issues(api, repos, username)
        elif choice == '8':
            download_assets(api, repos, username)
        elif choice == '9':
            open_in_browser(repos)
        elif choice == '10':
            if not user_profile:
                user_profile = fetch_user_profile(api, username)
            display_user_profile(user_profile)
        elif choice == '11':
            print("🔄 Refreshing repositories...")
            new_repos = fetch_repos(api, username)
            if new_repos:
                repos.clear()
                repos.extend(new_repos)
                print(f"✅ Refreshed! Found {len(repos)} repositories.")
            else:
                print("❌ Failed to refresh repositories.")
        elif choice == '12':
            print("👋 Thanks for using GitNav! Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1-12.")

def display_banner():
    """Display the GitNav ASCII banner with credits"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██╗████████╗███╗   ██╗ █████╗ ██╗   ██╗    ██╗   ██╗ ██████╗      ║
║  ██╔════╝ ██║╚══██╔══╝████╗  ██║██╔══██╗██║   ██║    ██║   ██║██╔═████╗     ║
║  ██║  ███╗██║   ██║   ██╔██╗ ██║███████║██║   ██║    ██║   ██║██║██╔██║     ║
║  ██║   ██║██║   ██║   ██║╚██╗██║██╔══██║╚██╗ ██╔╝    ╚██╗ ██╔╝████╔╝██║     ║
║  ╚██████╔╝██║   ██║   ██║ ╚████║██║  ██║ ╚████╔╝      ╚████╔╝ ╚██████╔╝     ║
║   ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝        ╚═══╝   ╚═════╝      ║
║                                                                              ║
║                    🚀 Cli GitHub Repository Navigator                        ║
║                              Version """ + VERSION + """                     ║
║                                                                              ║
║                        💻 Coded by 0xb0rn3 | 0xbv1 💻                        ║
║                    🌟 Your Gateway to GitHub Excellence 🌟                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main function with enhanced startup"""
    display_banner()
    
    username = input("Enter GitHub username: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return
    
    api = GitHubAPI()
    print(f"🔍 Fetching repositories for '{username}'...")
    
    repos = fetch_repos(api, username)
    if repos:
        print(f"✅ Found {len(repos)} repositories!")
        display_repo_stats(repos)
        menu_loop(api, repos, username)
    else:
        print("❌ Unable to proceed without repositories.")
        print("   Please check the username and try again.")

if __name__ == "__main__":
    main()
