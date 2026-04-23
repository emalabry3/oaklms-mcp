#!/usr/bin/env bash
# install.sh — Installation interactive du plugin OakLMS pour Claude Code
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS="$HOME/.claude/settings.json"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Plugin OakLMS — Installation           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# --- URL OakLMS ---
read -r -p "URL de votre instance OakLMS (défaut : http://localhost:8080) : " OAKLMS_URL
OAKLMS_URL="${OAKLMS_URL:-http://localhost:8080}"
OAKLMS_URL="${OAKLMS_URL%/}"

echo ""
echo "→ URL configurée : $OAKLMS_URL"
echo ""

# --- Vérification Python et mcp ---
if ! python3 -c 'import mcp' 2>/dev/null; then
    echo "Installation des dépendances Python..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet
fi

# --- Mise à jour settings.json ---
python3 - <<PYEOF
import json, os, sys

settings_path = os.path.expanduser("$SETTINGS")
script_dir = "$SCRIPT_DIR"
oaklms_url = "$OAKLMS_URL"

os.makedirs(os.path.dirname(settings_path), exist_ok=True)

if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

settings.setdefault("mcpServers", {})
settings["mcpServers"]["oaklms"] = {
    "command": "python3",
    "args": [os.path.join(script_dir, "server.py")],
    "env": {"OAKLMS_URL": oaklms_url},
}

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"✓ MCP server 'oaklms' ajouté dans {settings_path}")
PYEOF

# --- Installation des skills ---
SKILLS_DIR="$HOME/.claude/commands"
mkdir -p "$SKILLS_DIR"

if [ -d "$SCRIPT_DIR/skills" ]; then
    cp "$SCRIPT_DIR/skills/formation.md" "$SKILLS_DIR/formation.md"
    cp "$SCRIPT_DIR/skills/atelier.md" "$SKILLS_DIR/atelier.md"
    echo "✓ Skills /formation et /atelier installés dans $SKILLS_DIR"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Installation terminée ✓                ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Prochaines étapes :"
echo "  1. Redémarrez Claude Code"
echo "  2. Vérifiez que le MCP 'oaklms' apparaît dans les tools disponibles"
echo "  3. Testez avec /formation ou /atelier"
echo ""
echo "Pour basculer dev/prod : ./oaklms-switch dev|prod"
echo ""
