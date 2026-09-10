# Telegram Store + PlusPix
Loja Telegram de produtos digitais fictícios com catálogo, estoque, saldo, Gift Cards e consulta de pagamentos PlusPix.

## Instalação
`pip install -r requirements.txt`
`python bot.py`

Configure no Railway ou `.env`: BOT_TOKEN, ADMIN_ID, PLUSPIX_CLIENT_ID, PLUSPIX_CLIENT_SECRET.

Nunca publique segredos no GitHub.

Formato de estoque:
`IDENTIFICADOR_12_16|CODIGO_5|CODIGO_3_4|NOME_FICTICIO|NUMERO_10|VALOR`

Exemplo:
`12345678901234|A7K92|7391|TESTE FULANO CICRANO|0000000000|49.90`
