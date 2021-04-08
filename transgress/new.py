from pathlib import Path

def new(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)

    folder.joinpath('select.sql').touch()
    folder.joinpath('copy.sql').touch()
    folder.joinpath('before_copy.sql').touch()
    folder.joinpath('after_copy.sql').touch()

    script_folder = folder.joinpath('script')
    script_folder.mkdir()

    with script_folder.joinpath('__init__.py').open('w') as init_py:
        init_py.write("""DBNAME=''
from .main import run""")

    with script_folder.joinpath('main.py').open('w') as init_py:
        init_py.write("""from safetywrap import Ok, Err

async def run(input_rows, out):
    await out.send(Ok(()))""")
