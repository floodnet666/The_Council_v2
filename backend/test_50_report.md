# Relatório de Stress Test: The Council v2

**Total Perguntas:** 50
**Sucessos:** 30
**Erros:** 20
**Tempo Total Execução:** 267.21 segundos
**Duração Média por Pergunta:** 5.34 segundos

## Detalhamento

### Q26: 26. Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas.
- Status: sucesso
- Tempo: 37.06s
- Agente: system
- Resposta: Sinto muito, a análise desta pergunta excedeu o limite de segurança de 35 segundos para evitar sobrecarga do servidor.

### Q27: 27. Qual 'Vendor Name' tem a maior variedade de produtos únicos ('Item Number') ofertados?
- Status: sucesso
- Tempo: 37.06s
- Agente: system
- Resposta: Sinto muito, a análise desta pergunta excedeu o limite de segurança de 35 segundos para evitar sobrecarga do servidor.

### Q28: 28. Compare as vendas de Vodka e de Whiskey. Qual teve maior faturamento?
- Status: sucesso
- Tempo: 37.08s
- Agente: system
- Resposta: Sinto muito, a análise desta pergunta excedeu o limite de segurança de 35 segundos para evitar sobrecarga do servidor.

### Q29: 29. Qual é o percentual aproximado do faturamento total que pertence à cidade de 'DES MOINES'?
- Status: sucesso
- Tempo: 37.06s
- Agente: system
- Resposta: Sinto muito, a análise desta pergunta excedeu o limite de segurança de 35 segundos para evitar sobrecarga do servidor.

### Q30: 30. Existe alguma loja que comprou mais de 1000 garrafas em uma única transação?
- Status: sucesso
- Tempo: 37.08s
- Agente: system
- Resposta: Sinto muito, a análise desta pergunta excedeu o limite de segurança de 35 segundos para evitar sobrecarga do servidor.

### Q31: 31. Mostre as estatísticas descritivas (min, max, media) de 'Sale (Dollars)'.
- Status: erro_conexao
- Tempo: 4.07s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37D16D0>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q32: 32. Em média, qual é a diferença absoluta entre o preço de varejo da loja e o custo da garrafa?
- Status: erro_conexao
- Tempo: 4.1s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E5D50>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q33: 33. Filtre vendas da cidade 'CEDAR RAPIDS' e identifique o produto ('Item Description') mais vendido (soma de garrafas).
- Status: erro_conexao
- Tempo: 4.09s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E7FD0>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q34: 34. Agrupe por 'Store Name' e mostre quantas Lojas diferentes têm o mesmo nome. Quais os nomes mais comuns?
- Status: erro_conexao
- Tempo: 4.11s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37F2290>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q35: 35. Qual é o mês com o maior volume em Litros da história do dataset?
- Status: erro_conexao
- Tempo: 4.07s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E7110>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q36: 36. Qual é a variação percentual de vendas (faturamento) do primeiro semestre para o segundo semestre de 2015? Calcule dinamicamente.
- Status: erro_conexao
- Tempo: 4.12s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E5490>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q37: 37. Identifique os Top 3 fornecedores que têm o maior lucro projetado por litro vendido.
- Status: erro_conexao
- Tempo: 4.1s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E4790>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q38: 38. Para a cidade 'DES MOINES', como a média de preço de varejo varia ao longo dos meses do ano de 2012?
- Status: erro_conexao
- Tempo: 4.09s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37D1050>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q39: 39. Descubra qual conjunto Condado/Cidade concentra os maiores outliers de preço (acima do percentil 95 ou limite superior equivalente).
- Status: erro_conexao
- Tempo: 4.12s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37D6990>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q40: 40. Calcule a correlação entre o custo da garrafa e o número de garrafas vendidas. Há uma correlação linear obvia?
- Status: erro_conexao
- Tempo: 4.1s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37F1410>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q41: 41. Crie um rank das 5 categorias menos vendidas que ainda geraram algum faturamento positivo.
- Status: erro_conexao
- Tempo: 4.07s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37FC890>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q42: 42. Verifique se o somatório do 'Bottle Volume (ml)' vezes 'Bottles Sold' bate com o 'Volume Sold (Liters)' para as primeiras 10 transações.
- Status: erro_conexao
- Tempo: 4.11s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37723D0>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q43: 43. Quais os 2 meses do ano global onde geralmente as vendas despencam (menor soma de vendas históricas conjuntas)?
- Status: erro_conexao
- Tempo: 4.08s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37D1B50>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q44: 44. Liste o share do mercado (faturamento): descubra qual % a loja número 1 ocupa diante de todo o faturamento da base.
- Status: erro_conexao
- Tempo: 4.09s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37D7C10>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q45: 45. Execute um agrupamento com rolling window (média móvel mensal) do faturamento total global, se o duckdb/polars permitir, caso contrário apenas agregue mensal.
- Status: erro_conexao
- Tempo: 4.11s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37F3950>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q46: 46. Pode gerar um gráfico de barras com as 10 cidades que mais venderam garrafas?
- Status: erro_conexao
- Tempo: 4.1s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37F3410>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q47: 47. Eu quero um gráfico de pizza mostrando a proporção de vendas (em dólares) dos Top 5 Condados.
- Status: erro_conexao
- Tempo: 4.08s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E6650>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q48: 48. Crie um gráfico de linha do faturamento total ao longo dos anos-mês (ex: Jan/2012, Fev/2012).
- Status: erro_conexao
- Tempo: 4.09s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E7590>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q49: 49. Crie um gráfico de dispersão (scatter plot) cruzando o 'State Bottle Cost' (eixo X) e o 'State Bottle Retail' (eixo Y).
- Status: erro_conexao
- Tempo: 4.08s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E7AD0>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

### Q50: 50. Construa um gráfico de barras comparando as categorias de produto Top 8 que mais venderam garrafas totais.
- Status: erro_conexao
- Tempo: 4.09s
- Erro: HTTPConnectionPool(host='localhost', port=8001): Max retries exceeded with url: /chat (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x000002B9D37E5290>: Failed to establish a new connection: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione'))

