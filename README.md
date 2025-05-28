# 🚀 GitNav v0.0.2

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██╗████████╗███╗   ██╗ █████╗ ██╗   ██╗    ██╗   ██╗ ██████╗      ║
║  ██╔════╝ ██║╚══██╔══╝████╗  ██║██╔══██╗██║   ██║    ██║   ██║██╔═████╗     ║
║  ██║  ███╗██║   ██║   ██╔██╗ ██║███████║██║   ██║    ██║   ██║██║██╔██║     ║
║  ██║   ██║██║   ██║   ██║╚██╗██║██╔══██║╚██╗ ██╔╝    ╚██╗ ██╔╝████╔╝██║     ║
║  ╚██████╔╝██║   ██║   ██║ ╚████║██║  ██║ ╚████╔╝      ╚████╔╝ ╚██████╔╝     ║
║   ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝        ╚═══╝   ╚═════╝      ║
║                                                                              ║
║                    🚀 Enhanced GitHub Repository Navigator                   ║
║                              Version 0.0.2                                   ║
║                                                                              ║
║                        💻 Coded by 0xb0rn3 | 0xbv1 💻                        ║
║                    🌟 Your Gateway to GitHub Excellence 🌟                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**The Ultimate Command-Line Tool for GitHub Repository Management**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/badge/Issues-Welcome-red.svg)](https://github.com/0xb0rn3/gitnav/issues)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## 🌟 Overview

GitNav is a powerful, feature-rich command-line interface that transforms how you interact with GitHub repositories. Built by **0xb0rn3 | 0xbv1**, this tool provides an intuitive, menu-driven experience for exploring, managing, and analyzing GitHub repositories without ever leaving your terminal.

Whether you're a developer, researcher, or GitHub enthusiast, GitNav streamlines your workflow by offering comprehensive repository insights, seamless cloning capabilities, and advanced search functionality all in one elegant package.

---

## ✨ Key Features

### 🎯 **Repository Management**
- **Smart Listing**: View repositories with detailed metadata including stars, forks, languages, and file sizes
- **Advanced Search**: Multi-field search across repository names, descriptions, and programming languages
- **One-Click Cloning**: Effortless repository cloning with intelligent error handling and progress feedback
- **Statistics Dashboard**: Comprehensive analytics showing aggregate repository data and language distributions

### 📊 **Project Insights**
- **Issue Tracking**: Browse open, closed, or all issues with detailed metadata and label information
- **Release Management**: Explore repository releases and download assets with size and popularity metrics
- **README Viewer**: Read repository documentation directly in your terminal with proper formatting
- **User Profiles**: Access detailed developer profiles including bio, location, and contribution statistics

### 🔧 **Developer Experience**
- **Intuitive Interface**: Clean, emoji-enhanced menus with numbered options for quick navigation
- **Robust Error Handling**: Comprehensive error messages with actionable suggestions and recovery options
- **Real-time Updates**: Refresh repository data without restarting the application
- **Browser Integration**: Seamlessly open repositories in your default web browser

### 🚀 **Performance & Reliability**
- **Smart Caching**: Efficient API usage with intelligent request management
- **Timeout Protection**: Network timeout handling prevents application freezing
- **Rate Limit Awareness**: GitHub API rate limit monitoring with reset time notifications
- **Streaming Downloads**: Memory-efficient file downloads for large assets

---

## 🛠️ Installation & Setup

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.7 or higher**: GitNav leverages modern Python features for optimal performance
- **Git**: Required for repository cloning functionality
- **Internet Connection**: Needed for GitHub API interactions

### Quick Installation

```bash
# Clone the GitNav repository
git clone https://github.com/0xb0rn3/gitnav.git

# Navigate to the project directory
cd gitnav

# Install required dependencies
pip install requests

# Make GitNav executable (Unix/Linux/macOS)
chmod +x gitnav.py

# Run GitNav
python gitnav.py
```

### Alternative Installation Methods

**Using pip (if published to PyPI):**
```bash
pip install gitnav
gitnav
```

**Direct download:**
```bash
wget https://raw.githubusercontent.com/0xb0rn3/gitnav/main/gitnav.py
python gitnav.py
```

---

## 🎮 Usage Guide

### Getting Started

Launch GitNav by running the Python script. You'll be greeted with the beautiful ASCII banner and prompted to enter a GitHub username:

```bash
python gitnav.py
```

### Main Menu Options

GitNav presents a comprehensive menu system with the following options:

#### **Repository Operations**
1. **📋 List Repositories**: Quick overview of all repositories
2. **📋+ Detailed Listing**: Comprehensive repository information including sizes and update times
3. **🔍 Search Repositories**: Multi-field search functionality
4. **📊 Repository Statistics**: Aggregate analytics and insights

#### **Content Access**
5. **📥 Clone Repository**: Download repositories locally with progress tracking
6. **📖 View README**: Read documentation directly in terminal
7. **🐛 View Issues**: Browse repository issues with filtering options
8. **📦 Download Assets**: Access release files and binaries

#### **Navigation & Tools**
9. **🌐 Open in Browser**: Launch repositories in your web browser
10. **👤 User Profile**: View detailed developer information
11. **🔄 Refresh Data**: Update repository information
12. **❌ Exit**: Clean application termination

### Example Workflow

