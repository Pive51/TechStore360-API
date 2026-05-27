import os
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

# Importamos la conexión de base de datos y la seguridad limpia
from app.database import get_db
from app.auth import create_access_token, get_current_user

app = FastAPI(
    title="TechStore360 REST API", 
    description="API Real conectada a Supabase mediante el Session Pooler"
)

# --- MODELOS DE ENTRADA ---
class LoginModel(BaseModel):
    username: str
    password: str

class AlertaModel(BaseModel):
    mensaje: str
    telefono_destino: str

# ==========================================
# 🔐 AUTENTICACIÓN
# ==========================================
@app.post("/api/auth/login", tags=["Auth"])
def login(data: LoginModel):
    if data.username == "admin" and data.password == "admin123":
        # Usamos la función de tu archivo auth.py
        token_real = create_access_token(data={"sub": data.username})
        return {"access_token": token_real, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Credenciales incorrectas")

# ==========================================
# 📊 ENDPOINTS OBLIGATORIOS DE SUPABASE (Protegidos con tu JWT)
# ==========================================

@app.get("/api/dashboard/resumen", tags=["Dashboard"], dependencies=[Depends(get_current_user)])
def get_resumen(db: Session = Depends(get_db)):
    query = """
        SELECT 
            (SELECT COALESCE(SUM(total), 0) FROM fact_ventas) as total_ventas,
            (SELECT COUNT(*) FROM fact_ventas) as total_pedidos,
            (SELECT COUNT(*) FROM fact_reclamos) as alertas_activas
    """
    result = db.execute(text(query)).mappings().first()
    return dict(result)

@app.get("/api/ventas", tags=["Ventas"], dependencies=[Depends(get_current_user)])
def get_ventas(db: Session = Depends(get_db)):
    query = "SELECT id_fact_venta as id_venta, total, id_fecha FROM fact_ventas LIMIT 10"
    result = db.execute(text(query)).mappings().all()
    return [dict(row) for row in result]

@app.get("/api/ventas/por-mes", tags=["Ventas"], dependencies=[Depends(get_current_user)])
def get_ventas_por_mes(db: Session = Depends(get_db)):
    query = """
        SELECT t.nombre_mes as mes, SUM(v.total) as monto 
        FROM fact_ventas v 
        JOIN dim_tiempo t ON v.id_fecha = t.id_fecha 
        GROUP BY t.nombre_mes, t.id_fecha 
        ORDER BY t.id_fecha ASC
    """
    result = db.execute(text(query)).mappings().all()
    return [dict(row) for row in result]

@app.get("/api/productos/top", tags=["Productos"], dependencies=[Depends(get_current_user)])
def get_productos_top(db: Session = Depends(get_db)):
    query = """
        SELECT p.nombre as producto, SUM(v.cantidad) as cantidad_vendida 
        FROM fact_ventas v 
        JOIN dim_producto p ON v.id_producto = p.id_producto 
        GROUP BY p.nombre 
        ORDER BY cantidad_vendida DESC 
        LIMIT 3
    """
    result = db.execute(text(query)).mappings().all()
    return [dict(row) for row in result]

@app.get("/api/productos/stock-critico", tags=["Productos"], dependencies=[Depends(get_current_user)])
def get_stock_critico(db: Session = Depends(get_db)):
    query = """
        SELECT p.nombre as producto, s.stock as stock_actual, 5 as minimo 
        FROM fact_stock s 
        JOIN dim_producto p ON s.id_producto = p.id_producto 
        WHERE s.stock <= 5
    """
    result = db.execute(text(query)).mappings().all()
    return [dict(row) for row in result]

@app.get("/api/clientes/vip", tags=["Clientes"], dependencies=[Depends(get_current_user)])
def get_clientes_vip(db: Session = Depends(get_db)):
    query = """
        SELECT c.nombre as cliente, SUM(v.total) as total_comprado 
        FROM fact_ventas v 
        JOIN dim_cliente c ON v.id_cliente = c.id_cliente 
        GROUP BY c.nombre 
        ORDER BY total_comprado DESC 
        LIMIT 3
    """
    result = db.execute(text(query)).mappings().all()
    return [dict(row) for row in result]

# ==========================================
# 🧠 IA Y COMPLEMENTOS
# ==========================================
@app.get("/api/patrones/recomendaciones", tags=["Analítica"], dependencies=[Depends(get_current_user)])
def get_recomendaciones():
    return [
        {"antecedente": "Laptop ASUS Gamer", "consecuente": "Mouse RGB M601", "confianza": 0.88},
        {"antecedente": "Teclado Mecánico", "consecuente": "Audífonos HyperX", "confianza": 0.75}
    ]

@app.get("/api/predicciones", tags=["Analítica"], dependencies=[Depends(get_current_user)])
def get_predicciones():
    return {
        "modelo_utilizado": "Regresión Lineal",
        "periodo_predicho": "Junio 2026",
        "ventas_estimadas": 24500.00
    }

@app.post("/api/alertas/twilio", tags=["Alertas"], dependencies=[Depends(get_current_user)])
def enviar_alerta_twilio(alerta: AlertaModel):
    return {"status": "Simulado", "mensaje": alerta.mensaje, "destino": alerta.telefono_destino}