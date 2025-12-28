# Regras de Escrita Acadêmica em Português

## Guia de Boas Práticas para Artigos Científicos em Computação

Este documento contém as diretrizes de escrita acadêmica para produção de artigos, dissertações e teses na área de Ciência da Computação, baseadas nas orientações do Prof. Charles Christian Miers.

---

## 1. Linguagem e Tom

### 1.1 Pessoa do Discurso
- **Use sempre a terceira pessoa** (impessoal)
- Evite: "nós implementamos", "desenvolvemos", "propomos"
- Prefira: "foi implementado", "é desenvolvido", "é proposto"
- Artigos científicos em computação geralmente seguem estilo impessoal

### 1.2 Formalidade
- Use linguagem técnica e formal
- Evite coloquialismos e expressões informais
- Mantenha tom objetivo e científico

---

## 2. Termos Estrangeiros

### 2.1 Itálico Obrigatório
- **Todos os termos em língua estrangeira devem estar em itálico**
- Exemplos:
  - `\textit{Virtual Network Embedding}`
  - `\textit{Machine Learning}`
  - `\textit{XGBoost}`
  - `\textit{features}`
  - `\textit{baseline}`
  - `\textit{trade-off}`
  - `\textit{overhead}`
  - `\textit{framework}`
  - `\textit{ensemble}`
  - `\textit{dataset}`
  - `\textit{Grid Search}`
  - `\textit{F1-score}`

### 2.2 Exceções
- Siglas amplamente conhecidas: CPU, RAM, GPU (não precisam itálico)
- Termos que já foram incorporados ao português técnico de forma padronizada

---

## 3. Terminologia Técnica

### 3.1 Traduções Preferenciais
- **"performance" → "desempenho"** (sempre use o termo em português)
- "training" → "treinamento" (não "treino")
- "test" → "teste"
- "validation" → "validação"

### 3.2 Quando Usar Original em Inglês
- Quando o termo é consagrado internacionalmente
- Quando não há tradução adequada em português
- Quando a tradução pode causar ambiguidade
- **Sempre em itálico quando mantido em inglês**

---

## 4. Números e Quantidades

### 4.1 Números Pequenos (0-10)
- **Escreva por extenso em texto corrido**
- Exemplos:
  - "sete algoritmos"
  - "duas topologias"
  - "três métricas"
  - "quatro dos seis casos"

### 4.2 Números Grandes
- Use algarismos para números > 10
- Use palavras para milhares, milhões: "oito mil", "dois milhões"
- Em tabelas e gráficos: sempre use algarismos

### 4.3 Porcentagens e Medidas
- Sempre use algarismos: "93,33%", "5,63s", "16GB"
- Use vírgula como separador decimal (padrão brasileiro)

---

## 5. Referências Cruzadas

### 5.1 Uso do Til (~)
- **Sempre use `~` antes de `\ref{}`** para evitar quebra de linha
- Exemplos corretos:
  - `a Figura~\ref{fig:exemplo}`
  - `a Tabela~\ref{tab:resultados}`
  - `a Seção~\ref{sec:metodologia}`
  - `o Algoritmo~\ref{alg:xgboost}`

### 5.2 Artigos e Preposições
- "a Figura", "a Tabela", "a Seção" (com artigo feminino)
- "o Algoritmo", "o Teorema" (com artigo masculino)
- Primeira letra maiúscula: Figura, Tabela, Seção, etc.

### 5.3 Evitar Indicadores Vagos
- ❌ Evite: "a figura abaixo", "como mostrado acima"
- ✅ Use: "a Figura~\ref{fig:X}", "conforme apresentado na Seção~\ref{sec:Y}"

---

## 6. Estrutura de Sentenças

### 6.1 Clareza
- Sentenças curtas e diretas
- Uma ideia principal por sentença
- Evite subordinações excessivas

### 6.2 Conectivos
- Use conectivos apropriados: "portanto", "assim", "consequentemente"
- Evite "daí", "então" (muito coloquial)

### 6.3 Paralelismo
- Mantenha estrutura paralela em listas
- Exemplo correto: "extrair dados, processar resultados e analisar métricas"

---

## 7. Uso de Palavras Específicas

### 7.1 "Onde"
- **Use APENAS para localizações físicas/geográficas**
- ❌ Incorreto: "algoritmo onde o tempo é minimizado"
- ✅ Correto: "algoritmo no qual o tempo é minimizado"
- ✅ Correto: "experimentos realizados em São Paulo, onde..."

### 7.2 "Qual"
- Use "no qual", "na qual", "pelo qual", etc.
- Concorde em gênero e número com o antecedente

### 7.3 "Sendo"
- Evite uso excessivo de gerúndio
- Prefira construções mais diretas

---

## 8. Figuras e Tabelas

