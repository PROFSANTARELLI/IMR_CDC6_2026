<img width="1059" height="643" alt="image" src="https://github.com/user-attachments/assets/7b465729-22db-48f7-90bf-442da6d50649" />


Introdução à Robótica Móvel e Odometria Básica
=====================================================================================
                          ROBÓTICA MÓVEL
=========================================================================================
O que define um robô móvel autônomo:

- Ciclo clássico: Sentir (Percepção) -> Pensar (Planejamento) -> Agir (Controle).

- Pose: Posição cartesiana do centro do eixo (x, y) combinada com a orientação theta (ângulo da "frente" do robô em radianos).
  
- Sistema de Coordenadas e Estado do Robô: O estado de um robô móvel em um plano 2D é definido pela pose:



  <img width="115" height="98" alt="image" src="https://github.com/user-attachments/assets/e1d633df-ee61-4cd3-b62b-f381328e5a3a" />
  
Onde (x, y) representam a posição no espaço cartesiano e θ representa a orientação (ângulo de guinada/yaw) em relação ao eixo X global.

  [ 1. O ESTADO DO ROBÔ (POSE 2D) ]
  ---------------------------------------------------------------------------------------
     Y ↑
       │         ▲ Frente (Heading)
       │        /  
       │       / θ (Teta = Orientação)         Pose:
       │      ● (x, y)                         p = [ x, y, θ ]ᵀ
       │
       └────────────────────────► X
       (x, y) = Posição no plano | θ (Teta) = Ângulo de guinada em radianos/graus

-----------------------------------------------------------------------------------------


Parâmetro L (Wheelbase): A distância física entre os pontos de contato das rodas com o solo. L dita a "dificuldade" de girar: quanto maior L, maior deve ser a diferença entre as rodas para produzir a mesma rotação.

  [ 2. CINEMÁTICA DIRETA: DAS RODAS PARA O CORPO ]

  Cinemática Diferencial Intuitiva:
   - O robô possui duas rodas independentes separadas por uma distância L.
   - Velocidade linear (v) e velocidade angular ω:

     <img width="265" height="69" alt="image" src="https://github.com/user-attachments/assets/8ffbdf91-965b-4769-8efa-edd75d7e9646" />

  ---------------------------------------------------------------------------------------
     Roda Esquerda (v_L) ────┐
                             ├─► [ v = (v_R + v_L) / 2 ]   ──► Velocidade Linear
     Roda Direita  (v_R) ────┤
       (Distância = L)       └─► [ ω = (v_R - v_L) / L ]   ──► Velocidade Angular (Ômega)

     Comportamentos Fundamentais:
     • v_R =  v_L  ──► Linha Reta (ω = 0)
     • v_R = -v_L  ──► Giro Puro no Eixo (v = 0, ω ≠ 0)
     • v_L = 0     ──► Pivô em Torno da Roda Esquerda

-----------------------------------------------------------------------------------------

  [ 3. ODOMETRIA DISCRETA (INTEGRAÇÃO NO TEMPO Δt) ]

  Integração Temporal de Posição (Odometria a cada Δt):
  ---------------------------------------------------------------------------------------
     A cada intervalo Δt (Delta t ≈ 0.016s):

     ① Atualiza Ângulo:       θ_{k+1} = θ_k + (ω · Δt)
     ② Projeta no Eixo X:     x_{k+1} = x_k + (v · cos(θ) · Δt)
     ③ Projeta no Eixo Y:     y_{k+1} = y_k + (v · sin(θ) · Δt)

-----------------------------------------------------------------------------------------

  [ 4. NAVEGAÇÃO "GO-TO-GOAL" (CONTROLE PROPORCIONAL EM MALHA FECHADA) ]
  ---------------------------------------------------------------------------------------
     Robô p = (x, y, θ)                              ★ Alvo (x_alvo, y_alvo)
            \                                       /
             \────────── Distância d (ou ρ) ───────/
                         θ_desejado = atan2(Δy, Δx)

     • Erro Angular:      e_θ = θ_desejado - θ   (normalizado em [-π, π])
     • Comando Angular:   ω   = Kp_θ · e_θ
     • Comando Linear:    v   = Kp_v · d · cos(e_θ)
=========================================================================================
Síntese em 3 Passos:

1 - Onde estou? → Lido pela Pose p=[x,y,θ]^T

2 - Como me movo? → Convertendo as rodas em v e ω via Cinemática Diferencial.

3 - Como chego ao alvo? → Calculando o erro até o objetivo e aplicando o Controlador Proporcional (Kp).







