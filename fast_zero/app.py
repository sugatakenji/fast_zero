from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message

app = FastAPI()


@app.get('/', response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!!!'}


@app.get('/exercicio-html', response_class=HTMLResponse)
def read_html():
    return """
    <html>
        <header>
            <title>Html response</title>
        </header>
        <body>
            <h1>Olá Mundo!</h1>
        </body>
    </html>
    """
