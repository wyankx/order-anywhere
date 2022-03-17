import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from sqlalchemy.pool import NullPool

SqlAlchemyBase = dec.declarative_base()

__factory = None
engine = None


def global_init(db_file):
    global __factory, engine

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = 'postgresql' + db_file[8:]
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False, poolclass=NullPool)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


def close_connection(db_sess: Session):
    db_sess.close()
    db_sess.invalidate()
    engine.dispose()
    __factory.close_all()
