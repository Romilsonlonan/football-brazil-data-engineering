"""Entidade para gerenciar vagas nas competições."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, TYPE_CHECKING

from ..value_objects.posicao import TipoVaga

if TYPE_CHECKING:
    from .classificacao import Classificacao


@dataclass
class VagasConfig:
    """Configuração de vagas para Libertadores e Sul-Americana."""
    
    temporada: str
    vagas_libertadores_grupo: int = 4           # 1º-4º
    vagas_libertadores_pre: int = 1               # 5º
    vagas_sul_americana: int = 6                  # 6º-11º
    rebaixados: int = 4                           # 17º-20º
    
    # Times que já garantiram vaga por serem campeões
    campeao_libertadores: Optional[str] = None
    campeao_sul_americana: Optional[str] = None
    campeao_copa_brasil: Optional[str] = None
    
    # Cache calculado
    _vagas_por_campeao: Dict[str, int] = field(default_factory=dict, init=False)
    
    def __post_init__(self):
        """Calcula as vagas após inicialização."""
        self._calcular_vagas_por_campeao()
    
    def _calcular_vagas_por_campeao(self):
        """Calcula quantas vagas "descendem" por cada campeão."""
        self._vagas_por_campeao = {
            "libertadores": 0,
            "sul_americana": 0,
            "copa_brasil": 0
        }
        
        # Se o campeão da Libertadores já está no G4, a vaga desce
        if self.campeao_libertadores:
            self._vagas_por_campeao["libertadores"] = 1
        
        # Se o campeão da Sul-Americana já está classificado, a vaga desce
        if self.campeao_sul_americana:
            self._vagas_por_campeao["sul_americana"] = 1
        
        # Se o campeão da Copa do Brasil está no G5, vai para fase de grupos
        # e a vaga do G5 "desce" para G6
        if self.campeao_copa_brasil:
            self._vagas_por_campeao["copa_brasil"] = 1
    
    @property
    def total_vagas_libertadores(self) -> int:
        """Total de vagas na Libertadores (grupo + pré)."""
        base = self.vagas_libertadores_grupo + self.vagas_libertadores_pre
        extras = sum(self._vagas_por_campeao.values())
        return min(base + extras, 9)  # Máximo G9
    
    @property
    def zona_liberadores_fim(self) -> int:
        """Última posição que garante Libertadores."""
        return self.total_vagas_libertadores
    
    @property
    def zona_sul_americana_inicio(self) -> int:
        """Primeira posição que garante Sul-Americana."""
        return self.zona_liberadores_fim + 1
    
    @property
    def zona_sul_americana_fim(self) -> int:
        """Última posição que garante Sul-Americana."""
        return self.zona_sul_americana_inicio + self.vagas_sul_americana - 1
    
    def get_vaga_para_posicao(self, posicao: int) -> Optional[TipoVaga]:
        """Retorna o tipo de vaga para uma posição específica."""
        if 1 <= posicao <= 4:
            return TipoVaga.LIBERTADORES_GRUPO
        elif posicao == 5 and self.campeao_copa_brasil is None:
            return TipoVaga.LIBERTADORES_PRE
        elif posicao <= self.zona_liberadores_fim:
            # G6, G7, G8 ou G9 - Libertadores fase de grupos
            return TipoVaga.LIBERTADORES_GRUPO
        elif self.zona_sul_americana_inicio <= posicao <= self.zona_sul_americana_fim:
            return TipoVaga.SUL_AMERICANA
        return None
    
    def get_zona_por_posicao(self, posicao: int) -> str:
        """Retorna a zona (G4, G5, G6... Sul-Americana, Rebaixamento)."""
        if posicao <= 4:
            return f"G4 (Libertadores)"
        elif posicao == 5 and self.campeao_copa_brasil is None:
            return "G5 (Pré-Libertadores)"
        elif posicao <= self.zona_liberadores_fim:
            return f"G{posicao} (Libertadores)"
        elif posicao <= self.zona_sul_americana_fim:
            return f"{posicao}º (Sul-Americana)"
        elif posicao >= 17:
            return f"{posicao}º (Rebaixamento)"
        else:
            return f"{posicao}º"
    
    def to_dict(self) -> dict:
        """Retorna dicionário com a configuração."""
        return {
            "temporada": self.temporada,
            "vagas_libertadores": self.total_vagas_libertadores,
            "vagas_libertadores_grupo": self.vagas_libertadores_grupo,
            "vagas_libertadores_pre": self.vagas_libertadores_pre,
            "vagas_sul_americana": self.vagas_sul_americana,
            "rebaixados": self.rebaixados,
            "zonas": {
                "libertadores": f"1º a {self.zona_liberadores_fim}º",
                "sul_americana": f"{self.zona_sul_americana_inicio}º a {self.zona_sul_americana_fim}º",
                "rebaixamento": "17º a 20º"
            },
            "campeoes": {
                "libertadores": self.campeao_libertadores,
                "sul_americana": self.campeao_sul_americana,
                "copa_brasil": self.campeao_copa_brasil
            }
        }


@dataclass
class ClassificacaoService:
    """Serviço de domínio para classificação."""
    
    @staticmethod
    def calcular_pontos(vitorias: int, empates: int) -> int:
        """Calcula pontos: 3 por vitória, 1 por empate."""
        return (vitorias * 3) + empates
    
    @staticmethod
    def calcular_aproveitamento(pontos: int, jogos: int) -> float:
        """Calcula percentual de aproveitamento."""
        if jogos == 0:
            return 0.0
        return round((pontos / (jogos * 3)) * 100, 2)
    
    @staticmethod
    def calcular_saldo(gp: int, gc: int) -> int:
        """Calcula saldo de goals."""
        return gp - gc
    
    @staticmethod
    def determinar_status(
        posicao: int, 
        vagas_config: Optional[VagasConfig] = None
    ) -> str:
        """Determina o status do time na competição."""
        if vagas_config:
            zona = vagas_config.get_zona_por_posicao(posicao)
            if "Libertadores" in zona:
                return "LIBRERTADORES"
            elif "Sul-Americana" in zona:
                return "SUL-AMERICANA"
            elif "Rebaixamento" in zona:
                return "REBAIXAMENTO"
        
        # Fallback para lógica simples
        if posicao <= 5:
            return "LIBRERTADORES"
        elif posicao <= 11:
            return "SUL-AMERICANA"
        elif posicao >= 17:
            return "REBAIXAMENTO"
        else:
            return "SEM_REBAIXAMENTO"
    
    @staticmethod
    def comparar_classificacao(
        c1: "Classificacao", 
        c2: "Classificacao"
    ) -> int:
        """
        Compara duas classificações para ordenação.
        Retorna:
            -1 se c1 < c2
             0 se c1 == c2
             1 se c1 > c2
        """
        # 1º critério: Pontos
        if c1.pontos != c2.pontos:
            return -1 if c1.pontos > c2.pontos else 1
        
        # 2º critério: Saldo de Goals
        if c1.sg != c2.sg:
            return -1 if c1.sg > c2.sg else 1
        
        # 3º critério: Gols Pró
        if c1.gp != c2.gp:
            return -1 if c1.gp > c2.gp else 1
        
        # 4º critério: Vitórias
        if c1.vitorias != c2.vitorias:
            return -1 if c1.vitorias > c2.vitorias else 1
        
        return 0
