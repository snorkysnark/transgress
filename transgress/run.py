import sys
import trio
from pathlib import Path
from enum import Enum
from .sql import Sql
from .postgres import Db, MaybeDb, MaybeExport
from safetywrap import Option, Some, Nothing
##
class RunOptions(Enum):
    NODB = 1
    NOEXPORT = 2
    FULL = 3
##

async def run_script(script, input_rows, sender):
    async with sender:
        await script.run(input_rows, sender)
##
def handle_error(error, log_file):
    print(error)
    log_file.write(f"{error}\n")
##

def handle_result(result, maybe_export, log_file):
    value = result.unwrap_or_else(lambda err: handle_error(err, log_file))
    if value is not None:
        print(value)
        maybe_export.write_row(value)
##
def clamp_to_limit(rows, limit_opt: Option[int]):
    for limit in limit_opt:
        if len(rows) >= limit:
            rows = rows[:limit]
    return rows

##
async def async_transform(script, dbname: Option[str], sql: Sql, export: bool, limit: Option[int], log_path: Path):
    with log_path.open('w') as log_file:
        with MaybeDb(dbname.map(lambda name: Db(sql, name))) as maybe_db:
            input_rows = maybe_db.select_result().unwrap_or([])
            input_rows = clamp_to_limit(input_rows, limit)

            with MaybeExport((maybe_db.export() if export else Nothing())) as maybe_export:
                sender, receiver = trio.open_memory_channel(0)
                async with trio.open_nursery() as nurs:
                    nurs.start_soon(run_script, script, input_rows, sender)
                    async with receiver:
                        async for output_result in receiver:
                            handle_result(output_result, maybe_export, log_file)

            if export:
                maybe_db.commit()
##
def transform(script, dbname: Option[str], sql: Sql, export: bool, limit: Option[int], log_path: Path):
    trio.run(async_transform, script, dbname, sql, export, limit, log_path)

##
def run(folder: Path, options: RunOptions, limit: Option[int]):
    sql = Sql.load_files(folder)

    sys.path.append(str(folder))
    import script #type: ignore

    log_path = folder.joinpath('errors.log')

    if options != RunOptions.NODB:
        if script.DBNAME != '':
            transform(script, Some(script.DBNAME), sql, options == RunOptions.FULL, limit, log_path)
        else:
            print('DBNAME not specified. Run with --nodb or fill DBNAME in script/__init__.py')
    else:
        transform(script, Nothing(), sql, False, limit, log_path)
