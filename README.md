# Transgress
> Python framework for transforming postgres data  
> (useful for web scraping and the like)

## Installation
```
pip install git+https://github.com/snorkysnark/transgress.git
```
## Usage
Run `transgress new [folder]` to create a script template:

```
├── script
│   ├── __init__.py
│   └── main.py
├── select.sql
├── before_copy.sql
├── copy.sql
└── after_copy.sql
```
### \_\_init\_\_.py
Put the database name here:
```python
DBNAME='transgress_example'
```

### select.sql
This is the input of the script:
```sql
SELECT id, url
FROM pages
WHERE content IS NULL;
```

### before_copy.sql
Optional action before exporting from the script.
Yout can create temporary tables here.
```sql
CREATE TABLE pages_update(
	id INT,
	content TEXT
);
```
### copy.sql
What to do with the output of the script.
Only copy statements go here.
```sql
COPY pages_update FROM STDIN;
```

### after_copy.sql
Optional action to do after the copying:
```sql
UPDATE pages
SET content = tmp.content
FROM pages_update AS tmp
WHERE pages.id = tmp.id;

DROP TABLE pages_update;
```

### main.py
Finally, the script itself:
```python
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

# Main method, called by the framework
# Return rows with out.send(Ok(value1, value2, value3, ...))
# Return errors with out.send(Err("Error message"))
async def run(input_rows, out):
    async with trio.open_nursery() as nurs:
        for (id, url) in input_rows:
            nurs.start_soon(page_task, id, url, out)
```

### Run command
Try on only 10 rows, without exporting:
```
transgress run --noexport --limit 10
```
Full transform:
```
transgress run
