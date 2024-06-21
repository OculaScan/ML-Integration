from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

# App
from flask import Flask

app = Flask(__name__)
app.secret_key = "buat_secret_key_lebih_rumit"

# Konfigurasi SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql://root:@localhost/flask_deteksipenyakitmata"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    password = Column(String(255))
    create_at = Column(
        String(50), default=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def __repr__(self):
        return "<UserModel(name='%s', email='%s', password='%s', create_at='%s')>" % (
            self.name,
            self.email,
            self.password,
            self.create_at,
        )


# Membuat tabel
if __name__ == "__main__":
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    Base.metadata.create_all(engine)  # Membuat tabel sesuai definisi model
