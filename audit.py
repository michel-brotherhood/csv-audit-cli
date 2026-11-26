"""Audit CSV structure without uploading or modifying the input file."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def audit(path, key=None, encoding='utf-8-sig'):
    with Path(path).open(newline='', encoding=encoding) as source:
        reader = csv.DictReader(source, restkey='__extra__', restval=None)
        fields = reader.fieldnames
        if not fields:
            raise ValueError('CSV vazio ou sem cabeçalho')
        if len(fields) != len(set(fields)) or any(not name for name in fields):
            raise ValueError('Cabeçalho contém colunas vazias ou repetidas')
        if key and key not in fields:
            raise ValueError(f'Coluna de chave inexistente: {key}')
        missing = Counter({name: 0 for name in fields})
        seen = set()
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
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.file, args.key, args.encoding), ensure_ascii=False, indent=2))
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        parser.exit(2, f'Erro: {error}\n')


if __name__ == '__main__':
    main()
