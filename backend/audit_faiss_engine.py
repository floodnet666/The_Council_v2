"""
Script de Auditoria Sênior para Recuperação Vetorial FAISS.
Este script executa uma bateria de 25 testes de complexidade progressiva
diretamente contra o MemoryEngine, isolando a camada de agentes e LLMs.
O objetivo é salvar todos os logs, sucessos, e stack traces de erros
em um arquivo Markdown para análise humana posterior.
"""

import os
import time
import traceback
from datetime import datetime
from engines.memory_engine import memory_engine

# As 25 perguntas de teste cobrindo todos os Tiers de complexidade
AUDIT_QUESTIONS = [
    # Tier 1: BI Básico
    "Qual o faturamento total acumulado em toda a base de dados?",
    "Quantos itens foram vendidos no total ao longo de todo o período?",
    "Qual o ticket médio geral dos pedidos realizados?",
    "Quais os 5 produtos mais vendidos em termos de volume físico?",
    "Qual a categoria de produtos com o melhor desempenho de vendas?",
    "Existe algum produto na base que não vendeu absolutamente nada no último mês?",
    
    # Tier 2: Análise Temporal
    "Qual a taxa de crescimento mensal (Month-over-Month) do faturamento?",
    "Qual a taxa de crescimento anual (Year-over-Year) consolidada?",
    "Qual a tendência da média móvel de 3 meses para as vendas globais?",
    "Quais meses do ano, historicamente, apresentam o pior desempenho de receita?",
    "Qual a evolução diária das vendas ao longo do último mês fechado?",
    "Agrupe as vendas pela safra (mês da primeira venda do produto) e mostre o volume.",
    "Qual safra de produtos teve o maior retorno financeiro no primeiro ano de lançamento?",
    
    # Tier 3: Estatística
    "Qual o desvio padrão das vendas diárias para avaliar a volatilidade?",
    "Qual o percentil 90 das vendas totais?",
    "Identifique dias específicos com vendas anômalas (Outliers) usando o método IQR.",
    "Qual a mediana absoluta das vendas por categoria?",
    "Calcule o Z-Score das vendas para normalização estatística.",
    "Qual a relação (correlação) entre o número de vendas e o valor unitário dos produtos?",
    "Gere um resumo estatístico completo (describe) de todas as colunas numéricas disponíveis.",
    
    # Tier 4: ML e Simulações
    "Simulação de Monte Carlo para projeção de faturamento futuro.",
    "Probabilidade empírica de vender mais de 1000 unidades amanhã.",
    "Regressão linear simples para identificar a tendência de crescimento das vendas.",
    "Simule um cenário financeiro pessimista com queda de 20% nas vendas totais.",
    "Faça um forecast ingênuo (Naive Forecast) projetando os resultados para o próximo mês."
]

OUTPUT_FILE = "faiss_audit_report.md"

def generate_markdown_header():
    """Gera o cabeçalho do relatório Markdown."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"""# 📊 Relatório de Auditoria Sênior: Motor FAISS (MemoryEngine)
**Data de Execução:** {timestamp}
**Total de Casos de Teste:** {len(AUDIT_QUESTIONS)}
**Objetivo:** Validar a integridade dos embeddings, a ausência de incompatibilidade de dimensões (dimension mismatch) e a qualidade do código Polars 'Gold Standard' armazenado na base de conhecimento legada.

---

## 📈 Resumo Executivo
*Este espaço é reservado para a análise do Engenheiro Sênior.*

---

## 🧪 Detalhamento dos Testes Vetoriais

