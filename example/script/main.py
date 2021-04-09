import trio
import asks
from safetywrap import Ok, Err

async def try_download(id, url):
    try:
        response = await asks.get(url)
        return Ok((id, response.text))
    except Exception as err:
        return Err(err)

async def page_task(id, url, out):
    await out.send(await try_download(id, url))

async def run(input_rows, out):
    async with trio.open_nursery() as nurs:
        for (id, url) in input_rows:
            nurs.start_soon(page_task, id, url, out)
