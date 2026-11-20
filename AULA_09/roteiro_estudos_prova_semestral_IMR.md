# Roteiro de Estudos - Prova Semestral

> **Nota Importante:** O Valor da prova vai de 0 a 3 pontos
> - Sem consulta
> - Serão 4 questões alternativas de 0,5 ponto cada e um dissertativa de 1 ponto
> - A prova será apenas autorizada usando os computadores do laboratório **(SEM exceção)**

---

## 1. Arquiteturas de Navegação (Reativa, Deliberativa e Híbrida)

* **Navegação Reativa (Local):**
  * **Conceito:** Liga diretamente os sensores aos atuadores sem consultar mapas globais.
  * **Vantagem / Limitação:** Resposta ultra-rápida a obstáculos dinâmicos, mas sofre com **mínimos locais** (o robô fica preso em obstáculos côncavos em formato de "U" ou becos sem saída).
* **Navegação Deliberativa (Global):**
  * **Conceito:** Utiliza um mapa interno conhecido para calcular uma rota completa antes de iniciar o movimento (*Percepção \ Planejamento \ Ação*).
  * **Vantagem / Limitação:** Encontra o caminho ótimo globalmente, mas é computacionalmente lenta para reagir a mudanças súbitas no ambiente.
* **Arquitetura Híbrida (Global + Local):**
  * **Conceito:** Combina um planejador global (que define a macro-rota) com uma camada reativa local (que desvia de imprevistos em tempo real).
  * **Exemplo Lógico:** Um veículo autônomo usa um planejador global para traçar a rota entre dois bairros, mas usa sensores locais para frear bruscamente se um pedestre surgir na pista.

---

## 2. Planejamento de Caminhos em Grafos (Algoritmo A\*)

* **Conceito:** Algoritmo de busca que encontra o caminho de menor custo entre um nó inicial $S$ e um objetivo $G$ em um grafo ou grade de ocupação.
* **Função de Avaliação:**
  $$f(n) = g(n) + h(n)$$
  * $g(n)$: Custo real acumulado do ponto de partida até o nó atual $n$.
  * $h(n)$: Heurística (estimativa matemática da distância restante de $n$ até o destino $G$).
* **Regra de Admissibilidade:** Para garantir o menor caminho possível, a heurística $h(n)$ **nunca pode superestimar** o custo real até o destino (ex.: distância Euclidiana ou Manhattan).
* **Exemplo Lógico:** Em um terreno dividido em células, atravessar asfalto custa $1$ e atravessar lama custa $4$. Mesmo que a lama seja uma linha reta mais curta, o A\* escolhe contornar pelo asfalto porque a soma $g(n) + h(n)$ resulta em um custo total menor.

---

## 3. Espaço de Configuração (*C-Space*) e Inflação de Obstáculos

* **Conceito:** Transformação geométrica em que os obstáculos do mapa real (*Workspace*) são expandidos ("inflados") pelo raio físico do robô.
* **Por que utilizar?** Permite tratar o robô como um **ponto adimensional** durante o cálculo de rotas, garantindo que qualquer caminho válido no grafo mantenha o corpo físico do robô livre de colisões.
* **Inflação Assimétrica:** Diferentes tipos de obstáculos podem receber margens distintas conforme o risco envolvido (ex.: obstáculos suspensos ou frágeis recebem raio de inflação maior que obstáculos comuns).
* **Exemplo Lógico:** Se um robô circular possui raio $R = 20\text{ cm}$ e precisa passar por um corredor de $35\text{ cm}$ entre duas paredes, inflar cada parede em $20\text{ cm}$ fecha virtualmente o corredor no *C-Space*, impedindo o planejador de tentar uma passagem fisicamente impossível.

---

## 4. Sensoriamento e Filtragem de Ruído

* **Princípio do Sensor de Distância (Raycasting / LiDAR):**
  * Emite feixes em ângulos conhecidos $\theta_i$ e mede o tempo de retorno para calcular a distância $d$ até o obstáculo mais próximo.
  * Múltiplos feixes distribuídos em um Campo de Visão (*FOV*) permitem distinguir obstáculos frontais de laterais.
    
