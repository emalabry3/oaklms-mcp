"""OakLMS MCP Server — wraps the OakLMS REST API for Claude Code."""
import httpx
from mcp.server.fastmcp import FastMCP
from config import get_base_url
from session_store import store

mcp = FastMCP(
    "oaklms",
    instructions="OakLMS — séquences, niveaux, diaporamas, formations. Toutes les créations supportent dry_run=True.",
)


# ---------------------------------------------------------------------------
# Séquences
# ---------------------------------------------------------------------------

@mcp.tool()
def list_sequences() -> list:
    """Liste toutes les séquences avec leurs niveaux et slides."""
    r = httpx.get(f"{get_base_url()}/api/sequences", timeout=30)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def get_sequence(id: int) -> dict:
    """Détail d'une séquence (niveaux, slides)."""
    r = httpx.get(f"{get_base_url()}/api/sequences/{id}", timeout=30)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def create_sequence(
    titre: str,
    description: str = "",
    niveauTitre: str = "Niveau 1",
    dry_run: bool = False,
) -> dict:
    """Crée une séquence avec un premier niveau. dry_run=True retourne le payload sans appeler l'API."""
    payload = {"titre": titre, "description": description, "niveauTitre": niveauTitre}
    if dry_run:
        return {"dry_run": True, "payload": payload}
    store.begin_operation()
    r = httpx.post(f"{get_base_url()}/api/sequences", json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    store.record_sequence(data["id"])
    for n in data.get("niveaux", []):
        store.record_niveau(data["id"], n["id"])
    store.commit_operation()
    return data


@mcp.tool()
def add_niveau(
    sequenceId: int,
    titre: str,
    dry_run: bool = False,
) -> dict:
    """Ajoute un niveau à une séquence existante."""
    payload = {"titre": titre}
    if dry_run:
        return {"dry_run": True, "sequenceId": sequenceId, "payload": payload}
    store.begin_operation()
    r = httpx.post(f"{get_base_url()}/api/sequences/{sequenceId}/niveaux", json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    store.record_niveau(sequenceId, data["id"])
    store.commit_operation()
    return data


@mcp.tool()
def save_diaporama(
    sequenceId: int,
    niveauId: int,
    slides: list,
    generateReveal: bool = True,
    generatePdfFormateur: bool = True,
    generatePdfApprenant: bool = False,
    dry_run: bool = False,
) -> dict:
    """Sauvegarde les slides d'un niveau et génère Reveal.js/PDF. slides=[{type, fields}]. Timeout 120s."""
    payload = {
        "slides": slides,
        "generateReveal": generateReveal,
        "generatePdfFormateur": generatePdfFormateur,
        "generatePdfApprenant": generatePdfApprenant,
    }
    if dry_run:
        return {"dry_run": True, "sequenceId": sequenceId, "niveauId": niveauId, "payload": payload}
    r = httpx.post(
        f"{get_base_url()}/api/sequences/{sequenceId}/niveaux/{niveauId}/diaporama",
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


@mcp.tool()
def save_contenu(
    sequenceId: int,
    niveauId: int,
    contenu: str,
    dry_run: bool = False,
) -> dict:
    """Écrit le fichier Markdown de contenu d'un niveau. Retourne {path, url}."""
    payload = {"contenu": contenu}
    if dry_run:
        return {"dry_run": True, "sequenceId": sequenceId, "niveauId": niveauId, "payload": payload}
    r = httpx.post(
        f"{get_base_url()}/api/sequences/{sequenceId}/niveaux/{niveauId}/contenu",
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


@mcp.tool()
def add_prerequis(
    sequenceId: int,
    niveauId: int,
    prerequisId: int,
    dry_run: bool = False,
) -> dict:
    """Ajoute un prérequis à un niveau (endpoint retourne 302 — succès si 200/302/303)."""
    if dry_run:
        return {"dry_run": True, "sequenceId": sequenceId, "niveauId": niveauId, "prerequisId": prerequisId}
    r = httpx.post(
        f"{get_base_url()}/sequences/{sequenceId}/niveaux/{niveauId}/prerequis",
        params={"prerequisId": prerequisId},
        follow_redirects=False,
        timeout=30,
    )
    if r.status_code in (200, 302, 303):
        return {"success": True, "status": r.status_code}
    r.raise_for_status()
    return {"success": True, "status": r.status_code}


# ---------------------------------------------------------------------------
# Formations
# ---------------------------------------------------------------------------

@mcp.tool()
def list_formations() -> list:
    """Liste toutes les formations OakLMS."""
    r = httpx.get(f"{get_base_url()}/api/formations", timeout=30)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def get_formation(id: int) -> dict:
    """Détail d'une formation avec ses séquences/niveaux ordonnés."""
    r = httpx.get(f"{get_base_url()}/api/formations/{id}", timeout=30)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def create_formation(
    code: str,
    titre: str,
    client: str = "",
    description: str = "",
    niveauIds: list = None,
    dry_run: bool = False,
) -> dict:
    """Crée une formation et y attache des niveaux (ordre = ordre de niveauIds)."""
    payload = {
        "code": code,
        "titre": titre,
        "client": client,
        "description": description,
        "niveauIds": niveauIds or [],
    }
    if dry_run:
        return {"dry_run": True, "payload": payload}
    store.begin_operation()
    r = httpx.post(f"{get_base_url()}/api/formations", json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    store.record_formation(data["id"])
    store.commit_operation()
    return data


@mcp.tool()
def update_formation_etapes(
    formationId: int,
    niveauIds: list,
    dry_run: bool = False,
) -> dict:
    """Remplace toutes les étapes d'une formation. niveauIds = liste ordonnée complète (existants + nouveaux)."""
    payload = {"niveauIds": niveauIds}
    if dry_run:
        return {"dry_run": True, "formationId": formationId, "payload": payload}
    r = httpx.post(
        f"{get_base_url()}/formations/{formationId}/etapes",
        json=payload,
        follow_redirects=False,
        timeout=30,
    )
    if r.status_code in (200, 302, 303):
        return {"success": True, "status": r.status_code, "formationId": formationId}
    r.raise_for_status()
    return {"success": True}


@mcp.tool()
def rollback_last_creation() -> dict:
    """Supprime les entités créées lors de la dernière opération (séquences, formations). Borné à la dernière op."""
    last = store.get_last()
    if not last:
        return {"message": "Aucune opération de création à annuler."}

    base = get_base_url()
    deleted = {"sequences": [], "formations": []}
    errors = []

    for formation_id in last.formations:
        try:
            r = httpx.delete(f"{base}/api/formations/{formation_id}", timeout=30)
            if r.status_code in (200, 204):
                deleted["formations"].append(formation_id)
            else:
                errors.append(f"Formation {formation_id} : HTTP {r.status_code}")
        except Exception as e:
            errors.append(f"Formation {formation_id} : {e}")

    for sequence_id in last.sequences:
        try:
            r = httpx.delete(f"{base}/api/sequences/{sequence_id}", timeout=30)
            if r.status_code in (200, 204):
                deleted["sequences"].append(sequence_id)
            else:
                errors.append(f"Séquence {sequence_id} : HTTP {r.status_code}")
        except Exception as e:
            errors.append(f"Séquence {sequence_id} : {e}")

    store.clear_last()
    msg = "Rollback terminé." if not errors else "Rollback partiel — voir errors."
    return {"deleted": deleted, "errors": errors, "message": msg}


# ---------------------------------------------------------------------------
# Entrée
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
