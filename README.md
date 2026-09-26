<div align="center">🧠 SHERON AI

Your Personal AI Assistant

A modular personal AI assistant built with Python, memory, local knowledge, smart routing, calculations, and an extensible architecture.

<br><a href="https://github.com/sew199/sheron-ai">
<img src="https://img.shields.io/badge/GitHub-SHERON_AI-181717?style=for-the-badge&logo=github" alt="GitHub">
</a><img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"><img src="https://img.shields.io/badge/Platform-Termux-000000?style=for-the-badge&logo=android" alt="Termux"></div>---

⚡ Quick Install

Install Sheron AI on Termux with one command:

curl -fsSL https://raw.githubusercontent.com/sew199/sheron-ai/main/install.sh | bash

After installation:

sheron

That's it. 🧠

---

⚡ Quick Install

Install Sheron AI on Termux with one command:

curl -fsSL https://raw.githubusercontent.com/sew199/sheron-ai/main/install.sh | bash

The installer automatically:

- 📦 Installs required packages
- 🐍 Installs Python
- 📥 Downloads Sheron AI
- 🔍 Checks the Python files
- ⚙️ Creates the "sheron" command
- 🚀 Starts Sheron AI automatically

▶️ Start Sheron AI

After installation, simply type:

sheron

«Note: Sheron AI is installed inside "~/sheron-ai/".
You do not need to run "python chatbot.py" from your home directory.»

📁 Run Manually

If you want to run the project manually:

cd ~/sheron-ai
python chatbot.py

❌ Common Mistake

Don't run:

python chatbot.py

directly from:

~

because "chatbot.py" is inside:

~/sheron-ai/

Use:

sheron

instead. 🧠


🧠 What is Sheron AI?

Sheron AI is a personal AI assistant project designed to combine:

- 🧠 Intelligent response handling
- 💾 Persistent memory
- 📚 Local knowledge
- 🧭 Smart topic routing
- 🧮 Mathematical calculations
- 🛠️ Modular tools
- 🚀 Future AI and API integrations

The architecture is designed to grow over time rather than being a single fixed program.

---

✨ Features

Feature| Description
🧠 AI Brain| Central response and processing system
💾 Memory| Stores profile, preferences, facts and history
📚 Knowledge| Local topic-based knowledge system
🧭 Smart Router| Detects the topic of user questions
🧮 Calculator| Safe mathematical expression calculator
📱 Termux| Designed for Android through Termux
⚡ Installer| One-command installation
🔧 Modular| Easy to expand with new systems

---

🖥️ Interface

Sheron AI includes a terminal interface with:

╔══════════════════════════════════════╗
║                                      ║
║          🧠  SHERON AI               ║
║                                      ║
║      Your Personal AI Assistant      ║
║                                      ║
╚══════════════════════════════════════╝

Commands

/help       Show available commands
/memory     Show saved memory
/clear      Clear conversation history
/exit       Exit Sheron AI

---

🏗️ Architecture

                         🧠 SHERON AI
                              │
              ┌───────────────┼───────────────┐
              │               │               │
           🧠 BRAIN        💾 MEMORY       📚 KNOWLEDGE
              │               │               │
        ┌─────┼─────┐     ┌───┼───┐      ┌────┼────┐
        │     │     │     │   │   │      │    │    │
    Router  Calc  Logic  Profile Facts History Topics
                                      │
                                      ▼
                              🚀 Future Systems
                                      │
                       ┌──────────────┼──────────────┐
                       │              │              │
                    🌐 Web          🎬 Movies      🌦️ Weather
                       │
                  💱 Currency
                       │
                    📰 News

---

📂 Project Structure

sheron-ai/
│
├── api/
│   └── __init__.py
│
├── core/
│   ├── __init__.py
│   ├── brain.py
│   ├── knowledge.py
│   ├── memory.py
│   └── router.py
│
├── knowledge/
│   ├── __init__.py
│   ├── coding.txt
│   ├── cybersecurity.txt
│   ├── english.txt
│   ├── forex.txt
│   └── networking.txt
│
├── memory/
│   └── __init__.py
│
├── tools/
│   ├── __init__.py
│   └── termux.py
│
├── calculator.py
├── chatbot.py
├── chatbot_before_advanced.py
├── chatbot_v3_backup.py
├── welcome.py
├── install.sh
├── .gitignore
└── README.md

---

🛠️ Built With

<div align="center"><img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"><img src="https://img.shields.io/badge/Termux-000000?style=flat-square&logo=android"><img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white"><img src="https://img.shields.io/badge/JSON-000000?style=flat-square&logo=json&logoColor=white"><img src="https://img.shields.io/badge/Bash-4EAA25?style=flat-square&logo=gnu-bash&logoColor=white"></div>---

🗺️ Roadmap

✅ Completed

- [x] Python core
- [x] Memory system
- [x] Local knowledge system
- [x] Smart topic routing
- [x] Calculator
- [x] Termux support
- [x] GitHub repository
- [x] One-command installer
- [x] "sheron" launcher

🔮 Planned

- [ ] Advanced AI model
- [ ] Web search
- [ ] Weather API
- [ ] Movie API
- [ ] News API
- [ ] Currency API
- [ ] Database system
- [ ] Advanced memory
- [ ] External AI APIs
- [ ] Computer & hardware knowledge
- [ ] Networking knowledge
- [ ] Cybersecurity knowledge
- [ ] Cloud tools

---

👨‍💻 Creator

<div align="center">Sheron Elijah

🇱🇰 Sri Lanka

Creator & Developer of SHERON AI

Development assistance provided by ChatGPT.

</div>---

📜 Copyright

<div align="center">© 2026 Sheron Elijah

All Rights Reserved.

SHERON AI

Created by Sheron Elijah
With development assistance from ChatGPT

</div>---

⭐ Support

If you like the project, consider giving the repository a ⭐.

<div align="center">🧠 SHERON AI

Build. Learn. Create. 🚀

</div>
