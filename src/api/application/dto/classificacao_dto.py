"""DTO para Classificação."""

from dataclasses import dataclass
from typing import Optional

from src.api.domain.entities.classificacao import Classificacao


@dataclass
class ClassificacaoDTO:
    """Data Transfer Object para classificação."""

    posicao: int
    time: str
    time_reduzido: str
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gp: int
    gc: int
    sg: int
    pontos: int
    aproveitamento: float
    status: str
    temporada: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: Classificacao) -> "ClassificacaoDTO":
        """Cria um DTO a partir de uma entidade."""
        return cls(
            posicao=entity.posicao,
            time=entity.time.nome,
            time_reduzido=entity.time.nome_reduzido or entity.time.nome,
            jogos=entity.jogos,
            vitorias=entity.vitorias,
            empates=entity.empates,
            derrotas=entity.derrotas,
            gp=entity.gp,
            gc=entity.gc,
            sg=entity.sg,
            pontos=entity.pontos,
            aproveitamento=entity.aproveitamento,
            status=entity.status,
            temporada=entity.temporada,
        )

    def to_dict(self) -> dict:
        """Converte o DTO para dicionário."""
        return {
            "posicao": self.posicao,
            "time": self.time,
            "time_reduzido": self.time_reduzido,
            "jogos": self.jogos,
            "vitorias": self.vitorias,
            "empates": self.empates,
            "derrotas": self.derrotas,
            "gp": self.gp,
            "gc": self.gc,
            "sg": self.sg,
            "pontos": self.pontos,
            "aproveitamento": self.aproveitamento,
            "status": self.status,
            "temporada": self.temporada,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClassificacaoDTO":
        """Cria um DTO a partir de um dicionário."""
        return cls(
            posicao=data.get("posicao", data.get("Posição", 0)),
            time=data.get("time", data.get("Time", "")),
            time_reduzido=data.get("time_reduzido", data.get("Time", "")),
            jogos=data.get("jogos", data.get("J", 0)),
            vitorias=data.get("vitorias", data.get("V", 0)),
            empates=data.get("empates", data.get("E", 0)),
            derrotas=data.get("derrotas", data.get("D", 0)),
            gp=data.get("gp", data.get("GP", 0)),
            gc=data.get("gc", data.get("GC", 0)),
            sg=data.get("sg", data.get("SG", 0)),
            pontos=data.get("pontos", data.get("PTS", 0)),
            aproveitamento=data.get("aproveitamento", 0.0),
            status=data.get("status", "SEM_REBAIXAMENTO"),
            temporada=data.get("temporada"),
        )
