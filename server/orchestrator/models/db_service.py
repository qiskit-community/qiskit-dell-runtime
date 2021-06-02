
from .base import Session, engine, Base

from .runtime_program_model import RuntimeProgram

class DBService():
    def __init__(self):
        Base.metadata.create_all(engine)

    def save_runtime_program(self, runtime_program: RuntimeProgram):
        session = Session()
        try:
            session.add(runtime_program)
            session.commit()
        finally:
            session.close()

