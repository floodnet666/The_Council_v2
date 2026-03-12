PRD — The Council 2.0 (Sistema Autônomo
White‑Label de Inteligência Analítica)
1. Visão Geral
The Council 2.0 é um sistema autônomo de análise de dados, capaz de operar em múltiplos domínios,
múltiplos idiomas e múltiplos modelos LLM. O produto deve ser  white‑label, modular e facilmente
adaptável a diferentes bases de dados, diferentes fluxos analíticos e diferentes estilos visuais.
A nova versão deve preservar os pilares conceituais do The Council, mas reescrever sua arquitetura
para que seja:
Lazy‑load em todos os subsistemas (modelos, RAG, DataEngine, visualizações).
Multi‑modelo, com separação clara entre Router , Analyst, Designer e Librarian.
Multithread e paralela, sempre que possível.
Modular, com API limpa e camadas bem separadas.
Compatível com Faiss, garantindo reuso completo das bases de conhecimento existentes.
Internacionalizada: PT‑BR, EN, IT.
Visualmente consistente com o tema Dark‑Data.
O sistema mantém:
1.1 Pilares Conceituais do The Council
Os pilares conceituais definem a identidade imutável do produto e orientam todas as decisões de
arquitetura, UX e funcionamento.
Pilar 1 — Semântica como Orquestradora (LangGraph)
A inteligência do sistema não vem apenas dos modelos, mas do  workflow semântico que organiza
raciocínios, decisões e ferramentas. O LangGraph funciona como o "cérebro executivo", garantindo
coerência, controle e interpretabilidade.
Pilar 2 — Multi‑Agente como Ecologia de Papéis
Cada agente possui um papel cognitivo distinto (Router , Analyst, Designer , Librarian). Isso replica a
dinâmica de um conselho real: especialistas cooperam, discordam e complementam‑se.
Pilar 3 — RAG como Memória Contextual Viva
O sistema não se apoia apenas no modelo — ele consulta conhecimento estruturado e versionável. O
RAG é a "biblioteca viva" que garante precisão, reduz alucinações e amplia capacidade técnica.
Pilar 4 — Dados como Primeira Classe (Polars)
O  motor  de  dados  é  determinístico,  rápido  e  confiável.  O  LLM  interpreta,  mas  quem  executa
transformações reais é o Polars — garantindo performance e auditabilidade.
• 
• 
• 
• 
• 
• 
• 
1
Pilar 5 — Visual como Insight (Plotly + Dark‑Data)
Visualização não é enfeite: é ferramenta cognitiva. O tema Dark‑Data facilita leitura, foco e contraste,
enquanto Plotly gera gráficos claros, técnicos e auditáveis.
Pilar 6 — Lazy, Modular, Extensível
Nada  carrega  até  ser  necessário.  Cada  componente  é  substituível.  Modelos  podem  ser  trocados.
Agentes podem evoluir . O produto não é rígido — é adaptável por design.
Pilar 7 — White‑Label Profundo
A máquina é fixa, mas a identidade é variável. Cada cliente pode customizar aparência, narrativa e
agentes sem alterar o núcleo.
Workflow semântico com LangGraph.
Estratégia multi‑agente.
RAG como consultor contextual.
Polars como engine de dados.
Plotly como gerador de gráficos.
2. Objetivos e Métricas de Sucesso
2.1 Objetivos do Produto
Criar uma plataforma analítica autônoma capaz de dialogar com qualquer dataset enviado pelo
usuário.
Reduzir o tempo de inicialização de minutos para < 500 ms.
Permitir troca dinâmica de modelos LLM.
Minimizar alucinações via documentação contextual suportada por RAG.
Criar interface ágil e moderna com tema Dark‑Data.
2.2 Métricas de Sucesso
Boot < 500 ms.
Primeira resposta < 2s em modelo leve.
Resposta analítica complexa < 10s usando modelo avançado.
Redução de 90% do tempo de carregamento do RAG (graças ao Faiss).
Compatibilidade garantida com múltiplos datasets e schemas.
Suporte completo a PT‑BR, EN, IT.
3. Arquitetura Geral
3.1 Visão Macro
A arquitetura segue cinco camadas centrais:
Frontend (Dark‑Data UI) → Interação, chat, gráficos, relatórios.
• 
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
• 
• 
• 
• 
• 
• 
1. 
2
API Gateway (FastAPI ou equivalente) → Interface entre UI e backend.
Orquestrador Semântico (LangGraph) → Roteamento inteligente entre agentes.
Agentes Modulares (Router, Analyst, Designer, Librarian).
Engines Especializadas:
DataEngine (Polars)
VisualizationEngine (Plotly)
Faiss MemoryEngine (RAG)
3.2 Filosofia de Design
Nada é carregado até ser necessário.
Cada agente tem papel claro e independente.
O orquestrador decide, baseado em intenção, qual agente trabalhará.
O sistema deve suportar execução paralela de agentes quando possível.
O modelo grande deve ser carregado apenas se a tarefa exigir .
4. Multi‑Agente (Core Specification)
4.1 Router Agent
Função: detectar intenção, idioma e tipo de tarefa. Modelo recomendado: 1.5B–3B. Decisões:
Análise descritiva → Analyst
Criação de gráfico → Chart Designer
Consulta técnica → Librarian
Preparação de query → DataEngine
Correção linguística → Language Normalizer
4.2 Analyst Agent
Função: gerar raciocínio analítico, SQL, ML, insights. Modelo recomendado: ≥ 14B (ideal: Qwen3‑Coder
30B). Requisitos:
Executar SQLContext (Polars) via ferramentas.
Integrar dados com contexto RAG.
Gerar insights claros e estruturados.
Seguir idioma selecionado.
4.3 Chart Designer Agent
Função: traduzir pedidos de visualização em chart specs. Saída: JSON estruturado (Plotly). Modelo: 3B–
7B.
4.4 Librarian Agent (RAG)
Função: consultar Faiss para documentação, exemplos, sintaxe e padrões. Requisitos:
Executar busca em Faiss.
Retornar contexto filtrado e relevante.
Não reindexar nada.
2. 
3. 
4. 
5. 
6. 
7. 
8. 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
3
Latência < 3 ms.
5. Engines Internas
5.1 MemoryEngine (Faiss)
Substitui completamente o Chroma. Requisitos:
Carregar índice Faiss em < 50 ms.
Manter metadados externos.
Usar SentenceTransformer em modo lazy.
Métodos:
search(query, k)
embed(text)
5.2 DataEngine (Polars)
Regras:
LazyFrame sempre.
Derivações automáticas (ano, mês, dia, etc.).
Tipagem inferida + overrides do usuário.
Execução segura via SQLContext.
Amostragens limitadas para evitar travamento.
5.3 Visualization Engine (Plotly)
Converte chart specs em gráficos.
Independente do agente.
Exporta imagens estáticas para relatórios.
6. Workflow Semântico (LangGraph)
Fluxo típico
Usuário envia pergunta.
Router detecta idioma, intenção e rota.
Librarian opcionalmente enriquece contexto.
Analyst decide ferramenta → SQL, ML, Chart, RAG.
ToolNode executa operação.
ChartDesigner gera visualização (se aplicável).
Resposta é construída e devolvida ao usuário.
Estados necessários
messages
language
dataset_schema
last_dataframe
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
6. 
7. 
• 
• 
• 
• 
4
chart_config
rag_context
7. Internacionalização (PT‑BR, EN, IT)
Regras obrigatórias
Toda resposta deve seguir o idioma selecionado.
Router detecta idioma da entrada.
Analyst e Designer recebem variável {LANGUAGE} no prompt.
UI troca textos automaticamente.
8. Lazy‑Loading e Performance
Carregar APENAS quando necessário
Encoder RAG → na primeira busca.
Modelo grande → primeira ação analítica complexa.
DataEngine → carregado apenas após seleção de dataset.
Plotly → somente quando gerar visual.
Multithread
Pré‑cálculo de estatísticas do dataset.
Carregamento paralelo de fontes.
Buscas RAG independentes.
9. Frontend (Dark‑Data Theme)
Características
Tema black‑glass / minimalista.
Gráficos com alto contraste.
Componentes reativos.
Carregamento instantâneo.
UX universal: PT‑BR, EN, IT.
Possíveis stacks
Next.js + API Gateway (FastAPI)
Streamlit (versão refinada)
Reflex (Python → Web)
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
5
10. White‑Label Requirements
Elementos substituíveis
Logo
Cores
Fonte
Nome dos agentes
Conteúdo didático
Arquitetura visual
Elementos fixos
Engine analítica (Polars)
Workflow semântico LangGraph
Multi‑Agente
Faiss RAG
11. Estrutura de Arquivos Recomendada
/ council
  /frontend
  /api
  /agents
  /workflow
  /core
    memory_engine_faiss.py
    data_engine.py
    visualization.py
  /models
  /knowledge_base
