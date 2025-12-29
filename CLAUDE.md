# Virtual Network Resource Allocator using Decision Trees

**Author:** Luis Antonio Momm Duarte

**Goal:** Use decision trees to select the best Virtual Network Embedding (VNE) algorithm for each request, optimizing acceptance rate and solution time.

--- original paper starts here --- 

---
We adopt two topologies, GEANT (40 nodes and 61 links)
and WX100 (100 nodes and 500 links) [Waxman, 1988], as
physical networks. See Appendix E.1 for these topologies’
descriptions. The multiple-type resources (i.e., CPU, storage,
GPU) of physical nodes and bandwidth resources of physical
links are uniformly generated within the range of [50, 100]
units. In each simulation run, we randomly generate 1000
VNRs with varying sizes ranging from 2 to 10. The virtual
nodes within each VNR are randomly interconnected with a
probability of 50%. Additionally, resource demands of each
VNR’s node and link requirements are uniformly generated
within the range of [0, 20] and [0, 50] units, respectively. The
lifetime of each VNR is exponentially distributed with an average of 500 time units. The arrival of these VNRs follows
a Poisson process with an average rate η, wherein η VNRs
are received per unit of time. In subsequent experiments, we
first train models with η = 0.001 on GEANT and η = 0.08
on WX100, due to their different capacities of physical resources. Then we manipulate the value of η to emulate network systems with different traffic throughputs and infer with
trained models to study the sensitivity of algorithms.
Implementations. During training, we first conduct metalearning in the initial 20 simulations and then focus on finetuning in the subsequent 10 simulations. We set the policy entropy threshold δ to 2. We implement neural network models
with PyTorch and decide reasonable values for hyperparameters following the guide of related studies [Huang et al., 2022;
Zhou et al., 2023; Wang et al., 2021a; He et al., 2023a;
Kingma and Ba, 2014; Joshi et al., 2022]. See Appendix E.2
for hyperparameter settings on neural networks and meta-RL.O

--- original paper ends here --- 


## Step-by-Step Implementation




### Step 1: Data Generation
- Run ~8 different ViRNE algorithms (heuristic, exact, meta-heuristic) on the two topologies above
- Vary topology parameters, resource distributions, and workload characteristics
- Collect metrics for each algorithm:
  - Acceptance rate (% of accepted requests)
  - Solution time (time to embed the virtual network)
- Save results to CSV files
- Use multiple random seeds for statistical significance
- > what I want as final objective is the tree select the best algo for the current state (PN and VN). How can i do this? with this rperesentation i think its just best to select the 
winner who is overrepresented. what can I do?









The pipeline to generate the pipeline is the /machine_learning/pipeline

---

## 📝 Diretrizes para Escrita Acadêmica

As seguintes orientações devem ser seguidas ao escrever ou revisar documentos acadêmicos (artigos, papers, dissertações, etc.):

### Regras Fundamentais

1. **Terceira Pessoa Impessoal**: O trabalho deve ser escrito em terceira pessoa, de modo técnico/formal e impessoal. Evitar "nós", "apresentamos", "nosso".

2. **Método Científico**: Sempre estudar, escrever, raciocinar e produzir usando métodos científicos.

3. **Qualidade Bibliográfica**: Cuide da qualidade e atualidade do material bibliográfico. Artigos científicos de revistas bem conceituadas são os mais indicados.

4. **Termos em Português**: Procurar sempre utilizar termos técnicos em português, quando houverem.
   - Recursos: http://www.ime.usp.br/~kon/ResearchStudents/traducao.html
   - http://wiki.inf.ufpr.br/maziero/doku.php?id=so:termos_de_so_em_portugues

### Estrutura e Coesão

5. **Prazos e Cronograma**: Você é responsável pelo cumprimento dos prazos/cronograma.

6. **Didática**: O óbvio deve ser dito e SEJA DIDÁTICO. Você está escrevendo para outras pessoas que irão ler seu trabalho.

