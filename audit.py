"""Audit CSV structure without uploading or modifying the input file."""
import argparse
import csv
import json
import sqlite3
import tempfile
from collections import Counter
from contextlib import ExitStack, closing
from pathlib import Path


def audit(path, key=None, encoding='utf-8-sig', disk=False):
    with ExitStack() as stack:
        source = stack.enter_context(Path(path).open(newline='', encoding=encoding))
        if disk:
            directory = stack.enter_context(tempfile.TemporaryDirectory(prefix='csv-audit-'))
            database = stack.enter_context(closing(sqlite3.connect(Path(directory) / 'keys.sqlite3')))
            database.execute('CREATE TABLE seen (identity TEXT PRIMARY KEY) WITHOUT ROWID')
        else:
            seen = set()
        reader = csv.DictReader(source, restkey='__extra__', restval=None)
        fields = reader.fieldnames
        if not fields:
            raise ValueError('CSV vazio ou sem cabeçalho')
        if len(fields) != len(set(fields)) or any(not name for name in fields):
            raise ValueError('Cabeçalho contém colunas vazias ou repetidas')
        if key and key not in fields:
            raise ValueError(f'Coluna de chave inexistente: {key}')
        missing = Counter({name: 0 for name in fields})
        duplicates = []
        malformed = []
        rows = 0
        for number, row in enumerate(reader, start=2):
            rows += 1
            if row.get('__extra__') is not None or any(row[name] is None for name in fields):
                malformed.append(number)
            for name in fields:
                if row[name] is None or not row[name].strip():
                    missing[name] += 1
            identity = row[key] if key else tuple(row[name] for name in fields)
            if disk:
                encoded = json.dumps(identity, ensure_ascii=False, separators=(',', ':'))
                inserted = database.execute('INSERT OR IGNORE INTO seen VALUES (?)', (encoded,)).rowcount
                if not inserted:
                    duplicates.append(number)
            else:
                if identity in seen:
                    duplicates.append(number)
                else:
                    seen.add(identity)
    return {'rows': rows, 'columns': fields, 'missing_by_column': dict(missing),
            'duplicate_rows': duplicates, 'malformed_rows': malformed,
            'duplicate_basis': key or 'entire row'}


def main():
    parser = argparse.ArgumentParser(description='Audita campos vazios, duplicatas e formato de um CSV local.')
    parser.add_argument('file', type=Path)
    parser.add_argument('--key', help='Coluna usada para detectar duplicatas (padrão: linha completa)')
    parser.add_argument('--encoding', default='utf-8-sig')
    parser.add_argument('--disk', action='store_true', help='Armazena chaves de duplicatas em SQLite temporário')
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.file, args.key, args.encoding, args.disk), ensure_ascii=False, indent=2))
    except (OSError, UnicodeError, csv.Error, ValueError, sqlite3.Error) as error:
        parser.exit(2, f'Erro: {error}\n')


if __name__ == '__main__':
    main()