12. Requisitos Não‑Funcionais
Boot < 500 ms
UI responsiva
Modularidade máxima
Baixo acoplamento
Execução segura de SQL/ML
Compatibilidade com modelos locais (Ollama)
Deploy local ou on‑premise
13. Riscos e Mitigações
Modelo grande lento → Router + lazy loading.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
6
Dataset muito pesado → Polars LazyFrame + amostragem.
RAG desatualizado → Faiss reindex manual.
Idioma incorreto → variável LANGUAGE obrigatória no prompt.
14. Conclusão
The Council 2.0 mantém sua alma: um sistema multi‑agente, contextual, analítico e elegante.
A nova arquitetura garante velocidade, modularidade e uma experiência limpa tanto para o usuário
final quanto para quem deseja personalizar o produto.
Este PRD é a base para desenvolvimento, testes e extensões futuras.
15. Subgrafo de Relatórios (PDF Executive Report Subgraph)
A geração de PDF não é um processo de copiar respostas do chat. Trata‑se de um subgrafo autônomo,
composto  por  agentes  especializados  que  analisam  a  sessão,  sintetizam  insights  e  produzem  um
relatório executivo coerente, contextual e orientado ao tipo de análise solicitado pelo usuário.
Esse  subgrafo  deve  ser  suficientemente  desacoplado  do  fluxo  principal  para  permitir  evolução
independente, mas integrado ao estado global do LangGraph.
15.1 Objetivo do Subgrafo
Criar um relatório executivo capaz de:
Interpretar as perguntas do usuário como sinalizadores do tipo de raciocínio esperado.
Identificar padrões, tendências, anomalias e insights nos dados utilizados durante a sessão.
Estruturar uma narrativa executiva coerente, adaptada ao idioma do usuário.
Complementar ou expandir análises que não foram exploradas explicitamente na conversa.
Gerar gráficos adicionais se necessários para comunicar padrões.
O relatório é, portanto, uma análise autônoma, e não um histórico formatado.
15.2 Arquitetura do Subgrafo de Relatórios
O subgrafo é composto por três agentes principais:
A) Report Planner Agent
Função:
Ler toda a sessão (mensagens, ferramentas, gráficos gerados).
Analisar as perguntas do usuário para determinar o tipo de relatório (tendência, performance,
diagnóstico, comparação, previsão etc.).
Criar uma estrutura executiva contendo:
Objetivo analítico
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
7
Métricas-chave
Hipóteses
Tópicos principais
Gráficos necessários
Seções obrigatórias
B) Report Analyst Agent
Função:
Executar análises adicionais usando o DataEngine (Polars) quando necessário.
Validar padrões apontados pelo Planner .
Enriquecer com insights estatísticos reais.
Gerar novos chart_specs quando úteis.
Consolidar informações em linguagem executiva.
Esse agente funciona como um Analyst especializado em síntese de alto nível.
C) Report Synthesizer Agent
Função:
Escrever a versão final do relatório executivo.
Seguir o idioma selecionado (PT‑BR, EN, IT).
Integrar texto + gráficos + tabelas.
Gerar seções como:
Resumo Executivo
Situação Atual
Principais Insights
Riscos / Anomalias
Oportunidades
Recomendações
Saída: documento estruturado pronto para renderização.
15.3 Estados e Artefatos do Subgrafo
O LangGraph deve possuir estados adicionais:
report_requested: bool
report_plan: dict
report_insights: list
report_charts: list
report_final_text: str
report_assets: list (PNGs de gráficos)
pdf_path: str
O subgrafo só deve ser executado quando report_requested == True.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
8
15.4 Fluxo Completo do Subgrafo
Usuário solicita relatório (manual ou gatilho automático).
Estado é atualizado: report_requested = True.
Report Planner analisa o histórico e as perguntas do usuário → gera plano.
Report Analyst executa análises complementares e cria/valida gráficos.
Report Synthesizer escreve narrativa final + integra assets.
Engine de PDF converte texto e imagens em documento final.
Caminho do arquivo é salvo em pdf_path.
Frontend oferece download.
15.5 Requisitos do Relatório Executivo
O relatório deve obrigatoriamente:
Ser adaptado ao idioma do usuário.
Ser orientado às perguntas originais.
Destacar padrões, tendências e anomalias.
Gerar insights que não dependem exclusivamente das respostas do chat.
Ser reutilizável em ambiente corporativo.
Ser imprimível.
Suportar personalização visual (white‑label).
15.6 Engine de PDF (Render Layer)
A engine deve:
Receber report_final_text + report_assets.
Renderizar usando FPDF2, ReportLab ou WeasyPrint.
Suportar cabeçalhos e rodapés customizáveis.
Exportar PDF em < 5 segundos.
A geração continua lazy, mas agora depende do subgrafo dedicado.
15.7 Conclusão da Seção
A funcionalidade de relatório passa a ser um módulo autônomo, com lógica própria, agentes próprios
e  papel  estratégico  no  produto.  Essa  abordagem  maximiza  escalabilidade,  qualidade  da  análise  e
aderência a cenários corporativos, onde relatórios executivos são exigência crítica.
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
9
15.8 Diagrama do Subgrafo de Relatórios (Mermaid)
flowchart TD
    U[Usuário solicita relatório] --> RQ[report_requested = True]
    RQ --> RP[Report Planner]
    RP -->|Plano estrutural| RA[Report Analyst]
    RA -->|Insights + Charts| RS[Report Synthesizer]
    RS -->|Narrativa completa| PDF[PDF Engine]
    PDF --> OUT[PDF final disponível para download]
