from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.core.graph_db import create_constraints, close_driver
from app.core.auth import create_user_constraint, seed_default_users
from app.api import ingest, appraisal, cam, risk, stats, auth, chat, documents, research, banking, notifications, audit, reconcile, gstn, erp


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — don't crash if Neo4j isn't ready yet
    try:
        create_constraints()
        create_user_constraint()
        seed_default_users()
        print("Neo4j connected, constraints created.")
    except Exception as e:
        print(f"WARNING: Neo4j not available at startup: {e}")
        print("The app will start but DB operations will fail until Neo4j is reachable.")
    yield
    # Shutdown
    close_driver()


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Credit Appraisal System using Knowledge Graphs for Corporate Lending",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingest.router, prefix="/api/data", tags=["Data Ingestion"])
app.include_router(reconcile.router, prefix="/api/reconcile", tags=["Credit Appraisal & GST Compliance"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit & CAM Reports"])
app.include_router(appraisal.router, prefix="/api/appraisal", tags=["Credit Appraisal"])
app.include_router(cam.router, prefix="/api/cam", tags=["Credit Appraisal Memo"])
app.include_router(documents.router, prefix="/api/documents", tags=["Document Processing"])
app.include_router(research.router, prefix="/api/research", tags=["External Research"])
app.include_router(banking.router, prefix="/api/banking", tags=["Banking Analysis"])
app.include_router(risk.router, prefix="/api/risk", tags=["Credit Risk"])
app.include_router(stats.router, prefix="/api/stats", tags=["Dashboard Stats"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Assistant"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(gstn.router, prefix="/api/gstn", tags=["GSTN/GSP Integration"])
app.include_router(erp.router, prefix="/api/erp", tags=["ERP Integration"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}
