# -*- coding: utf-8- -*-
from time import time
from typing import Optional, Tuple
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
        self.clear()

    def save(
            self,
            code
    ) -> str:
        self.clear()
        uuid = token_hex(12)
        self.cur.execute(
            'INSERT INTO code (save_time, code, uuid) VALUES (?, ?, ?)',
            (time(), code, uuid)
        )
        self.con.commit()
        return uuid

    def load(
            self,
            uuid: str
    ) -> Optional[Tuple[int, str, str]]:
        self.clear()
        return self.cur.execute('SELECT * FROM code WHERE uuid = ?', (uuid,)).fetchone()

    def clear(self):
        data = self.cur.execute('SELECT * FROM code').fetchall()
        now = time()
        for i in data:
            if now - i[0] >= self.timeout:
                self.cur.execute('DELETE FROM code WHERE save_time = ?', (i[0],))