stateDiagram-v2
    [*] --> Planner
    Planner --> Analyst: plano criado
    Analyst --> Analyst: análises adicionais / gráficos
    Analyst --> Synthesizer: insights consolidados
    Synthesizer --> PDF_Render: narrativa final
    PDF_Render --> [*]
15.9 Descrição dos Prompts dos Agentes do Subgrafo
Report Planner Agent — Prompt Specification
Objetivo: transformar toda a sessão + perguntas do usuário em um blueprint de relatório executivo.
Elementos obrigatórios do prompt:
Leia todas as perguntas do usuário e identifique o modus analítico predominante.
Extraia temas recorrentes (ex.: tendência, comparação, sazonalidade, diagnóstico).
Defina seções do relatório:
Objetivo analítico
Contexto
Hipóteses
Métricas-chave
Gráficos necessários
Riscos e oportunidades
Gere plano em JSON estruturado.
Siga o idioma {LANGUAGE}.
Report Analyst Agent — Prompt Specification
Objetivo: executar análises adicionais e gerar insights.
Elementos obrigatórios:
Com base no plano do Planner , execute operações Polars necessárias.
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
10
Descubra padrões não mencionados explicitamente.
Proponha novos gráficos.
Gere "insights executivos" e não apenas descrição técnica.
Respeite limites de amostragem.
Siga idioma {LANGUAGE}.
Report Synthesizer Agent — Prompt Specification
Objetivo: escrever relatório executivo final.
Elementos obrigatórios:
Criar narrativa clara, concisa e em tom corporativo.
Estruturar:
Resumo Executivo
Achados Principais
Interpretação dos Gráficos
Riscos / Anomalias
Oportunidades
Recomendações
Adicionar coerência entre texto e gráficos.
Adaptar vocabulário ao idioma {LANGUAGE}.
15.10 Regras de Escalonamento Multi‑Modelo no Subgrafo
A escolha do modelo deve seguir lógica de custo-benefício:
1. Report Planner → Modelo leve (1.5B–3B)
Tarefas: classificação, estruturação, leitura geral.
Justificativa: não requer raciocínio profundo.
2. Report Analyst → Modelo intermediário ou avançado (7B–30B)
Se o dataset for pequeno → 7B.
Se houver operações analíticas complexas → 14B–30B.
Justificativa: análises precisam de precisão.
3. Report Synthesizer → 3B–7B
Narrativa não exige razor-sharp reasoning.
Mas precisa de boa coerência e estilo.
Fallback automático:
Se  qualquer  agente  detectar  baixa  confiança  no  output,  deve  solicitar  reforço  do  modelo
imediatamente superior .
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
11
15.11 Integração do Subgrafo com o Estado Global do LangGraph
Estados adicionados no GraphState:
report_requested: bool
report_plan: dict
report_insights: list
report_charts: list
report_final_text: str
report_assets: list
pdf_path: str
Regras de Integridade:
Subgrafo só inicia se report_requested == True.
O fluxo principal pausa até o subgrafo terminar .
O estado é atualizado incrementalmente por cada agente.
O pdf_path final deve ser persistido para o frontend.
Movimentação do Estado:
flowchart LR
    S0((State)) --> Planner
    Planner -->|update: report_plan| S1((State))
    S1 --> Analyst
    Analyst -->|update: report_insights, report_charts| S2((State))
    S2 --> Synthesizer
    Synthesizer -->|update: report_final_text| S3((State))
    S3 --> PDF_Engine
    PDF_Engine -->|update: pdf_path| S4((State))
