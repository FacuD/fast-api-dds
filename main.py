from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuración de la base de datos
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Modelo de datos
class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    barrio = Column(String, index=True)
    ha_solicitado_vianda = Column(Integer)  # 0: No, 1: Sí


# Crear la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint para obtener las localidades y las personas registradas
@app.get("/localidades")
def obtener_localidades(db: Session = Depends(get_db)):
    # Consulta para obtener las localidades y la cantidad de personas que solicitaron vianda
    query_personas_con_vianda = select(Persona.barrio, Persona.nombre).where(
        Persona.ha_solicitado_vianda == 1
    )

    personas_con_vianda = db.execute(query_personas_con_vianda).all()

    localidades = {}
    # breakpoint()

    for barrio, nombre in personas_con_vianda:
        if barrio not in localidades:
            localidades[barrio] = {
                "cantidad de personas en situación de calle que solicitaron vianda": 1,
                "nombres": [],
            }
        else:
            localidades[barrio][
                "cantidad de personas en situación de calle que solicitaron vianda"
            ] += 1
        localidades[barrio]["nombres"].append(nombre)

    return localidades


# Población inicial
def init_db():
    db = SessionLocal()
    personas = [
        Persona(nombre="Juan", barrio="Boedo", ha_solicitado_vianda=1),
        Persona(nombre="María", barrio="Palermo", ha_solicitado_vianda=0),
        Persona(nombre="Luis", barrio="Caballito", ha_solicitado_vianda=1),
        Persona(nombre="Ana", barrio="Caballito", ha_solicitado_vianda=1),
        Persona(nombre="Pedro", barrio="Lugano", ha_solicitado_vianda=0),
        Persona(nombre="Joaco", barrio="Lugano", ha_solicitado_vianda=1),
    ]
    db.add_all(personas)
    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()  # Inicializa la base de datos con algunos datos de ejemplo
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
