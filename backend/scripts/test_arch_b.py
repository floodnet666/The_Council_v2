import asyncio
import time
from langchain_ollama import ChatOllama
from langchain_experimental.tools import PythonREPLTool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

async def run_test_b():
    print("=== INICIANDO TESTE B: LLM AUTÔNOMA COM PYTHON REPL ===")
    start_time = time.time()
    
    llm = ChatOllama(model="hf.co/mradermacher/gemma-4-E2B-it-uncensored-GGUF:Q8_0", temperature=0.1)
    tools = [PythonREPLTool()]
    
    template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''
    
    prompt = PromptTemplate.from_template(template)
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5, handle_parsing_errors=True)
    
    instrucao = """
    Você é um Analista de BI Sênior. Você precisa usar o terminal Python para carregar o arquivo 'uploads/vendas_complexas_100k.csv' usando 'polars'.
    Primeiro, crie uma coluna chamada 'lucro_estimado' que é a subtração (valor_bruto - valor_desconto - valor_frete).
    Faça o código Python necessário para calcular a correlação exata de Pearson entre 'valor_bruto', 'valor_desconto' e 'lucro_estimado'.
    Depois que você conseguir imprimir a correlação via código e ler no console, escreva sua resposta final:
    A correlação aponta que vender mais (dar desconto) gera lucro de forma causal, ou estamos apenas destruindo margem? Aponte hipóteses.
    """
    
    print("\n[LLM] Agente ReAct instanciado. Iniciando loop de ferramentas (Agent Executor)...")
    
    try:
        response = await asyncio.wait_for(agent_executor.ainvoke({"input": instrucao}), timeout=240)
        output = response["output"]
    except Exception as e:
        output = f"Erro/Timeout/Parsing Error no Agente B: {e}"
        
    res = f"=== RESUMO (TESTE B) ===\n{output}\n\n[METRICAS B] Tempo Total: {time.time() - start_time:.2f}s"
    print("Writing to results_b.txt...")
    with open("results_b.txt", "w", encoding="utf-8") as f:
        f.write(res)

if __name__ == "__main__":
    asyncio.run(run_test_b())
