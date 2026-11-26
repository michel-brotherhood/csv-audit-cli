# CSV Audit CLI

Audita um CSV local sem dependências externas e sem alterar ou enviar os dados. Conta linhas, campos vazios por coluna, duplicatas e linhas com número incorreto de campos.

## Uso

Requer Python 3.9 ou superior.

```sh
python audit.py contatos.csv
python audit.py contatos.csv --key email
python audit.py contatos.csv --encoding latin-1
```

O relatório sai em JSON no terminal. Linhas duplicadas e malformadas são listadas pelos números físicos aproximados do CSV (para campos com quebras de linha, o número corresponde ao registro, não à linha física). O padrão usa todas as colunas como chave; `--key` compara apenas uma coluna. Espaços em torno de valores contam na identidade de duplicatas, enquanto campos só com espaços são considerados vazios. A primeira linha deve conter cabeçalhos únicos e não vazios.

## Testes

```sh
python -m unittest discover -s tests -v
```

## Limite

O programa guarda as chaves já vistas em memória. Arquivos enormes podem exigir uma estratégia baseada em disco ou leitura particionada.
