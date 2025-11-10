"""Use case: пересчитать состояние сделки через доменный пайплайн."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from backend.config.frameworks import available_frameworks, get_frameworks
from backend.domain.entities import DealReadModel
from backend.pipelines.recompute_steps import RecomputeInput, recompute_read_model
from backend.ports.unit_of_work import UnitOfWorkFactory


@dataclass(frozen=True, slots=True)
class RecomputeCommand:
    """Команда на пересчёт доменной read-model сделки."""

    deal_id: str


class RecomputeHandler:
    """Запускает пересчёт и сохраняет обновлённую read-model."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        framework_ids: Sequence[str] | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._framework_ids = tuple(framework_ids) if framework_ids else available_frameworks()

    def execute(self, command: RecomputeCommand) -> DealReadModel:
        """Пересчитать состояние и записать результат атомарно."""

        frameworks = get_frameworks(self._framework_ids)
        with self._uow_factory() as uow:
            facts = list(uow.facts.list_for_deal(command.deal_id))
            current = uow.read_models.get(command.deal_id)
            pipeline_input = RecomputeInput(
                deal_id=command.deal_id,
                facts=facts,
                frameworks=list(frameworks),
            )
            updated = recompute_read_model(pipeline_input)
            if current and updated.last_event is None:
                updated = DealReadModel(
                    deal_id=updated.deal_id,
                    status=updated.status,
                    score=updated.score,
                    last_event=current.last_event,
                    updated_at=updated.updated_at,
                    letters=updated.letters,
                )
            uow.read_models.save(updated)
            uow.commit()
            return updated