7. **Referenciação**: Fazer a referenciação de acordo com a norma da sua universidade.

8. **Falta de Referenciação (CRÍTICO)**: Para apresentar algo em texto científico, é necessário:
   - Fazer a comprovação científica (parágrafo anterior com base teórica), ou
   - Fundamentar em parágrafo/texto referenciado por alguém que o fez ou o afirmou.

9. **Contextualização**: Pequeno texto que situa o leitor no contexto do assunto. Não é descrição do conteúdo.

10. **Contextualização de Subseções**: Adicionar texto que situa o leitor no contexto dos assuntos nas subseções subsequentes.

11. **Parágrafo de Uma Frase (EVITAR)**: Um parágrafo com apenas uma frase enquadra-se em uma das seguintes situações:
    - Muito objetivo: descrever mais a ideia
    - Faz parte do parágrafo anterior/posterior: agrupar
    - Está perdido: excluir ou remodelar
    - Muito extenso: fazer pontuação adequada

12. **Falta de Ligação**: O texto deve possuir sentido lógico de evolução, não um amontoado de ideias.
    - Fazer ligação durante o decorrer do texto
    - Dedicar parágrafo no final de cada seção para essa finalidade

13. **Comentar com Suas Palavras**: Logo após uma citação direta, escrever com suas palavras o entendimento ou interpretação. Evitar texto que seja apenas coletânea de resumos.

### Siglas, Termos e Expressões

14. **Siglas e Termos Desconhecidos**: Quando utilizar termo que não seja de conhecimento comum, explicar:
    - Breve nota de rodapé, ou
    - Criar glossário e/ou lista de siglas, ou
    - Fazer a nota de rodapé E criar glossário (recomendado)

15. **Padronização de Termos**: Padronizar siglas, termos e expressões ao decorrer de todo o trabalho. Exemplo: usar sempre "datacenter" ou "data center", nunca alternar entre formas.

### Qualidade do Texto

16. **Texto Confuso**: Texto que não permite interpretação correta ou permite várias interpretações distintas.

17. **Texto Perdido**: Texto que não se encaixa na "história". Solução: ocultar e reler; se não fizer falta, excluir; se fizer falta, remodelar o texto periférico.

18. **Termos em Língua Estrangeira (IMPORTANTE)**: Devem estar em itálico. Exemplos: \textit{machine learning}, \textit{baseline}, \textit{online}, \textit{features}.

19. **Indicadores Geográficos (EVITAR)**: Não devem ser utilizados no texto (abaixo, acima, a seguir). Utilizar sempre numeração: "Seção~\ref{sec:X}", "Figura~\ref{fig:Y}".

20. **Transição Quebrada**: Dois parágrafos/subseções sem evolução satisfatória. Soluções:
    - Inserir mais texto para criar sequência evolutiva
    - Remodelar os textos discrepantes
    - Excluir a parte que não faz falta

### Citações

21. **Citações Diretas**: Empregar somente quando necessário deixar claro que a ideia não sofreu alteração. Use para questões polêmicas/contraditórias. Evitar para conceitos básicos.

22. **Fim de Seção (CRÍTICO)**: Nunca terminar uma seção/subseção com citações (texto ou figura). Indica falta de conclusão/explicação do material referido.

### Elementos Gráficos (Figuras, Tabelas, Quadros)

23. **Menção Antes da Apresentação**: Figuras, tabelas e quadros devem ser mencionados no texto ANTES de serem apresentados.

24. **Explicação Após Apresentação (CRÍTICO)**: Sempre que um elemento gráfico for apresentado, é necessário explicá-lo após sua apresentação.

25. **Referências Bibliográficas**: Sempre incluir as referências empregadas. O revisor identifica se discrepâncias são dos autores ou da fonte.

26. **Tópicos**: Um parágrafo em tópicos = conjunto de parágrafos de uma frase. Aplicar as mesmas medidas de correção do item #11.

### Vocabulário e Estilo

