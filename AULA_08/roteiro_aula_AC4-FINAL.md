*AULA - AC-4 ENTREGA FINAL

#PROJETO DOG-IA

## 1. Visão Geral da Aula
* **Ponto de Partida:** Código base **DOG-IA V1**.
* **Objetivo Final:** Evoluir a arquitetura do código até alcançar os requisitos da **DOG-IA V2** e responder às **5 Questões Técnicas** preparatórias para a avaliação semestral.

## 2. Roteiro de Desenvolvimento Prático

### Marco 1 — Ambiente Urbano Dinâmico, Semáforo e Barreira de Meio-Fio
**Problema da V1:** O robô atravessa a avenida diretamente em direção ao alvo sem respeitar a faixa de pedestres, semáforos ou veículos.
* **Requisitos Técnicos:**
  1. Implementar o ciclo semafórico completo com fases de segurança **All-Red** (`VERDE` $\rightarrow$ `AMARELO` $\rightarrow$ `TODOS_VERM_1` $\rightarrow$ `PEDESTRE` $\rightarrow$ `TODOS_VERM_2`) utilizando tempo simulado (`dt` em segundos, independente do FPS).
  2. Criar veículos em duas mãos opostas com cinemática realista: aceleração (`ACEL`), desaceleração (`DESACEL`), distância de seguimento entre carros e frenagem antes da linha de retenção da faixa.
  3. Adicionar **veículos infratores** que ignoram o sinal vermelho para testar a segurança ativa do robô.
  4. Implementar uma barreira física (`aplicar_barreira`) que impeça o robô de descer o meio-fio fora da faixa de pedestres ou quando a travessia não estiver autorizada.

### Marco 2 — Arquitetura Híbrida: Planejamento Global
**Problema da V1:** A navegação puramente reativa fica presa em mínimos locais (obstáculos em "U") e não otimiza o uso do piso tátil nem múltiplos destinos.
* **Requisitos Técnicos:**
  1. Discretizar o mapa em uma grade de ocupação (células de $10 \times 10\text{ px}$) e implementar o algoritmo de busca **A\*** com heurística octile/euclidiana.
  2. Aplicar o conceito de **Espaço de Configuração (*C-Space*)** com inflação assimétrica: inflar obstáculos de solo (`30 px`), edificações (`22 px`) e dar margem maior para obstáculos suspensos (`38 px`), protegendo a cabeça do tutor humano.
  3. Atribuir custo reduzido (`0.45`) às células sobre o **piso tátil amarelo**, fazendo o planejador preferir rotas acessíveis.
  4. Configurar pontos de destino selecionáveis (`1`: Mercado, `2`: Farmácia, `3`: Padaria, `4`: Casa) e replanejamento automático caso o robô fique preso em desvio local por mais de `3,5 s`.

### Marco 3 — Sensoriamento LiDAR Realista e Segurança Preditiva
**Problema da V1:** O sensor faz varredura perfeita sem ruído e o robô não antecipa trajetórias de veículos em movimento.
* **Requisitos Técnicos:**
  1. Substituir o loop discreto de passos por interseção analítica de segmentos (`rect.clipline`), adicionando **ruído gaussiano** ($\sigma = 1,5\text{ px}$) e taxa de falha (*dropout*) de $2\%$.
  2. Aplicar um **filtro de mediana temporal** sobre uma janela deslizante de 3 quadros (`deque(maxlen=3)`) para eliminar leituras fantasmas.
  3. Implementar predição de colisão por **zona varrida (*swept volume*)**: projetar o retângulo futuro de cada veículo em movimento ($\Delta t = 1,0\text{ s}$) e acionar `FREIO_EMERGENCIA` caso intercepte o robô ou o tutor.

