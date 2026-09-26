#!/data/data/com.termux/files/usr/bin/bash

set -e

REPO="https://github.com/sew199/sheron-ai.git"
INSTALL_DIR="$HOME/sheron-ai"

echo "========================================"
echo "        🧠 SHERON AI INSTALLER"
echo "========================================"
echo

echo "[1/5] Updating Termux packages..."
pkg update -y

echo
echo "[2/5] Installing required packages..."
pkg install -y git python

echo
echo "[3/5] Downloading Sheron AI..."

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Sheron AI already exists. Updating..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo
echo "[4/5] Checking Python files..."

python -m py_compile chatbot.py
python -m py_compile calculator.py
python -m py_compile core/brain.py
python -m py_compile core/memory.py
python -m py_compile core/knowledge.py
python -m py_compile core/router.py

echo "Python checks passed ✓"

echo
echo "[5/5] Creating 'sheron' command..."

cat > "$PREFIX/bin/sheron" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
cd "$INSTALL_DIR"
exec python chatbot.py "\$@"
EOF

chmod +x "$PREFIX/bin/sheron"

echo
echo "========================================"
echo "     ✅ SHERON AI INSTALLED!"
echo "========================================"
echo
echo "You can now start Sheron AI with:"
echo
echo "    sheron"
echo

echo "Starting Sheron AI..."
echo

exec "$PREFIX/bin/sheron"
