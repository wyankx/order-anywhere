import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from sqlalchemy.pool import NullPool

SqlAlchemyBase = dec.declarative_base()

__factory = None
engine = None
db_session = None


def global_init(db_file):
    global __factory, engine, db_session

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = 'postgresql' + db_file[8:]
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False, poolclass=NullPool)
    __factory = orm.sessionmaker(bind=engine, autocommit=False, autoflush=False)

    from . import __all_models

    db_session = create_session()

    SqlAlchemyBase.metadata.create_all(engine)
    SqlAlchemyBase.query = db_session.query_property()


def create_session() -> Session:
    global __factory
    return orm.scoped_session(__factory)


def get_session() -> Session:
    return db_session


def close_connection(db_sess: orm.scoped_session):
    db_sess.remove()
    engine.dispose()
