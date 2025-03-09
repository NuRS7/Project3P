from fastapi import FastAPI, Depends, Request, Form
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

DATABASE_URL = "sqlite:///./cars.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

templates = Jinja2Templates(directory="templates")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    year = Column(Integer)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/cars/search")
def search_cars(request: Request, car_name: str = "", db: Session = Depends(get_db)):
    cars = db.query(Car).filter(Car.name.contains(car_name)).all()
    return templates.TemplateResponse("cars/search.html", {"request": request, "cars": cars, "car_name": car_name})

@app.get("/cars/new")
def new_car_form(request: Request):
    return templates.TemplateResponse("cars/new.html", {"request": request})

@app.post("/cars/new")
def add_car(name: str = Form(...), year: int = Form(...), db: Session = Depends(get_db)):
    car = Car(name=name, year=year)
    db.add(car)
    db.commit()
    return RedirectResponse(url="/cars", status_code=303)

@app.get("/cars")
def list_cars(request: Request, db: Session = Depends(get_db)):
    cars = db.query(Car).all()
    return templates.TemplateResponse("cars/list.html", {"request": request, "cars": cars})