15.12 Formato Final do PDF (Template White‑Label)
Estrutura recomendada:
Capa (white‑label)
Logo do cliente
Título customizável
Data
Resumo Executivo
3–5 insights principais
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
6. 
12
Contexto da Análise
Perguntas originais do usuário
Descrição do dataset
Seções Analíticas
Tendências
Distribuições
Correlações
Segmentações
Padrões temporais
Gráficos (Plotly → PNG)
Inclusão modular
Legendas adaptadas ao idioma
Riscos / Anomalias / Outliers
Oportunidades & Recomendações
Apêndice Técnico (opcional)
Queries SQL geradas
Operações Polars usadas
Rodapé padrão do cliente
Nome
Website
Contatos
Estilo visual:
Tema Dark‑Data com acentos azul/indigo.
Tipografia: Inter / JetBrains Mono.
Margens amplas e alta legibilidade.
7. 
8. 
9. 
10. 
11. 
12. 
13. 
14. 
15. 
16. 
17. 
18. 
19. 
20. 
21. 
22. 
23. 
24. 
25. 
26. 
27. 
• 
• 
• 
13
15.13 Conclusão Final do Subgrafo
Este subgrafo transforma The Council em um sistema corporativo completo, capaz de não apenas
responder perguntas, mas sintetizar pensamento analítico estruturado, gerando relatórios de nível
executivo que podem ser apresentados diretamente a diretoria ou stakeholders externos.
14
