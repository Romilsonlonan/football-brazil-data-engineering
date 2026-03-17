"""Entidade Classificacao."""

from dataclasses import dataclass
from typing import Optional

from .time import Time
from .vagas import VagasConfig


@dataclass
class Classificacao:
    """Entidade que representa a classificação de um time no Brasileirão."""
    
    posicao: int
    time: Time
    jogos: int = 0
    vitorias: int = 0
    empates: int = 0
    derrotas: int = 0
    gp: int = 0  # Gols Pró
    gc: int = 0  # Gols Contra
    sg: int = 0  # Saldo de Gols
    pontos: int = 0
    
    # Campos opcionais de metadata
    id: Optional[int] = None
    temporada: Optional[str] = None
    
    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.posicao < 1 or self.posicao > 20:
            raise ValueError("Posição deve estar entre 1 e 20")
        
        if self.jogos < 0:
            raise ValueError("Número de jogos não pode ser negativo")
        
        # Recalcula pontos se não for fornecido
        if self.pontos == 0 and (self.vitorias > 0 or self.empates > 0):
            self.pontos = (self.vitorias * 3) + (self.empates * 1)
        
        # Recalcula saldo de gol se não for fornecido
        if self.sg == 0 and (self.gp > 0 or self.gc > 0):
            self.sg = self.gp - self.gc
    
    @property
    def aproveitamento(self) -> float:
        """Calcula o percentual de aproveitamento."""
        if self.jogos == 0:
            return 0.0
        return round((self.pontos / (self.jogos * 3)) * 100, 2)
    
    def get_status(self, vagas_config: Optional[VagasConfig] = None) -> str:
        """Retorna o status do time na competição."""
        if vagas_config:
            return vagas_config.get_zona_por_posicao(self.posicao)
        
        # Fallback para lógica simples
        if self.posicao <= 4:
            return "LIBRERTADORES (G4)"
        elif self.posicao == 5:
            return "PRÉ-LIBERTADORES (G5)"
        elif self.posicao <= 6:
            return "SUL-AMERICANA"
        elif self.posicao >= 17:
            return "REBAIXAMENTO"
        else:
            return "SEM_REBAIXAMENTO"
    
    @property
    def zona(self) -> str:
        """Retorna a zona do time (propriedade de conveniência)."""
        return self.get_status()
    
    def __str__(self) -> str:
        return f"{self.posicao}º - {self.time.nome_reduzido} ({self.pontos} pts)"
