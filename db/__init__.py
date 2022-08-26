# -*- coding: utf-8- -*-
from time import time
from typing import NoReturn, Optional, Tuple
from secrets import token_hex
from sqlite3 import connect


class DB:
    def __init__(
            self,
            db_name: str = 'code.db',
            timeout: int = 60 * 60 * 24  # 24 hours to save code
    ):
        self.con = connect(db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS code (
                save_time INTEGER,
                code TEXT,
                uuid TEXT
            );'''
        )
        self.con.commit()
        self.timeout = timeout

    def save(
            self,
            code
    ) -> NoReturn:
        self.cur.execute(
            'INSERT INTO code (save_time, code, uuid) VALUES (?, ?, ?)',
            (time(), code, token_hex(8))
        )
        self.con.commit()

    def load(
            self,
            uuid: str
    ) -> Optional[Tuple[int, str, str]]:
        return self.cur.execute('SELECT * FROM code WHERE uuid = ?', (uuid,)).fetchone()

    def clear(self):
        pass
