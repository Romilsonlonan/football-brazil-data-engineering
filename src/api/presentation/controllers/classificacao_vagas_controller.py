"""Controller para classificação com vagas.

Este controller estende o ClassificacaoController para incluir endpoints específicos
para classificação com vagas em competições internacionais (Libertadores e Sul-Americana).

Usa o Use Case ListarClassificacaoVagasUseCase para manter a arquitetura limpa.
"""

from typing import Dict

from src.api.application.use_cases.listar_classificacao_vagas import (
    ListarClassificacaoVagasUseCase,
)


class ClassificacaoVagasController:
    """Controller para operações de classificação com vagas.

    Este controller gerencia endpoints relacionados à classificação do Campeonato
    Brasileiro com informações de vagas para competições internacionais:
    - Copa Libertadores (G4, G5, G6)
    - Copa Sul-Americana
    - Rebaixamento
    """

    def __init__(self):
        """Inicializa o controller com o use case."""
        self._use_case = ListarClassificacaoVagasUseCase()

    def listar_classificacao_completa(
        self, temporada: str = "2026", usar_dto: bool = False
    ) -> Dict:
        """
        Lista a classificação completa com vagas.

        Args:
            temporada: Ano da temporada
            usar_dto: Se True, retorna DTOs serializáveis

        Returns:
            Dicionário com classificação e metadados
        """
        try:
            if usar_dto:
                classificacao = self._use_case.get_all_as_dto(temporada)
                data = [c.to_dict() for c in classificacao]
            else:
                classificacao = self._use_case.get_all(temporada)
                data = [self._to_dict(c) for c in classificacao]

            return {
                "success": True,
                "data": {
                    "temporada": temporada,
                    "classificacao": data,
                    "total_times": len(data),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def listar_libertadores(
        self, temporada: str = "2026", usar_dto: bool = False
    ) -> Dict:
        """
        Lista times classificados para a Copa Libertadores.

        Args:
            temporada: Ano da temporada
            usar_dto: Se True, retorna DTOs serializáveis

        Returns:
            Dicionário com times classificados para Libertadores
        """
        try:
            if usar_dto:
                libertadores = self._use_case.get_libertadores_as_dto(temporada)
                data = [c.to_dict() for c in libertadores]
            else:
                libertadores = self._use_case.get_libertadores(temporada)
                data = [self._to_dict(c) for c in libertadores]

            return {
                "success": True,
                "data": {
                    "temporada": temporada,
                    "zona": "LIBERTADORES",
                    "quantidade": len(data),
                    "times": data,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def listar_sul_americana(
        self, temporada: str = "2026", usar_dto: bool = False
    ) -> Dict:
        """
        Lista times classificados para a Copa Sul-Americana.

        Args:
            temporada: Ano da temporada
            usar_dto: Se True, retorna DTOs serializáveis

        Returns:
            Dicionário com times classificados para Sul-Americana
        """
        try:
            if usar_dto:
                sulamericana = self._use_case.get_sul_americana_as_dto(temporada)
                data = [c.to_dict() for c in sulamericana]
            else:
                sulamericana = self._use_case.get_sul_americana(temporada)
                data = [self._to_dict(c) for c in sulamericana]

            return {
                "success": True,
                "data": {
                    "temporada": temporada,
                    "zona": "SUL-AMERICANA",
                    "quantidade": len(data),
                    "times": data,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def listar_rebaixados(
        self, temporada: str = "2026", usar_dto: bool = False
    ) -> Dict:
        """
        Lista times na zona de rebaixamento.

        Args:
            temporada: Ano da temporada
            usar_dto: Se True, retorna DTOs serializáveis

        Returns:
            Dicionário com times rebaixados
        """
        try:
            if usar_dto:
                rebaixados = self._use_case.get_rebaixados_as_dto(temporada)
                data = [c.to_dict() for c in rebaixados]
            else:
                rebaixados = self._use_case.get_rebaixados(temporada)
                data = [self._to_dict(c) for c in rebaixados]

            return {
                "success": True,
                "data": {
                    "temporada": temporada,
                    "zona": "REBAIXAMENTO",
                    "quantidade": len(data),
                    "times": data,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def buscar_por_posicao(self, posicao: int, temporada: str = "2026") -> Dict:
        """
        Busca a classificação de uma posição específica.

        Args:
            posicao: Posição na tabela (1-20)
            temporada: Ano da temporada

        Returns:
            Dicionário com classificação da posição
        """
        try:
            if posicao < 1 or posicao > 20:
                return {"success": False, "error": "Posição deve estar entre 1 e 20"}

            classificacao = self._use_case.get_by_posicao(posicao, temporada)

            if not classificacao:
                return {"success": False, "error": f"Posição {posicao} não encontrada"}

            return {"success": True, "data": self._to_dict(classificacao)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def buscar_por_time(self, nome_time: str, temporada: str = "2026") -> Dict:
        """
        Busca a classificação de um time específico.

        Args:
            nome_time: Nome do time
            temporada: Ano da temporada

        Returns:
            Dicionário com classificação do time
        """
        try:
            classificacao = self._use_case.get_by_time(nome_time, temporada)

            if not classificacao:
                return {"success": False, "error": f"Time '{nome_time}' não encontrado"}

            return {"success": True, "data": self._to_dict(classificacao)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_resumo_temporada(self, temporada: str = "2026") -> Dict:
        """
        Retorna um resumo completo da temporada.

        Args:
            temporada: Ano da temporada

        Returns:
            Dicionário com resumo da temporada
        """
        try:
            resumo = self._use_case.get_resumo_temporada(temporada)

            return {"success": True, "data": resumo}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _to_dict(self, classificacao) -> dict:
        """Converte entidade para dicionário."""
        return {
            "posicao": classificacao.posicao,
            "time": classificacao.time.nome,
            "time_reduzido": classificacao.time.nome_reduzido,
            "jogos": classificacao.jogos,
            "vitorias": classificacao.vitorias,
            "empates": classificacao.empates,
            "derrotas": classificacao.derrotas,
            "gp": classificacao.gp,
            "gc": classificacao.gc,
            "sg": classificacao.sg,
            "pontos": classificacao.pontos,
            "aproveitamento": classificacao.aproveitamento,
            "zona": classificacao.zona_computada or "",
            "status": classificacao.status_curto or "",
        }