### Marco 4 — Acoplamento Físico do Tutor, Áudio Estéreo e Telemetria
**Problema da V1:** O usuário acompanhante é desenhado por deslocamento rígido fixo e não há feedback espacial nem métricas de desempenho.
* **Requisitos Técnicos:**
  1. Modelar o **Tutor** como entidade independente conectada pelo arnês (`GUIA = 42 px`). Se a distância entre o robô e o tutor ultrapassar a folga (`tensão > 10 px`), reduzir proporcionalmente a velocidade do robô para não puxar o usuário.
  2. Adicionar alertas sonoros sintéticos em **estéreo (`pan` $-1$ a $+1$)** para indicar auditivamente o lado do obstáculo.
  3. Registrar métricas da viagem (tempo, distância percorrida, alertas vermelhos, freios de emergência e viagens concluídas) e suporte a execução *headless* (`--benchmark`).


## 3. Questões preparatórias para a Prova semestral

## 1. Arquitetura Híbrida de Navegação (Global vs. Local):
*Na Versão 1, o robô utiliza apenas leitura imediata do LiDAR para desviar de obstáculos e apontar para o alvo. Na Versão 2, o sistema combina um planejador **A\*** em grade com a evasão reativa local.*
### 1 - Qual limitação crítica da navegação puramente reativa é resolvida por essa arquitetura híbrida e por que o planejador global sozinho também não basta em um ambiente urbano?


## 2. Máquina de estados
*Execute uma viagem completa (1 para Mercado) e observe o campo Estado no painel. Responda:*

### 1 - Liste, em ordem, os estados por que o robô passou e a condição que causou cada transição.
### 2 - Qual é a diferença entre AGUARDANDO_SINAL e FREIO_EMERGENCIA?


## 3. Percepção e ruído do sensor
*O LiDAR tem ruído gaussiano, falhas esporádicas (2%) e filtro de mediana sobre 3 varreduras. Responda:*

### 1 - Por que a mediana é mais adequada que a média para falhas do tipo “leitura = alcance máximo”?
### 2 - Qual é o custo do filtro em termos de atraso na detecção? Estime-o em segundos, considerando 60 varreduras por segundo.
### 3 - O que aconteceria se o filtro usasse 15 varreduras em vez de 3?

## 4. Segurança temporal na travessia
*A travessia só começa se tempo_restante > (RUA_ALTURA + 24 + GUIA) / velocidade × 1,35 + 0,4. Responda:*

### 1- Calcule esse limite em segundos com os valores do código (170 px de rua, 24 px de folga, 42 px de guia e 156 px/s de velocidade).
### 2- Por que o semáforo tem fases “todos vermelhos” de 1,5 s? Que risco elas eliminam?

## 5. Avaliação experimental
*Rode python dog_ia_v2.py --benchmark 20 --seed 1 e depois com --seed 7. Responda:*

### 1- Informe taxa de sucesso, tempo médio, colisões e quase-colisões das duas execuções.
### 2- Por que a seed fixa torna o experimento reproduzível, e por que ainda assim os resultados das duas seeds diferem?
### 3- Proponha uma melhoria concreta (por exemplo, margem de segurança maior, outro filtro ou outro custo no A*) e diga qual métrica você esperaria que melhorasse e qual poderia piorar.

 
### ETAPA BÔNUS - VALOR EXTRA DE MEIO PONTO PARA A PROVA SEMESTRAL.*

1 - Grave um vídeo com a execução do seu código com o DOG-IA fazendo o percurso completo ida e volta. (deve durar entre 20 a 40 segundos)

2 - Um dos integrantes do grupo deve fazer uma postagem no Linkedin e marcar todos os colegas e o professor (Flavio Santarelli no linkedin)

3 - No texto deve-se se destacar o objetivo nobre do projeto e a motivação social que eles pensado

4 - Enviar o link por email ao professor (flavio.santarelli@pro.fecaf.com.br) No corpo do email colocar o nome completo de todos os participantes do grupo.

5 - Subir todos os códigos e perguntas para o github do grupo (coloque o link do github no email)


