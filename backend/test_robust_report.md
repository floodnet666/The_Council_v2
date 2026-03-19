# Relatório de Teste Robusto (10 Perguntas)

**Total Perguntas:** 10
**Sucessos:** 2
**Erros:** 8

## Detalhes

### Q1: 1. Quantos registros totais existem no arquivo de vendas de bebidas?
- Status: erro_conexao
- Tempo: 302.08s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

### Q2: 2. Qual é o valor total de vendas ('Sale (Dollars)') gerado considerando todas as linhas?
- Status: erro_conexao
- Tempo: 302.09s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

### Q3: 3. Quantas vendas ocorreram na cidade de 'DES MOINES'?
- Status: sucesso
- Tempo: 44.08s
- Resposta: Sinto muito, a análise desta pergunta excedeu o limite de segurança de 42 segundos para evitar sobre...

### Q4: 4. Agrupe as vendas por 'City' e liste as 10 cidades que mais geraram faturamento em dólares.
- Status: erro_conexao
- Tempo: 302.05s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

### Q5: 5. Agrupe as vendas por 'Category Name' e me mostre o Top 5 de faturamento.
- Status: erro_conexao
- Tempo: 302.09s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

### Q6: 6. Qual condado ('County') tem a média mais cara de preço de varejo ('State Bottle Retail')?
- Status: erro_conexao
- Tempo: 302.06s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

### Q7: 7. Mostre as estatísticas descritivas (min, max, media) de 'Sale (Dollars)'.
- Status: sucesso
- Tempo: 44.1s
- Resposta: Sinto muito, a análise desta pergunta excedeu o limite de segurança de 42 segundos para evitar sobre...

### Q8: 8. Filtre vendas da cidade 'CEDAR RAPIDS' e identifique o produto ('Item Description') mais vendido (soma de garrafas).
- Status: erro_conexao
- Tempo: 302.06s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

### Q9: 9. Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas.
- Status: erro_conexao
- Tempo: 302.08s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

### Q10: 10. Qual fornecedor ('Vendor Name') vendeu a maior quantidade de garrafas no total ('Bottles Sold')?
- Status: erro_conexao
- Tempo: 302.08s
- Erro: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=300)

