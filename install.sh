#!/data/data/com.termux/files/usr/bin/bash

echo "================================"
echo "        SHERON AI INSTALLER"
echo "================================"

echo
echo "[1/3] Checking Python..."

if ! command -v python >/dev/null 2>&1; then
    echo "Python not found."
    echo "Installing Python..."
    pkg install python -y
else
    echo "Python found ✓"
fi

echo
echo "[2/3] Checking project files..."

if [ ! -f "chatbot.py" ]; then
    echo "Error: chatbot.py not found."
    exit 1
fi

echo "Project files found ✓"

echo
echo "[3/3] Checking Python files..."

python -m py_compile chatbot.py

if [ $? -ne 0 ]; then
    echo "Python check failed."
    exit 1
fi

echo "Python check passed ✓"

echo
echo "================================"
echo "     SHERON AI READY! 🧠"
echo "================================"

echo
echo "Run Sheron AI with:"
echo
echo "    python chatbot.py"
echo
