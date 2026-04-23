# Plugin OakLMS pour Claude Code

MCP Server Python + skills `/formation` et `/atelier` pour OakLMS.

---

## Prérequis

- Python 3.11+
- Claude Code (CLI ou extension VS Code)
- Instance OakLMS accessible (dev : `http://localhost:8080`)

---

## Installation

```bash
git clone https://github.com/emalabry3/oaklms-mcp.git
cd oaklms-mcp
bash install.sh
```

L'installateur :
1. Demande l'URL de votre instance OakLMS
2. Installe les dépendances Python (`mcp`, `httpx`)
3. Configure le MCP server dans `~/.claude/settings.json`
4. Copie les skills dans `~/.claude/commands/`

Redémarrez Claude Code après l'installation.

---

## Utilisation

### Skills disponibles

| Skill | Description |
|-------|-------------|
| `/formation` | Crée une formation complète (séquences + slides) |
| `/atelier` | Génère des TP à partir d'une formation existante |

### Basculer dev / prod

```bash
./oaklms-switch dev         # → http://localhost:8080
./oaklms-switch prod        # → demande l'URL prod
./oaklms-switch prod https://lms.example.com
```

Redémarrez Claude Code après le switch.

---

## MCP Tools disponibles

| Tool | Description |
|------|-------------|
| `list_sequences()` | Liste toutes les séquences |
| `get_sequence(id)` | Détail d'une séquence |
| `create_sequence(titre, description?, niveauTitre?, dry_run?)` | Crée une séquence |
| `add_niveau(sequenceId, titre, dry_run?)` | Ajoute un niveau |
| `save_diaporama(sequenceId, niveauId, slides, ...)` | Sauvegarde les slides |
| `save_contenu(sequenceId, niveauId, contenu, dry_run?)` | Écrit le fichier .md |
| `add_prerequis(sequenceId, niveauId, prerequisId, dry_run?)` | Ajoute un prérequis |
| `list_formations()` | Liste les formations |
| `get_formation(id)` | Détail d'une formation |
| `create_formation(code, titre, client?, description?, niveauIds?, dry_run?)` | Crée une formation |
| `update_formation_etapes(formationId, niveauIds, dry_run?)` | Met à jour les étapes |
| `rollback_last_creation()` | Annule la dernière création |

### dry_run

Tous les tools de création acceptent `dry_run=True` : retourne le payload sans appeler l'API.

### rollback

`rollback_last_creation()` supprime les entités créées lors du dernier appel de création. Borné à la dernière opération.

---

## Tests smoke (validation manuelle)

```
- [ ] MCP server démarre (visible dans Claude Code)
- [ ] list_sequences() retourne les séquences de votre instance
- [ ] create_sequence("Test", dry_run=True) retourne le payload sans créer
- [ ] create_sequence("Test MCP") crée une séquence
- [ ] rollback_last_creation() supprime la séquence créée
- [ ] list_formations() retourne les formations
- [ ] /formation fonctionne sans demander l'URL
- [ ] /atelier fonctionne sans demander l'URL
```

---

## Structure du repo

```
oaklms-mcp/
├── server.py          ← MCP server (12 tools)
├── session_store.py   ← Store IDs session (rollback)
├── config.py          ← Base URL depuis OAKLMS_URL
├── requirements.txt
├── install.sh         ← Installateur interactif
├── oaklms-switch      ← Bascule dev/prod
├── .env.example
└── skills/
    ├── formation.md   ← Skill /formation (MCP-aware)
    └── atelier.md     ← Skill /atelier (MCP-aware)
```

---

## Versions

- **v1 (ce repo)** : no-auth, usage dev local
- **v2 (à venir)** : auth API key `X-Api-Key` (#106)