27. **Advérbios/Adjetivos de Intensidade**: Informar o que considera "grande", "melhor", "muito", etc. Esses adjetivos demandam mais explicações/justificativas.

28. **Termos Temporais (CUIDADO)**: Utilizar com cautela: "hoje em dia", "atualmente", "atual", "recentemente". Não é claro se refere à data de escrita ou das fontes.

29. **Múltiplas Fontes**: Nunca escrever baseando-se apenas em um autor/fonte. Usar mínimo duas fontes, preferindo literatura científica.

30. **Falta de Chamada ":"**: Ao apresentar itens, fazer texto de chamada que explique genericamente os itens que serão listados.

31. **"Vantagens e Desvantagens"**: Evitar esses termos. Uma vantagem é uma característica que interessa em um contexto específico. Descrever o contexto.

32. **Elementos Gráficos Referenciados**: Figuras/tabelas também devem ser referenciadas:
    - Sem alterações (Copy&Paste): referência na legenda
    - Com alterações (tradução, redesenho): "Adaptado de: [referência]"

33. **Apud**: Quando a fonte é de um autor que referencia outro:
    - Usar: \cite{autor-que-referencia apud autor-original}

### Formatação e Ortografia

34. **Formato**: Seguir normas da universidade (UDESC: https://www.udesc.br/arquivos/udesc/id_cpmenu/12510/MANUAL_2020_09_07_1599489825065_12510.pdf)

35. **Novo Acordo Ortográfico**: Escrever conforme o novo acordo ortográfico (válido desde 2016).

36. **"Demonstrar" em Exatas**: Refere-se a prova matemática ou método formal. Para outros casos, usar "exemplificar", "apresentar", etc.

37. **"Performance" em Textos Técnicos**: Em área de exatas, usar "desempenho" para indicadores/medições. "Performance" tem conotação artística.

38. **Tempo Verbal (IMPORTANTE)**:
    - Presente: para questões desenvolvidas/relatadas no texto
    - Futuro: para itens que NÃO estão descritos e SERÃO feitos
    - Futuro do pretérito: ação que não será realizada por outro fator ("seria", "faria")

39. **"Onde"**: Somente para localizações geográficas. Para partes de sistemas, usar: "no qual", "na qual", "nas quais", "localizado no", etc.

40. **Tempo Verbal Futuro do Pretérito**: Significa ação no futuro que não será realizada. Ex: "Eu revisaria o seu texto hoje, mas tenho o dia repleto de reuniões".

41. **Expressões em Inglês**: Revisar a sintaxe. Traduções literais podem não existir no inglês. Consultar guias de termos e expressões.

42. **Português Brasileiro**: Termos e palavras devem estar na língua portuguesa, segundo a definição brasileira. Consultar: http://www.academia.org.br/nossa-lingua/busca-no-vocabulario

43. **e.g. e i.e. (Correto)**: "e.g.," (exempli gratia = por exemplo) e "i.e.," (id est = isto é)
    - Referência: https://www.enago.com/academy/when-to-use-e-g-and-i-e-while-writing-your-paper/

44. **Pronomes Pessoais**: Usar "ele" ou "ela" somente para pessoas. Para sistemas/objetos, usar "este" ou "esta", etc.

45. **Iniciar Parágrafo (EVITAR)**: Não convém iniciar parágrafo com: E, Ou, Porém, Mas, Senão. Essas conjunções devem estar ligadas ao enunciado anterior.

46. **Números por Extenso vs Algarismos**: Consultar quando usar cada um em textos formais.
    - Referência: https://www.normaculta.com.br/escrever-numeros-por-extenso-ou-em-algarismos/

---

**Fonte**: Orientações baseadas nas práticas do Prof. Charles Christian Miers para orientação e avaliação de trabalhos acadêmicos.

**Observação**: Este é um conjunto de diretrizes, não "verdade absoluta". Diferentes professores e instituições podem ter variações em suas preferências.

