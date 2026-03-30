"""DTO para Classificação com Vagas.

Este DTO contém campos de classificação mais informações de vagas/zonas.
Usado pelo pipeline carga_classificacao_vagas.py.

Campos adicionais:
    - zona: Zona completa (ex: "LIBERTADORES (G4)")
    - status_curto: Status curto (ex: "LIB", "SUL-AM")
"""

from dataclasses import dataclass
from typing import Optional

from src.api.domain.entities.classificacao import Classificacao


@dataclass
class ClassificacaoVagasDTO:
    """Data Transfer Object para classificação com vagas."""
    
    posicao: int
    time: str
    time_reduzido: str
    jogos: int
    vitorias: int
    empates: int
    defeats: int
    gp: int
    gc: int
    sg: int
    pontos: int
    aproveitamento: float
    zona: str
    status_curto: str
    temporada: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: Classificacao) -> "ClassificacaoVagasDTO":
        """Cria um DTO a partir de uma entidade."""
        return cls(
            posicao=entity.posicao,
            time=entity.time.nome,
            time_reduzido=entity.time.nome_reduzido or entity.time.nome,
            jogos=entity.jogos,
            vitorias=entity.vitorias,
            empates=entity.empates,
            defeats=entity.derrotas,
            gp=entity.gp,
            gc=entity.gc,
            sg=entity.sg,
            pontos=entity.pontos,
            aproveitamento=entity.aproveitamento,
            zona=entity.zona_computada or entity.zona or "",
            status_curto=entity.status_curto or "",
            temporada=entity.temporada
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
            "zona": self.zona,
            "status_curto": self.status_curto,
            "temporada": self.temporada
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ClassificacaoVagasDTO":
        """Cria um DTO a partir de um dicionário."""
        return cls(
            posicao=data.get("posicao", data.get("Posição", 0)),
            time=data.get("time", data.get("Time", "")),
            time_reduzido=data.get("time_reduzido", data.get("Time", "")),
            jogos=data.get("jogos", data.get("J", 0)),
            vitorias=data.get("vitorias", data.get("V", 0)),
            empates=data.get("empates", data.get("E", 0)),
            defeats=data.get("derrotas", data.get("D", 0)),
            gp=data.get("gp", data.get("GP", 0)),
            gc=data.get("gc", data.get("GC", 0)),
            sg=data.get("sg", data.get("SG", 0)),
            pontos=data.get("pontos", data.get("PTS", 0)),
            aproveitamento=data.get("aproveitamento", 0.0),
            zona=data.get("zona", ""),
            status_curto=data.get("status_curto", ""),
            temporada=data.get("temporada")
        )
