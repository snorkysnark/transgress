from typing import NamedTuple
from pathlib import Path

##
def read_file(file: Path):
    return file.open('r').read()
##

class Sql(NamedTuple):
    select_sql: str
    copy_sql: str
    before_copy_sql: str
    after_copy_sql: str

    @classmethod
    def load_files(cls, folder: Path):
        return cls(
            select_sql=read_file(folder.joinpath('select.sql')),
            copy_sql=read_file(folder.joinpath('copy.sql')),
            before_copy_sql=read_file(folder.joinpath('before_copy.sql')),
            after_copy_sql=read_file(folder.joinpath('after_copy.sql'))
        )
