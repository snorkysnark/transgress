import psycopg3
from psycopg3 import Copy
from .sql import Sql
from typing import Sequence, Tuple, Any, NamedTuple, ContextManager
from safetywrap import Option, Some, Nothing
##

class Db:
    sql: Sql
    conn: psycopg3.Connection
    cursor: psycopg3.Cursor
    select_result: Option[Sequence[Tuple[Any, ...]]]

    def __init__(self, sql: Sql, dbname: str):
        self.sql = sql
        self.conn = psycopg3.connect(dbname=dbname)
        self.cursor = self.conn.cursor()
        if sql.select_sql != '':
            self.cursor.execute(sql.select_sql)
            self.select_result = Some(self.cursor.fetchall())
        else:
            self.select_result = Nothing()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

##
class MaybeCopy(NamedTuple):
    copy_opt: Option[Copy]

    def write_row(self, row: Sequence[Any]):
        for copy in self.copy_opt:
            copy.write_row(row)

##
class DbExport(NamedTuple):
    db: Db
    copy_gen: ContextManager[Copy]

    def __enter__(self):
        self.db.cursor.execute(self.db.sql.before_copy_sql)
        return self.copy_gen.__enter__()

    def __exit__(self, type, value, traceback):
        self.copy_gen.__exit__(type, value, traceback)
        self.db.cursor.execute(self.db.sql.after_copy_sql)

##
class MaybeExport(NamedTuple):
    export_opt: Option[DbExport]

    def __enter__(self):
        return MaybeCopy(self.export_opt.map(lambda export: export.__enter__()))

    def __exit__(self, type, value, traceback):
        for export in self.export_opt:
            export.__exit__(type, value, traceback)
##
class MaybeDb(NamedTuple):
    db_opt: Option[Db]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for db in self.db_opt:
            db.close()

    def select_result(self) -> Option[Sequence[Tuple[Any, ...]]]:
        return self.db_opt.and_then(lambda db: db.select_result)

    def commit(self):
        for db in self.db_opt:
            db.conn.commit()

    def export(self) -> Option[DbExport]:
        return self.db_opt.map(lambda db: DbExport(db, db.cursor.copy(db.sql.copy_sql)))