"""
    return header

def run_audit():
    print(f"[INFO] Iniciando Auditoria FAISS com {len(AUDIT_QUESTIONS)} perguntas...")
    print(f"[INFO] O relatório será salvo em: {OUTPUT_FILE}")
    
    markdown_content = generate_markdown_header()
    
    success_count = 0
    error_count = 0
    empty_count = 0
    
    start_total_time = time.time()
    
    for i, question in enumerate(AUDIT_QUESTIONS, 1):
        print(f"\nProcessando [{i}/{len(AUDIT_QUESTIONS)}]: {question[:50]}...")
        
        markdown_content += f"### Teste {i}: `{question}`\n\n"
        
        start_query_time = time.time()
        try:
            # Requisitando os top 2 resultados mais relevantes (k=2)
            results = memory_engine.search(question, k=2)
            query_time = time.time() - start_query_time
            
            markdown_content += "- **Status de Execução:** ✅ SUCESSO\n"
            markdown_content += f"- **Tempo de Busca:** {query_time:.4f} segundos\n"
            
            if not results:
                markdown_content += "- **Aviso:** ⚠️ A busca não retornou nenhum erro, mas a lista de resultados está VAZIA. A base do FAISS pode não conter dados.\n\n"
                empty_count += 1
                continue
                
            markdown_content += f"- **Resultados Encontrados:** {len(results)}\n\n"
            
            success_count += 1
            
            for j, res in enumerate(results, 1):
                markdown_content += f"#### Resultado {j}\n"
                # Se o resultado for uma string, exibimos diretamente num bloco de código
                if isinstance(res, str):
                    markdown_content += f"```python\n{res}\n```\n\n"
                # Se for um objeto Document (Langchain), tentamos extrair o page_content e os metadados
                elif hasattr(res, 'page_content'):
                    markdown_content += f"**Metadados:** `{res.metadata}`\n\n"
                    markdown_content += f"**Conteúdo Recuperado:**\n```python\n{res.page_content}\n```\n\n"
                # Fallback genérico
                else:
                    markdown_content += f"```python\n{str(res)}\n```\n\n"
                    
        except Exception as e:
            error_count += 1
            query_time = time.time() - start_query_time
            error_trace = traceback.format_exc()
            
            print(f"[ERRO CRÍTICO] Falha no teste {i}. Verifique o relatório.")
            
            markdown_content += "- **Status de Execução:** ❌ FALHA CRÍTICA\n"
            markdown_content += f"- **Tempo até a Falha:** {query_time:.4f} segundos\n\n"
            markdown_content += "#### 🛑 Stack Trace do Erro\n"
            markdown_content += f"```text\n{error_trace}\n```\n\n"
            
            # Análise heurística do erro para ajudar no diagnóstico
            if "dimension" in str(e).lower() or "mismatch" in str(e).lower() or "shape" in str(e).lower():
                markdown_content += "> **💡 Diagnóstico Preliminar:** O erro sugere uma incompatibilidade de dimensões nos embeddings. O modelo usado para consultar (ex: Nomic 768d) diverge do modelo usado para popular o índice (ex: MiniLM 384d).\n\n"
            elif "not found" in str(e).lower() or "load" in str(e).lower() or "path" in str(e).lower():
                markdown_content += "> **💡 Diagnóstico Preliminar:** O arquivo do índice FAISS (`.bin`) ou os metadados não foram encontrados no caminho especificado pelo `MemoryEngine`.\n\n"

        markdown_content += "---\n\n"
        
    total_time = time.time() - start_total_time
    
    # Atualiza o resumo com as métricas finais
    summary = f"""
### 📊 Métricas de Execução da Auditoria
* **Tempo Total de Auditoria:** {total_time:.2f} segundos
* **Total de Testes:** {len(AUDIT_QUESTIONS)}
* **Testes Bem-Sucedidos (Dados Recuperados):** {success_count}
* **Testes Vazios (Sem Erro, Sem Dados):** {empty_count}
* **Testes com Erro Crítico (Exceptions):** {error_count}

"""
    # Inserindo o resumo logo após o cabeçalho (posição empírica)
    insert_pos = markdown_content.find("## 🧪 Detalhamento dos Testes Vetoriais")
    final_content = markdown_content[:insert_pos] + summary + markdown_content[insert_pos:]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print("\n[✅ AUDITORIA CONCLUÍDA]")
    print(f"- Sucessos: {success_count}")
    print(f"- Vazios: {empty_count}")
    print(f"- Erros: {error_count}")
    print(f"- Relatório salvo com sucesso em: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    run_audit()
