# -*- coding: utf-8 -*-
import sys
from multiprocessing import Process, Manager

from avoscript import version
from avoscript.lexer import Lexer
from avoscript.lexer.types import Signal, StdString, LevelIndex
from avoscript.parser import imp_parser
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from db import DB


class Code(BaseModel):
    value: str


class TimeoutException(Exception):
    pass


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
db = DB()


def execute_wrapper(stdout, parsed, lvl_index, signal, d):
    sys.stdout = stdout
    parsed.value.eval([], [], lvl_index, {}, signal)
    sys.stdout = sys.__stdout__
    d['out'] = stdout.out


@app.post('/exec')
async def execute(code: Code):
    if len(code.value) > 1024:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                'error': 'code too large'
            }
        )
    lexed = ''
    try:
        lexed = Lexer.lex(code.value)
    except SystemExit as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': f'[ERROR]: SyntaxError - {e}'}
        )
    parsed = None
    try:
        parsed = imp_parser(lexed)
    except RuntimeError as e:

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'error': f'[ERROR]: SyntaxError - {e}'}
        )
    if parsed is not None:
        manager = Manager()
        d = manager.dict()
        out = ''
        try:
            process = Process(target=execute_wrapper, args=(StdString(), parsed, LevelIndex(), Signal(), d))
            process.start()
            process.join(5)
            if process.is_alive():
                process.terminate()
                return JSONResponse(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    content={
                        'error': 'timeout'
                    }
                )
            if 'out' in d:
                out = d['out']
        except SystemExit as e:
            sys.stdout = sys.__stdout__
            print(out, e)
        except TimeoutException as e:
            return JSONResponse(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                content={
                    'error': 'timeout limit (5 seconds)'
                }
            )
        sys.stdout = sys.__stdout__
        return {
            'response': out
        }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'error': 'error when code parsed'}
    )


@app.post('/save')
async def save_code(code: Code):
    if len(code.value) > 1024:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                'error': 'code too large'
            }
        )
    name = db.save(code.value)
    return {
        'response': name
    }


@app.get('/code/{uuid}')
async def load_code(uuid: str):
    response = db.load(uuid)
    if response:
        save_time, code, uuid = response
        return {
            'response': code
        }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'error': 'this code is not exists'
        }
    )


@app.get('/version')
def avoscript_version():
    return {
        'response': version
    }