### 8.1 Ordem de Apresentação
1. **Mencione primeiro**: "A Figura~\ref{fig:X} apresenta..."
2. **Apresente a figura**: `\begin{figure}...\end{figure}`
3. **Explique depois**: "Observa-se que..."

### 8.2 Legendas
- Legendas completas e auto-explicativas
- Figuras: legenda **embaixo**
- Tabelas: legenda **em cima**
- Use ponto final em legendas completas

### 8.3 Referências no Texto
- Toda figura/tabela deve ser referenciada no texto
- Explique o que o leitor deve observar
- Não deixe elementos sem discussão

---

## 9. Citações

### 9.1 Formato
- Use `\cite{}` para citações entre parênteses
- Use `\citeauthor{}` para citar autores no texto
- Múltiplas citações: `\cite{ref1,ref2,ref3}`

### 9.2 Posicionamento
- Citação após a afirmação, antes do ponto
- Exemplo: "O VNE é NP-difícil~\cite{autor2020}."

### 9.3 Integração ao Texto
- Evite: "Em [5] é mostrado que..."
- Prefira: "Smith et al.~\cite{smith2020} demonstram que..."

---

## 10. Seções e Organização

### 10.1 Títulos de Seções
- Capitalize primeira palavra e nomes próprios
- Evite ponto final em títulos
- Use hierarquia clara: `\section`, `\subsection`, `\subsubsection`

### 10.2 Transições
- Inicie seções com parágrafo introdutório
- Conecte seções logicamente
- Finalize seções com síntese quando apropriado

---

## 11. Abreviações e Siglas

### 11.1 Primeira Ocorrência
- Escreva por extenso + sigla entre parênteses
- Exemplo: "Virtual Network Embedding (VNE)"
- Se termo em inglês: use itálico na primeira ocorrência

### 11.2 Uso Subsequente
- Apenas a sigla: "VNE"
- Não repita a expansão

---

## 12. Listas e Enumerações

### 12.1 Listas com Marcadores
```latex
\begin{itemize}
    \item Primeiro item
    \item Segundo item
    \item Terceiro item
\end{itemize}
```

### 12.2 Listas Numeradas
```latex
\begin{enumerate}
    \item Primeira etapa
    \item Segunda etapa
    \item Terceira etapa
\end{enumerate}
```

### 12.3 Pontuação em Listas
- Itens completos: ponto final
- Fragmentos: sem pontuação ou ponto e vírgula
- Consistência dentro da mesma lista

---

## 13. Formatação de Código

### 13.1 Nomes de Variáveis
- Use `\texttt{}` para código inline
- Exemplo: `\texttt{max\_depth}`

### 13.2 Blocos de Código
```latex
\begin{lstlisting}[language=Python]
def exemplo():
    return True
\end{lstlisting}
```

---

## 14. Equações Matemáticas

### 14.1 Inline vs Display
- Inline: `$x = y + z$`
- Display: `\[x = y + z\]` ou `\begin{equation}...\end{equation}`

### 14.2 Variáveis
- Variáveis em itálico (padrão matemático)
- Funções em romano: `\mathrm{sen}`, `\mathrm{log}`

---

## 15. Revisão Final

### 15.1 Checklist
- [ ] Todos os termos estrangeiros em itálico?
- [ ] Números pequenos escritos por extenso?
- [ ] Referências cruzadas com `~\ref{}`?
- [ ] Texto impessoal (terceira pessoa)?
- [ ] "performance" substituído por "desempenho"?
- [ ] "onde" usado apenas para lugares?
- [ ] Todas as figuras/tabelas referenciadas e explicadas?
- [ ] Citações formatadas corretamente?
- [ ] Consistência terminológica?

### 15.2 Ferramentas
- Corretor ortográfico (português brasileiro)
- Verificação de consistência de termos
- Revisão de pares

---

## 16. Exemplos Práticos

### ❌ Incorreto
```latex
Nós desenvolvemos um algoritmo onde o performance é melhorado.
A figura 3 mostra os resultados.
Foram testados 7 cenários diferentes.
```

### ✅ Correto
```latex
Foi desenvolvido um algoritmo no qual o desempenho é melhorado.
A Figura~\ref{fig:resultados} mostra os resultados.
Foram testados sete cenários diferentes.
```

---

## 17. Observações Finais

- Estas regras são **diretrizes**, não leis absolutas
- Use bom senso e mantenha **consistência**
- Diferentes revistas/conferências podem ter requisitos específicos
- Sempre consulte as normas da publicação-alvo
- Em caso de dúvida, consulte artigos bem escritos da área
- Revise múltiplas vezes antes da submissão

---

## Referências

Este guia é baseado nas orientações do Prof. Charles Christian Miers e nas práticas estabelecidas na área de Ciência da Computação no Brasil.

Para mais informações sobre escrita científica, consulte:
- Normas ABNT para trabalhos acadêmicos
- Guias de estilo de conferências (IEEE, ACM, SBC)
- Manuais de redação científica em português