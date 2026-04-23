"""Store de session en mémoire — IDs créés disponibles pour rollback."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CreationRecord:
    """Enregistrement d'une opération de création."""
    sequences: list = field(default_factory=list)   # [sequenceId, ...]
    niveaux: list = field(default_factory=list)     # [(sequenceId, niveauId), ...]
    formations: list = field(default_factory=list)  # [formationId, ...]


class SessionStore:
    """Store en mémoire pour les IDs créés dans la session courante."""

    def __init__(self):
        self._last: Optional[CreationRecord] = None
        self._current: Optional[CreationRecord] = None

    def begin_operation(self):
        self._current = CreationRecord()

    def record_sequence(self, sequence_id: int):
        if self._current:
            self._current.sequences.append(sequence_id)

    def record_niveau(self, sequence_id: int, niveau_id: int):
        if self._current:
            self._current.niveaux.append((sequence_id, niveau_id))

    def record_formation(self, formation_id: int):
        if self._current:
            self._current.formations.append(formation_id)

    def commit_operation(self):
        """Finalise l'opération — devient la dernière pour rollback."""
        if self._current:
            self._last = self._current
            self._current = None

    def get_last(self) -> Optional[CreationRecord]:
        return self._last

    def clear_last(self):
        self._last = None


# Instance singleton partagée par tous les tools
store = SessionStore()
