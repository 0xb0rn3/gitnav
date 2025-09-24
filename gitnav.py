#!/usr/bin/env python3
"""
GitNav v0.0.3 - Enhanced GitHub Navigator with Full Backup & Proxy Support
A comprehensive tool for exploring, managing, and backing up GitHub repositories
Features: Full repo backup, sync updates, proxy rotation for large operations
"""

import requests
import subprocess
import base64
import webbrowser
import json
from datetime import datetime
import os
import sys
import time
from pathlib import Path
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Configuration
API_BASE = "https://api.github.com"
VERSION = "0.0.3"
DEFAULT_BACKUP_DIR = "github_backups"
CLONE_THREADS = 3  # Number of parallel clone operations

class ProxyManager:
    """Manages proxy rotation for handling rate limits and large operations"""
    
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.enabled = False
        self.proxy_file = "proxies.txt"
        self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from file if it exists"""
        if os.path.exists(self.proxy_file):
            try:
                with open(self.proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                if self.proxies:
                    print(f"📡 Loaded {len(self.proxies)} proxies from {self.proxy_file}")
            except Exception as e:
                print(f"⚠️ Could not load proxies: {e}")
    
    def add_proxy(self, proxy):
        """Add a proxy to the rotation list"""
        # Validate proxy format (basic check)
        if '://' in proxy or ':' in proxy:
            self.proxies.append(proxy)
            self.save_proxies()
            return True
        return False
    
    def save_proxies(self):
        """Save current proxy list to file"""
        try:
            with open(self.proxy_file, 'w') as f:
                for proxy in self.proxies:
                    f.write(f"{proxy}\n")
        except Exception as e:
            print(f"⚠️ Could not save proxies: {e}")
    
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies or not self.enabled:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        # Format proxy for requests library
        if '://' not in proxy:
            proxy = f"http://{proxy}"
        
        return {
            'http': proxy,
            'https': proxy
        }
    
    def test_proxy(self, proxy_url):
        """Test if a proxy is working"""
        try:
            test_proxy = {'http': proxy_url, 'https': proxy_url} if '://' not in proxy_url else proxy_url
            response = requests.get('https://api.github.com', proxies=test_proxy, timeout=5)
            return response.status_code == 200
        except:
            return False

class BackupManager:
    """Manages repository backup and synchronization operations"""
    
    def __init__(self, backup_dir=DEFAULT_BACKUP_DIR):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Load backup metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def save_metadata(self):
        """Save backup metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_user_backup_dir(self, username):
        """Get or create user-specific backup directory"""
        user_dir = self.backup_dir / username
        user_dir.mkdir(exist_ok=True)
        return user_dir
    
    def is_repo_cloned(self, username, repo_name):
        """Check if a repository has been cloned"""
        repo_path = self.get_user_backup_dir(username) / repo_name
        return repo_path.exists() and (repo_path / '.git').exists()
    
    def get_repo_info(self, username, repo_name):
        """Get stored information about a cloned repository"""
        key = f"{username}/{repo_name}"
        return self.metadata.get(key, {})
    
    def update_repo_info(self, username, repo_name, info):
        """Update stored information about a repository"""
        key = f"{username}/{repo_name}"
        self.metadata[key] = info
        self.save_metadata()

class GitHubAPI:
    """Handles all GitHub API interactions with proxy support"""
    
    def __init__(self, proxy_manager=None):
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        self.proxy_manager = proxy_manager
        self.request_count = 0
        self.last_request_time = time.time()
    
    def _apply_rate_limit(self):
        """Apply rate limiting to avoid hitting GitHub limits"""
        # Limit to 30 requests per minute when not using proxies
        if not self.proxy_manager or not self.proxy_manager.enabled:
            elapsed = time.time() - self.last_request_time
            if elapsed < 2:  # Wait at least 2 seconds between requests
                time.sleep(2 - elapsed)
            self.last_request_time = time.time()
    
    def make_request(self, url, params=None):
        """Make API request with proxy rotation and rate limit handling"""
        try:
            # Apply rate limiting to avoid hitting GitHub limits
            self._apply_rate_limit()
            
            # Get proxy if enabled
            proxies = None
            if self.proxy_manager and self.proxy_manager.enabled:
                print("   Trying next proxy...")
                return self.make_request(url, params)
        except Exception as e:
            print(f"❌ Error: {e}")
        
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