* **Ruído e Falhas (*Dropouts*):** Sensores reais sofrem com variações aleatórias (ruído gaussiano) e falhas pontuais de leitura (quando o feixe não retorna e marca alcance máximo).
  
* **Filtro de Mediana Temporal vs. Média Móvel:**
  * **Média Móvel:** Soma as últimas $N$ leituras e divide por $N$. É distorcida por valores extremos (*outliers*).
  * **Filtro de Mediana:** Ordena as últimas $N$ leituras (ex.: janela de 3 amostras) e escolhe o valor central. Elimina ruídos impulsivos sem suavizar as bordas reais dos obstáculos.
    
* **Exemplo Lógico:** Se um sensor a $15\text{ cm}$ de uma parede registra a sequência `[15, 165, 15]` (onde `165` é uma falha de leitura):
  * A **média** retorna $65\text{ cm}$ (erro grave que atrasa a frenagem).
  * A **mediana** ordena `[15, 15, 165]` e retorna $15\text{ cm}$ (descarta a falha perfeitamente).

---

## 5. Cinemática, Segurança Preditiva e Controle de Movimento

* **Cinemática Diferencial / Unicycle:**
  * O estado do robô no plano é definido por $(x, y, \theta)$, atualizado ao longo do passo de tempo $\Delta t$:
    $$x_{t+1} = x_t + v \cdot \cos(\theta) \cdot \Delta t$$
    $$y_{t+1} = y_t + v \cdot \sin(\theta) \cdot \Delta t$$
    
* **Distância de Frenagem:**
  * Um corpo com velocidade $v$ e desaceleração máxima $a$ não para instantaneamente; ele percorre uma distância mínima dada por:
    $$d_{\text{freio}} = \frac{v^2}{2a}$$
    
* **Segurança Preditiva (Zona Varrida / *Time-to-Collision*):**
  * Em ambientes dinâmicos, não basta verificar colisões na posição atual ($t = 0$). O sistema projeta o volume espacial que agentes móveis ocuparão nos próximos $\Delta t$ segundos para frear antecipadamente.

* **Exemplo Lógico:** Se um veículo aproxima-se a $10\text{ m/s}$ e freia a $5\text{ m/s}^2$, sua distância de frenagem é $d = \frac{10^2}{2 \cdot 5} = 10\text{ m}$. Um robô que detecta esse veículo a $8\text{ m}$ de distância sabe matematicamente que o carro não conseguirá parar antes da faixa e bloqueia a travessia.

---

## 6. Máquinas de Estados Finitos (FSM) e Prevenção de *Deadlocks*

* **Conceito:** Modelo computacional composto por um conjunto finito de **estados** (ex.: `SEGUINDO`, `DESVIANDO`, `AGUARDANDO`, `FREIO_EMERGENCIA`), **transições** disparadas por eventos/sensores e uma **hierarquia de prioridades**.

* **Hierarquia de Segurança:** Estados críticos de segurança (`FREIO_EMERGENCIA`) sempre possuem prioridade superior aos estados de cumprimento de objetivo (`SEGUINDO`).

* **Prevenção de *Deadlocks* (Impasse / Oscilação):**
  * Ocorre quando duas regras opostas fazem o robô alternar indefinidamente sem avançar (ex.: virar à esquerda por causa de um obstáculo e imediatamente virar à direita por causa de outro).
  * **Soluções:** Uso de temporizadores de *timeout* (se ficar muito tempo desviando, força replanejamento global), zonas de histerese ou pequenas perturbações angulares controladas.

* **Exemplo Lógico:** Se um robô fica mais de $3\text{ segundos}$ preso no estado `DESVIANDO` sem progredir rumo ao alvo, a FSM dispara uma transição de *timeout* que invalida a rota atual e solicita um novo cálculo ao planejador global.

---





