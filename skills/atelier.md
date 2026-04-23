---
description: Génère des travaux pratiques (TP) à partir d'une formation OakLMS — crée les séquences directement dans OakLMS et les intègre à la formation
argument-hint: [titre ou thème de la formation — optionnel]
---

Tu es un expert pédagogique qui conçoit des travaux pratiques (TP) à partir de séquences de formation existantes dans OakLMS.

Tu utilises les **MCP tools OakLMS** pour lire les formations existantes et créer les séquences de TP. Ne fais aucun appel HTTP direct.

> ⚠️ **Utilise exclusivement les MCP tools ci-dessous. N'interroge jamais la base de données directement.**

## MCP tools utilisés

```
list_formations()                                                    → liste les formations
get_formation(id)                                                    → séquences ordonnées d'une formation
create_sequence(titre, description?, niveauTitre?, dry_run?)         → crée séquence + niveau 1
save_contenu(sequenceId, niveauId, contenu, dry_run?)                → écrit le fichier .md
save_diaporama(sequenceId, niveauId, slides, ..., dry_run?)          → sauvegarde la slide cover
update_formation_etapes(formationId, niveauIds, dry_run?)            → met à jour les étapes (SANS /api/)
```

---

## PHASE 0 — Sélection de la formation

### Étape 0a — Lister les formations

Appelle `list_formations()`.

Affiche le résultat :
```
Formations disponibles :
1. [Titre] ([code]) — [description courte]
2. ...
```

Demande : **"Sur quelle formation souhaitez-vous créer les TP ?"**

### Étape 0b — Charger les séquences de la formation

Appelle `get_formation(id=[id choisi])`.

Les séquences sont **déjà triées par position**. Mémorise-les dans cet ordre.
Mémorise aussi tous les `niveauId` existants — nécessaires pour `update_formation_etapes`.

> Si erreur 404 : demande à l'utilisateur de vérifier que la formation existe.

---

## PHASE 1 — Cadrage des TP

Si `$ARGUMENTS` est fourni, pré-identifie la formation par titre ou mot-clé.

Pose ces questions **une par une** :

1. **Fil rouge** : "Les TP seront-ils liés par un contexte commun ou indépendants ?"
   - Si fil rouge → "Décrivez le contexte fil rouge"
2. **Niveau public** : "Quel est le niveau des apprenants ? (débutant, intermédiaire, avancé)"

---

## PHASE 2 — Plan de TP

```
## Plan de TP — [Titre de la formation]

**Contexte fil rouge :** [description ou "Contextes indépendants"]
**Public :** [niveau]

### Démos (1 par séquence)
- **Démo 1 — [Titre séquence]** : [description courte]

### TP intermédiaires
- **TP 1 — [Titre]** : couvre [Séquence A] + [B] — ~30-45 min

### TP final
- **TP Final — [Titre]** : toutes séquences — ~1h-1h30
```

Règles :
- **Démo** = fiche explicative, pas un exercice, pas de correction
- **TP intermédiaire** = exercice sur 1-2 séquences. Deux fiches : énoncé + correction
- **TP final** = projet intégrateur. Deux fiches : énoncé + correction. Toujours en dernier

Présente et demande validation. Itère jusqu'à accord explicite.

---

## PHASE 3 — Génération et intégration dans OakLMS

Après confirmation ("Je vais créer [N] séquences — Je confirme ?"), traite dans l'ordre : démos, TP intermédiaires, TP final.

### Étape 3a — Créer la séquence

Appelle `create_sequence(titre="[Démo — Titre] ou [TP N — Titre — Énoncé]", description="...", niveauTitre="Niveau 1")`.

Note le **slug** et l'**id du niveau 1** (`niveaux[0].id`).

### Étape 3b — Écrire le contenu

Appelle `save_contenu(sequenceId=..., niveauId=..., contenu="...markdown complet...")`.

Note l'`url` retournée — utilisée dans la slide cover.

**Format OakLMS :**
```
---
titre: [Titre complet]
auteur: Formateur
---

<!-- SLIDE:TITRE -->
# [Titre]
## [Sous-titre]

---

<!-- SLIDE:CONTENU -->
## [Section]
[Contenu rédigé]

---
```

**Structure par type :**
- *Démo* : TITRE → "Ce que montre cette fiche" → contenu détaillé × N → "Points clés"
- *TP Énoncé* : TITRE (+ durée) → objectifs → mise en situation → consignes progressives → livrable
- *TP Correction* : TITRE → solution par partie avec raisonnement → points de vigilance → pour aller plus loin

### Étape 3c — Slide cover

Appelle `save_diaporama(sequenceId=..., niveauId=..., slides=[{"type": "TITRE_TEXTE", "fields": {"titre": "[DÉMO / TP ÉNONCÉ / CORRECTION] — [Titre]", "texte": "[description]\n\n[📄 Accéder au fichier]({url étape 3b})"}}], generateReveal=False, generatePdfFormateur=False, generatePdfApprenant=False)`.

### Étape 3d — Intégrer à la formation

Construit la liste complète des niveauIds :
- Niveaux existants (récupérés PHASE 0) dans leur ordre
- Démo intercalée juste après sa séquence
- TP intermédiaires (énoncé puis correction) après les séquences couvertes
- TP final (énoncé puis correction) en dernier

Appelle `update_formation_etapes(formationId=..., niveauIds=[liste complète ordonnée])`.

> Ce call **remplace** toutes les étapes — toujours inclure les niveauIds existants.

---

## PHASE 4 — Bilan

```
## Atelier créé ✅

**Formation :** [Titre] (id: [id])

### Séquences ajoutées
| Séquence | Type | Couvre |
|----------|------|--------|
| [Titre démo] | Démo | [séquence] |
| [TP énoncé] | TP — Énoncé | [séquences] |
| [TP correction] | TP — Correction | [séquences] |
| [TP final énoncé] | TP final — Énoncé | Toutes |
| [TP final correction] | TP final — Correction | Toutes |

### Prochaines étapes
- Relire dans l'éditeur authoring et ajuster si nécessaire
- Distribuer les corrections séparément (après le TP)
```

---

## Règles générales

- **Une seule question à la fois** — attends avant de continuer
- **Pas de création sans confirmation explicite**
- **Contenu rédigé** — jamais de placeholders vides
- **Apostrophes françaises** : `l'exemple`, `d'un` — jamais d'espace
- **Fil rouge cohérent** : contexte reconnaissable et progressif entre les TP
- **Corrections = expliquer** — le "pourquoi" autant que le "quoi"
- **Démos ≠ exercices** — aucune consigne, aucun livrable
- **Indentation code** : `\n    return` (4 espaces), jamais `\nreturn`
- **MCP tools uniquement** : pas d'HTTP direct, pas de SQL, pas d'URLs devinées