def clone_repo_with_progress(clone_url, repo_path, repo_name):
    """Clone repository with progress indication"""
    try:
        print(f"📥 Cloning {repo_name}...")
        
        # Use subprocess to show git progress
        process = subprocess.Popen(
            ["git", "clone", "--progress", clone_url, str(repo_path)],
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Show progress from git
        for line in process.stderr:
            if 'Counting objects' in line or 'Compressing objects' in line or 'Receiving objects' in line:
                print(f"   {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error cloning {repo_name}: {e}")
        return False

def update_repo(repo_path, repo_name):
    """Update an existing repository"""
    try:
        print(f"🔄 Updating {repo_name}...")
        
        # Change to repo directory and pull
        result = subprocess.run(
            ["git", "-C", str(repo_path), "pull", "--all"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            if "Already up to date" in result.stdout:
                print(f"   ✓ {repo_name} is already up to date")
            else:
                print(f"   ✅ {repo_name} updated successfully")
            return True
        else:
            print(f"   ⚠️ Warning: Could not update {repo_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {repo_name}: {e}")
        return False

def backup_all_repos(api, repos, username, backup_manager, max_workers=CLONE_THREADS):
    """Backup all repositories for a user with parallel cloning"""
    if not repos:
        print("No repositories to backup.")
        return
    
    user_dir = backup_manager.get_user_backup_dir(username)
    print(f"\n🗂️ Backup directory: {user_dir.absolute()}")
    
    # Separate repos into already cloned and new
    to_clone = []
    already_cloned = []
    
    for repo in repos:
        if backup_manager.is_repo_cloned(username, repo['name']):
            already_cloned.append(repo)
        else:
            to_clone.append(repo)
    
    print(f"\n📊 Backup Status:")
    print(f"   • Already backed up: {len(already_cloned)} repositories")
    print(f"   • To backup: {len(to_clone)} repositories")
    print(f"   • Total: {len(repos)} repositories")
    
    if not to_clone:
        print("\n✅ All repositories are already backed up!")
        
        # Ask if user wants to update existing repos
        update_choice = input("\n🔄 Would you like to update existing repositories? (y/n): ").lower()
        if update_choice == 'y':
            update_all_cloned_repos(backup_manager, already_cloned, username, max_workers)
        return
    
    # Confirm backup
    print(f"\n⚠️ This will clone {len(to_clone)} repositories")
    total_size = sum(repo['size'] * 1024 for repo in to_clone)
    print(f"   Estimated size: {format_size(total_size)}")
    
    confirm = input("\nProceed with backup? (y/n): ").lower()
    if confirm != 'y':
        print("Backup cancelled.")
        return
    
    # Clone repositories in parallel
    print(f"\n🚀 Starting backup with {max_workers} parallel threads...")
    start_time = time.time()
    
    successful = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        for repo in to_clone:
            repo_path = user_dir / repo['name']
            future = executor.submit(
                clone_repo_with_progress,
                repo['clone_url'],
                repo_path,
                repo['name']
            )
            futures[future] = repo
        
        for future in as_completed(futures):
            repo = futures[future]
            try:
                if future.result():
                    successful += 1
                    # Update metadata
                    backup_manager.update_repo_info(username, repo['name'], {
                        'cloned_at': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat(),
                        'size': repo['size'],
                        'language': repo.get('language', 'Unknown'),
                        'description': repo.get('description', ''),
                        'clone_url': repo['clone_url']
                    })
                    print(f"   ✅ [{successful}/{len(to_clone)}] {repo['name']} backed up")
                else:
                    failed += 1
                    print(f"   ❌ [{successful}/{len(to_clone)}] Failed: {repo['name']}")
            except Exception as e:
                failed += 1
                print(f"   ❌ Error with {repo['name']}: {e}")
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\n📊 Backup Complete!")
    print(f"   • Time taken: {elapsed:.1f} seconds")
    print(f"   • Successful: {successful} repositories")
    print(f"   • Failed: {failed} repositories")
    print(f"   • Backup location: {user_dir.absolute()}")
    
    # Ask about updating already cloned repos
    if already_cloned:
        update_choice = input(f"\n🔄 Update {len(already_cloned)} existing repositories? (y/n): ").lower()
        if update_choice == 'y':
            update_all_cloned_repos(backup_manager, already_cloned, username, max_workers)

def update_all_cloned_repos(backup_manager, repos, username, max_workers=CLONE_THREADS):
    """Update all cloned repositories"""
    user_dir = backup_manager.get_user_backup_dir(username)
    
    print(f"\n🔄 Updating {len(repos)} repositories...")
    start_time = time.time()
    
    successful = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        for repo in repos:
            repo_path = user_dir / repo['name']
            if repo_path.exists():
                future = executor.submit(update_repo, repo_path, repo['name'])
                futures[future] = repo
        
        for future in as_completed(futures):
            repo = futures[future]
            try:
                if future.result():
                    successful += 1
                    # Update metadata
                    info = backup_manager.get_repo_info(username, repo['name'])
                    info['last_updated'] = datetime.now().isoformat()
                    backup_manager.update_repo_info(username, repo['name'], info)
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"   ❌ Error updating {repo['name']}: {e}")
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\n📊 Update Complete!")
    print(f"   • Time taken: {elapsed:.1f} seconds")
    print(f"   • Updated: {successful} repositories")
    print(f"   • Failed: {failed} repositories")

def sync_backup(api, repos, username, backup_manager):
    """Synchronize backup - update existing and clone new repos"""
    user_dir = backup_manager.get_user_backup_dir(username)
    
    print(f"\n🔄 Synchronizing backup for {username}")
    print(f"📁 Backup directory: {user_dir.absolute()}")
    
    # Analyze current state
    to_clone = []
    to_update = []
    
    for repo in repos:
        if backup_manager.is_repo_cloned(username, repo['name']):
            to_update.append(repo)
        else:
            to_clone.append(repo)
    
    # Check for deleted repos (in backup but not in GitHub)
    backed_up_repos = set()
    if user_dir.exists():
        for repo_dir in user_dir.iterdir():
            if repo_dir.is_dir() and (repo_dir / '.git').exists():
                backed_up_repos.add(repo_dir.name)
    
    current_repos = {repo['name'] for repo in repos}
    deleted_repos = backed_up_repos - current_repos
    
    # Display sync status
    print(f"\n📊 Sync Analysis:")
    print(f"   • New repositories to clone: {len(to_clone)}")
    print(f"   • Existing repositories to update: {len(to_update)}")
    print(f"   • Deleted from GitHub (kept locally): {len(deleted_repos)}")
    
    if deleted_repos:
        print(f"\n⚠️ These repositories exist locally but not on GitHub:")
        for repo_name in deleted_repos:
            print(f"   • {repo_name}")
    
    if not to_clone and not to_update:
        print("\n✅ Everything is already synchronized!")
        return
    
    # Confirm sync
    confirm = input("\nProceed with synchronization? (y/n): ").lower()
    if confirm != 'y':
        print("Sync cancelled.")
        return
    
    # Clone new repositories
    if to_clone:
        print(f"\n📥 Cloning {len(to_clone)} new repositories...")
        backup_all_repos(api, to_clone, username, backup_manager)
    
    # Update existing repositories
    if to_update:
        print(f"\n🔄 Updating {len(to_update)} existing repositories...")
        update_all_cloned_repos(backup_manager, to_update, username)
    
    print(f"\n✅ Synchronization complete!")

def manage_proxies(proxy_manager):
    """Manage proxy settings and configuration"""
    while True:
        print(f"\n🌐 Proxy Management")
        print("=" * 40)
        print(f"Status: {'Enabled' if proxy_manager.enabled else 'Disabled'}")
        print(f"Loaded proxies: {len(proxy_manager.proxies)}")
        
        print("\n1. Enable/Disable proxy rotation")
        print("2. Add proxy")
        print("3. List proxies")
        print("4. Test proxies")
        print("5. Load proxies from file")
        print("6. Clear all proxies")
        print("7. Back to main menu")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            proxy_manager.enabled = not proxy_manager.enabled
            status = "enabled" if proxy_manager.enabled else "disabled"
            print(f"✅ Proxy rotation {status}")
            
        elif choice == '2':
            proxy = input("Enter proxy (format: ip:port or http://ip:port): ").strip()
            if proxy_manager.add_proxy(proxy):
                print(f"✅ Added proxy: {proxy}")
            else:
                print("❌ Invalid proxy format")
                
        elif choice == '3':
            if proxy_manager.proxies:
                print("\n📋 Configured proxies:")
                for i, proxy in enumerate(proxy_manager.proxies, 1):
                    print(f"   {i}. {proxy}")
            else:
                print("No proxies configured")
                
        elif choice == '4':
            if not proxy_manager.proxies:
                print("No proxies to test")
            else:
                print("\n🧪 Testing proxies...")
                working = 0
                for proxy in proxy_manager.proxies:
                    if proxy_manager.test_proxy(proxy):
                        print(f"   ✅ {proxy} - Working")
                        working += 1
                    else:
                        print(f"   ❌ {proxy} - Failed")
                print(f"\nResults: {working}/{len(proxy_manager.proxies)} working")
                
        elif choice == '5':
            file_path = input("Enter proxy file path (default: proxies.txt): ").strip()
            if not file_path:
                file_path = "proxies.txt"
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        new_proxies = [line.strip() for line in f if line.strip()]
                    proxy_manager.proxies.extend(new_proxies)
                    proxy_manager.save_proxies()
                    print(f"✅ Loaded {len(new_proxies)} proxies from {file_path}")
                except Exception as e:
                    print(f"❌ Error loading file: {e}")
            else:
                print(f"❌ File not found: {file_path}")
                
        elif choice == '6':
            confirm = input("Clear all proxies? (y/n): ").lower()
            if confirm == 'y':
                proxy_manager.proxies = []
                proxy_manager.save_proxies()
                proxy_manager.enabled = False
                print("✅ All proxies cleared")
                
        elif choice == '7':
            break
        else:
            print("❌ Invalid choice")

def view_backup_status(backup_manager, username):
    """View detailed backup status and statistics"""
    user_dir = backup_manager.get_user_backup_dir(username)
    
    print(f"\n📊 Backup Status for {username}")
    print("=" * 50)
    print(f"📁 Backup directory: {user_dir.absolute()}")
    
    if not user_dir.exists():
        print("No backups found for this user.")
        return
    
    # Count backed up repositories
    backed_up = []
    total_size = 0
    
    for repo_dir in user_dir.iterdir():
        if repo_dir.is_dir() and (repo_dir / '.git').exists():
            backed_up.append(repo_dir.name)
            # Get directory size
            try:
                size = sum(f.stat().st_size for f in repo_dir.rglob('*') if f.is_file())
                total_size += size
            except:
                pass
    
    print(f"\n📈 Statistics:")
    print(f"   • Total repositories backed up: {len(backed_up)}")
    print(f"   • Total backup size: {format_size(total_size)}")
    
    # Show recent backups
    recent_backups = []
    for repo_name in backed_up:
        info = backup_manager.get_repo_info(username, repo_name)
        if info:
            recent_backups.append((repo_name, info))
    
    # Sort by last updated
    recent_backups.sort(key=lambda x: x[1].get('last_updated', ''), reverse=True)
    
    if recent_backups:
        print(f"\n🕐 Recently updated (top 10):")
        for repo_name, info in recent_backups[:10]:
            updated = info.get('last_updated', 'Unknown')
            if updated != 'Unknown':
                updated = format_date(updated)
            print(f"   • {repo_name}: {updated}")
    
    # Show backup metadata
    metadata_size = backup_manager.metadata_file.stat().st_size if backup_manager.metadata_file.exists() else 0
    print(f"\n📝 Metadata:")
    print(f"   • Tracked repositories: {len(backup_manager.metadata)}")
    print(f"   • Metadata file size: {format_size(metadata_size)}")

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
    """Fetch all repositories with pagination support"""
    all_repos = []
    page = 1
    
    while True:
        url = f"{API_BASE}/users/{username}/repos"
        params = {'sort': sort, 'per_page': per_page, 'page': page}
        
        repos = api.make_request(url, params)
        if not repos:
            break
            
        all_repos.extend(repos)
        
        if len(repos) < per_page:
            break
            
        page += 1
        print(f"   📄 Fetching page {page}...")
    
    return all_repos

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
            print(f"     ⭐ {stars} | 🍴 {forks} | 💻 {language} | 📦 {size} | 🕐 {updated}")
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

def clone_repository(repos):
    """Handle single repository cloning with user selection"""
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
            
            # Clone to current directory
            if clone_repo_with_progress(clone_url, repo_name, repo_name):
                print(f"✅ Repository '{repo_name}' cloned successfully!")
                print(f"📁 Files saved to: {os.path.abspath(repo_name)}")
            else:
                print(f"❌ Failed to clone repository")
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
    """Display the enhanced main menu"""
    print("\n" + "=" * 50)
    print("📋 GitNav Menu v" + VERSION)
    print("=" * 50)
    print("Repository Operations:")
    print("  1.  📋 List repositories")
    print("  2.  📋+ List repositories (detailed)")
    print("  3.  🔍 Search repositories")
    print("  4.  📊 Show repository statistics")
    print("  5.  📥 Clone single repository")
    print("  6.  📖 View README")
    print("  7.  🌐 Open in browser")
    
    print("\nBackup & Sync:")
    print("  8.  💾 Backup ALL repositories")
    print("  9.  🔄 Sync/Update backup")
    print("  10. 📊 View backup status")
    
    print("\nSettings:")
    print("  11. 🌐 Manage proxies")
    print("  12. 👤 Show user profile")
    print("  13. 🔄 Refresh repositories")
    
    print("\n  14. ❌ Exit")
    print("=" * 50)

def menu_loop(api, repos, username, backup_manager, proxy_manager):
    """Enhanced menu loop with backup and proxy features"""
    user_profile = None
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-14): ").strip()
        
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
            open_in_browser(repos)
        elif choice == '8':
            backup_all_repos(api, repos, username, backup_manager)
        elif choice == '9':
            sync_backup(api, repos, username, backup_manager)
        elif choice == '10':
            view_backup_status(backup_manager, username)
        elif choice == '11':
            manage_proxies(proxy_manager)
        elif choice == '12':
            if not user_profile:
                user_profile = fetch_user_profile(api, username)
            display_user_profile(user_profile)
        elif choice == '13':
            print("🔄 Refreshing repositories...")
            new_repos = fetch_repos(api, username)
            if new_repos:
                repos.clear()
                repos.extend(new_repos)
                print(f"✅ Refreshed! Found {len(repos)} repositories.")
            else:
                print("❌ Failed to refresh repositories.")
        elif choice == '14':
            print("👋 Thanks for using GitNav! Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1-14.")

def display_banner():
    """Display the enhanced GitNav ASCII banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██╗████████╗███╗   ██╗ █████╗ ██╗   ██╗    ██╗   ██╗██████╗      ║
║  ██╔════╝ ██║╚══██╔══╝████╗  ██║██╔══██╗██║   ██║    ██║   ██║╚════██╗     ║
║  ██║  ███╗██║   ██║   ██╔██╗ ██║███████║██║   ██║    ██║   ██║ █████╔╝     ║
║  ██║   ██║██║   ██║   ██║╚██╗██║██╔══██║╚██╗ ██╔╝    ╚██╗ ██╔╝ ╚═══██╗     ║
║  ╚██████╔╝██║   ██║   ██║ ╚████║██║  ██║ ╚████╔╝      ╚████╔╝ ██████╔╝     ║
║   ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝        ╚═══╝  ╚═════╝      ║
║                                                                              ║
║               🚀 Enhanced GitHub Repository Navigator & Backup Tool          ║
║                              Version """ + VERSION + """                                   ║
║                                                                              ║
║                        💻 Coded by 0xb0rn3 | 0xbv1 💻                        ║
║                    🌟 Your Gateway to GitHub Excellence 🌟                   ║
║                                                                              ║
║  Features: Full Backup | Sync Updates | Proxy Support | Parallel Cloning    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main function with enhanced features"""
    display_banner()
    
    # Initialize managers
    proxy_manager = ProxyManager()
    backup_manager = BackupManager()
    
    # Check for proxy configuration
    if proxy_manager.proxies:
        use_proxies = input(f"\n🌐 Found {len(proxy_manager.proxies)} proxies. Enable proxy rotation? (y/n): ").lower()
        proxy_manager.enabled = (use_proxies == 'y')
    
    username = input("\nEnter GitHub username: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return
    
    api = GitHubAPI(proxy_manager)
    print(f"🔍 Fetching repositories for '{username}'...")
    
    repos = fetch_repos(api, username)
    if repos:
        print(f"✅ Found {len(repos)} repositories!")
        display_repo_stats(repos)
        menu_loop(api, repos, username, backup_manager, proxy_manager)
    else:
        print("❌ Unable to proceed without repositories.")
        print("   Please check the username and try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1).enabled:
                proxies = self.proxy_manager.get_next_proxy()
                if proxies:
                    print(f"🔄 Using proxy for request #{self.request_count + 1}")
            
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params, 
                proxies=proxies,
                timeout=15
            )
            
            self.request_count += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print("❌ Error: Resource not found")
            elif response.status_code == 403:
                print("❌ Error: API rate limit exceeded")
                if 'X-RateLimit-Reset' in response.headers:
                    reset_time = datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
                    print(f"   Rate limit resets at: {reset_time}")
                    
                    # If using proxies, try rotating to next one
                    if self.proxy_manager and self.proxy_manager.enabled:
                        print("   Rotating to next proxy...")
                        return self.make_request(url, params)  # Retry with next proxy
            else:
                print(f"❌ Error: HTTP {response.status_code}")
            
            return None
            
        except requests.exceptions.Timeout:
            print("❌ Error: Request timed out")
            if self.proxy_manager and self.proxy_manager.enabled:
                print("   Trying next proxy...")
                return self.make_request(url, params)
        except requests.exceptions.ProxyError:
            print("❌ Error: Proxy connection failed")
            if self.proxy_manager and self.proxy_manager
