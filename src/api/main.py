"""Main - Ponto de entrada da API."""

import time
from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

from src.api.config import config
from src.api.presentation.controllers.classificacao_controller import ClassificacaoController

# Custom metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total de requisições da API',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'Latência das requisições em segundos',
    ['method', 'endpoint']
)

# Criar app FastAPI
app = FastAPI(
    title="Brasileirão API",
    description="API para dados do Campeonato Brasileiro",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para coletar métricas do Prometheus
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    # Executar a requisição
    response = await call_next(request)
    
    # Calcular duração
    duration = time.time() - start_time
    
    # Ignorar endpoint de métricas e health para não sujar os dados
    if request.url.path not in ["/metrics", "/health", "/"]:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
    return response


# Instanciar controller
controller = ClassificacaoController()


@app.get("/")
async def root():
    """Rota raiz."""
    return {
        "message": "Brasileirão API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.get("/metrics")
def get_metrics():
    """Endpoint de métricas para o Prometheus."""
    return Response(
        content=generate_latest(), 
        media_type="text/plain",
        headers={"Access-Control-Allow-Origin": "*"}
    )


@app.get("/api/v1/gold-classificacao")
async def get_classificacao(
    temporada: str = Query("2026", description="Ano da temporada"),
    zona: Optional[str] = Query(None, description="Filtrar por zona: LIBERTADORES, SUL-AMERICANA, REBAIXAMENTO")
):
    """
    Retorna a classificação completa da camada Gold do Brasileirão.
    
    - **temporada**: Ano da temporada (padrão: 2026)
    - **zona**: Filtrar por zona (opcional)
    """
    return controller.listar_classificacao(temporada, zona)


@app.get("/api/v1/gold-classificacao/posicao/{posicao}")
async def get_posicao(
    posicao: int,
    temporada: str = Query("2026", description="Ano da temporada")
):
    """
    Retorna a classificação de uma posição específica (Camada Gold).
    """
    if posicao < 1 or posicao > 20:
        raise HTTPException(status_code=400, detail="Posição deve estar entre 1 e 20")
    
    result = controller.buscar_por_posicao(posicao, temporada)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return result


@app.get("/api/v1/gold-classificacao/time/{nome_time}")
async def get_time(
    nome_time: str,
    temporada: str = Query("2026", description="Ano da temporada")
):
    """
    Retorna a classificação de um time específico (Camada Gold).
    """
    result = controller.buscar_por_time(nome_time, temporada)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return result


@app.get("/api/v1/gold-classificacao/vagas")
async def get_vagas(
    temporada: str = Query("2026", description="Ano da temporada")
):
    """
    Retorna a configuração de vagas para Libertadores e Sul-Americana (Camada Gold).
    """
    return controller.get_vagas(temporada)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
