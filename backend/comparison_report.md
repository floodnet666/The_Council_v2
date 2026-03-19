# Relatório de Comparação Determinística

| ID | Pergunta | Status |
| --- | --- | --- |
| 1 | Quantos registros totais existem no arquivo de vendas de bebidas? | ❌ DIVERGE |
| 2 | Qual a data da venda mais antiga e da mais recente? | ❌ DIVERGE |
| 3 | Qual é o valor total de vendas ('Sale (Dollars)') gerado considerando todas as linhas? | ❌ DIVERGE |
| 4 | Liste os nomes de 5 lojas únicas diferentes encontradas neste dataset. | ❌ DIVERGE |
| 5 | Qual é o endereço e cidade da loja com 'Store Number' 2191? | ❌ DIVERGE |
| 6 | Quantos condados ('County') diferentes registraram vendas? | ❌ DIVERGE |
| 7 | Qual é a soma total do custo das garrafas ('State Bottle Cost')? | ❌ DIVERGE |
| 8 | Quantos litros totais ('Volume Sold (Liters)') foram vendidos? | ❌ DIVERGE |
| 9 | Retorne as 5 primeiras linhas da tabela para eu ver os dados. | ❌ DIVERGE |
| 10 | Qual é a descrição do item ('Item Description') mais frequente ou primeiro da lista? | ❌ DIVERGE |
| 11 | Qual o total de itens vendidos onde a categoria é 'Vodka' ou similar? | ❌ DIVERGE |
| 12 | Quantas vendas ocorreram na cidade de 'DES MOINES'? | ❌ DIVERGE |
| 13 | Qual é a média do volume das garrafas em mililitros ('Bottle Volume (ml)')? | ❌ DIVERGE |
| 14 | Quantas vendas tem a loja de nome 'Hy-Vee' apenas na cidade 'WATERLOO'? | ❌ DIVERGE |
| 15 | Qual é o nome do fornecedor ('Vendor Name') associado ao 'Vendor Number' 260? | ❌ DIVERGE |
| 16 | Agrupe as vendas por 'City' e liste as 10 cidades que mais geraram faturamento em dólares. | ❌ DIVERGE |
| 17 | Qual fornecedor ('Vendor Name') vendeu a maior quantidade de garrafas no total ('Bottles Sold')? | ❌ DIVERGE |
| 18 | Qual é a loja ('Store Name') com o maior volume vendido em galões ('Volume Sold (Gallons)')? | ❌ DIVERGE |
| 19 | Agrupe as vendas por 'Category Name' e me mostre o Top 5 de faturamento. | ❌ DIVERGE |
| 20 | Qual condado ('County') tem a média mais cara de preço de varejo ('State Bottle Retail')? | ❌ DIVERGE |
| 21 | Em qual mês e ano ocorreram o maior número de transações separadas na base? | ❌ DIVERGE |
| 22 | Gere uma tabela listando a 'City' e sua soma total de litros vendidos, apenas para garrafas com volume > 1000ml. | ❌ DIVERGE |
| 23 | Liste as 3 lojas com o maior lucro absoluto estimado (Venda total menos Custo de garrafa x garrafas vendidas). | ❌ DIVERGE |
| 24 | Qual cidade tem o menor faturamento médio por registro de venda? | ❌ DIVERGE |
| 25 | Conte o número de vendas para cada dia da semana (segunda a domingo). | ❌ DIVERGE |
| 26 | Filtre as vendas que ocorreram depois de 01/01/2015 e grupe por categoria, sumando o número de garrafas. | ❌ DIVERGE |
| 27 | Qual 'Vendor Name' tem a maior variedade de produtos únicos ('Item Number') ofertados? | ❌ DIVERGE |
| 28 | Compare as vendas de Vodka e de Whiskey. Qual teve maior faturamento? | ❌ DIVERGE |
| 29 | Qual é o percentual aproximado do faturamento total que pertence à cidade de 'DES MOINES'? | ❌ DIVERGE |
| 30 | Existe alguma loja que comprou mais de 1000 garrafas em uma única transação? | ❌ DIVERGE |
| 31 | Mostre as estatísticas descritivas (min, max, media) de 'Sale (Dollars)'. | ❌ DIVERGE |
| 32 | Em média, qual é a diferença absoluta entre o preço de varejo da loja e o custo da garrafa? | ❌ DIVERGE |
| 33 | Filtre vendas da cidade 'CEDAR RAPIDS' e identifique o produto ('Item Description') mais vendido (soma de garrafas). | ❌ DIVERGE |
| 34 | Agrupe por 'Store Name' e mostre quantas Lojas diferentes têm o mesmo nome. Quais os nomes mais comuns? | ❌ DIVERGE |
| 35 | Qual é o mês com o maior volume em Litros da história do dataset? | ❌ DIVERGE |
| 36 | Qual é a variação percentual de vendas (faturamento) do primeiro semestre para o segundo semestre de 2015? Calcule dinamicamente. | ❌ DIVERGE |
| 37 | Identifique os Top 3 fornecedores que têm o maior lucro projetado por litro vendido. | ❌ DIVERGE |
| 38 | Para a cidade 'DES MOINES', como a média de preço de varejo varia ao longo dos meses do ano de 2012? | ❌ DIVERGE |
| 39 | Descubra qual conjunto Condado/Cidade concentra os maiores outliers de preço (acima do percentil 95 ou limite superior equivalente). | ❌ DIVERGE |
| 40 | Calcule a correlação entre o custo da garrafa e o número de garrafas vendidas. Há uma correlação linear obvia? | ❌ DIVERGE |
| 41 | Crie um rank das 5 categorias menos vendidas que ainda geraram algum faturamento positivo. | ❌ DIVERGE |
| 42 | Verifique se o somatório do 'Bottle Volume (ml)' vezes 'Bottles Sold' bate com o 'Volume Sold (Liters)' para as primeiras 10 transações. | ❌ DIVERGE |
| 43 | Quais os 2 meses do ano global onde geralmente as vendas despencam (menor soma de vendas históricas conjuntas)? | ❌ DIVERGE |
| 44 | Liste le share do mercado (faturamento): descubra qual % a loja número 1 ocupa diante de todo o faturamento da base. | ❌ DIVERGE |
| 45 | Execute um agrupamento com rolling window (média móvel mensal) do faturamento total global, se o duckdb/polars permitir, caso contrário apenas agregue mensal. | ❌ DIVERGE |
| 46 | Gere um gráfico de barras com as 10 cidades que mais venderam garrafas? | ❌ DIVERGE |
| 47 | Eu quero um gráfico de pizza mostrando a proporção de vendas (em dólares) dos Top 5 Condados. | ❌ DIVERGE |
| 48 | Crie um gráfico de linha do faturamento total ao longo dos anos-mês (ex: Jan/2012, Fev/2012). | ❌ DIVERGE |
| 49 | Crie um gráfico de dispersão (scatter plot) cruzando o 'State Bottle Cost' (eixo X) e o 'State Bottle Retail' (eixo Y). | ❌ DIVERGE |
| 50 | Construa um gráfico de barras comparando as categorias de produto Top 8 que mais venderam garrafas totais. | ❌ DIVERGE |
