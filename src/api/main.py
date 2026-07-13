"""Main - Ponto de entrada da API."""

from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from src.api.config import config
from src.api.presentation.controllers.classificacao_controller import (
    ClassificacaoController,
)

# API Metrics
REQUEST_COUNT = Counter("api_requests_total", "Total number of API requests", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("api_request_duration_seconds", "Latency of API requests", ["method", "endpoint"])

# Criar app FastAPI
app = FastAPI(
    title="Brasileirão API",
    description="API para dados do Campeonato Brasileiro",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.enable_metrics:
    @app.middleware("http")
    async def monitor_requests(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        
        method = request.method
        endpoint = request.url.path
        status_code = response.status_code
        
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)
        
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Endpoint para exportação de métricas do Prometheus."""
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Instanciar controller
controller = ClassificacaoController()


@app.get("/")
async def root():
    """Rota raiz."""
    return {"message": "Brasileirão API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.get("/api/v1/classificacao")
async def get_classificacao(
    temporada: str = Query("2026", description="Ano da temporada"),
    zona: Optional[str] = Query(
        None, description="Filtrar por zona: LIBERTADORES, SUL-AMERICANA, REBAIXAMENTO"
    ),
):
    """
    Retorna a classificação completa do Brasileirão.

    - **temporada**: Ano da temporada (padrão: 2026)
    - **zona**: Filtrar por zona (opcional)
    """
    return controller.listar_classificacao(temporada, zona)


@app.get("/api/v1/classificacao/posicao/{posicao}")
async def get_posicao(
    posicao: int, temporada: str = Query("2026", description="Ano da temporada")
):
    """
    Retorna a classificação de uma posição específica.
    """
    if posicao < 1 or posicao > 20:
        raise HTTPException(status_code=400, detail="Posição deve estar entre 1 e 20")

    result = controller.buscar_por_posicao(posicao, temporada)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))

    return result


@app.get("/api/v1/classificacao/time/{nome_time}")
async def get_time(
    nome_time: str, temporada: str = Query("2026", description="Ano da temporada")
):
    """
    Retorna a classificação de um time específico.
    """
    result = controller.buscar_por_time(nome_time, temporada)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))

    return result


@app.get("/api/v1/classificacao/vagas")
async def get_vagas(temporada: str = Query("2026", description="Ano da temporada")):
    """
    Retorna a configuração de vagas para Libertadores e Sul-Americana.
    """
    return controller.get_vagas(temporada)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=config.host, port=config.port, reload=config.debug)
