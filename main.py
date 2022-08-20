from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from avoscript import imp_parser, Lexer, StdString
import sys


class Code(BaseModel):
    value: str


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/exec')
async def index(code: Code):
    if len(code.value) > 1024:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                'error': 'code too large'
            }
        )
    parsed = imp_parser(Lexer.lex(code.value))
    if parsed is not None:
        x = StdString()
        sys.stdout = x
        parsed.value.eval()
        sys.stdout = sys.__stdout__
        return {
            'response': x.out
        }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'error': 'error when code parsed'}
    )
