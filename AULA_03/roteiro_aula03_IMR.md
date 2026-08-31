ATIVIDADE AC-1 – PARTE FINAL – VALOR: 0,5 PONTO

Data: 31/08/26

Entregáveis:
	Laboratórios (exercícios com código): 0,35 ponto
	Relatório final: 0,15 ponto

  
Tema principal:
Nosso robô passa a operar com sensores de proximidade (feixes de distância tipo sonar/laser) e uma arquitetura de controle reativo baseada nos princípios de Valentino Braitenberg (Sense → Act direto, sem mapa prévio).
[ Sensores de Distância (Esquerda / Frente / Direita) ]
│
▼
[ Mapeamento Reativo / Braitenberg ]
│
▼
[ Cinemática Inversa (v_L, v_R) ]
│
▼
[ Movimento Real ]


Detalhamento:
A. Modelo do Sensor de Distância (Raycasting 2D)
O robô emite N raios a partir da sua pose p=[x,y,θ]^T, com ângulos relativos β_i∈[-ϕ_"max" ,+ϕ_"max"  ]:
θ_(〖"raio" 〗_i )=θ+β_i
A distância medida s_i é o comprimento euclidiano do feixe até interceptar um obstáculo ou atingir o alcance máximo S_"max" .

B. Veículos de Braitenberg 
	Quanto mais perto um obstáculo estiver à esquerda, mais rápida gira a roda esquerda (ou freia a direita), virando o robô para longe da ameaça.
	Lei de Desvio Diferencial:
v_"repulsão" =K_"obs" ⋅(1/s_"esq"  -1/s_"dir"  )
ω=ω_"alvo" +v_"repulsão" 


ETAPA 1: Preparação do Ambiente de Laboratório
Preparar a pasta avaliativa oficial no repositório:
1. Criar a ativar o venv se utilizar o VSCODE ou CODE SPACE. No COLAB não precisa.
2. Criar o diretório AULA_03 para as entregas de hoje no seu repositório
3. Criar o arquivo resultados_aula03.md dentro do diretório AULA_03 para inserir todos os resultados e relatório final da aula de hoje


ETAPA 2: Laboratórios (total: 0,35 ponto)


Laboratório 1: Código pronto com PYGAME 
Projete e execute o script que ilustra como calcular a interseção de 3 raios sensores com obstáculos retangulares no Pygame.
#CÓDIGO LAB-1
import pygame
import math
import numpy as np

LARGURA, ALTURA = 900, 650
FPS = 60
COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_OBSTACULO = (180, 50, 50)
COR_RAIO_LIVRE = (0, 255, 100)
COR_RAIO_COLISAO = (255, 200, 0)

class RaycastDemoRobot:
    def __init__(self, x, y, theta=0.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        self.sensor_angles = [-math.pi / 4, 0.0, math.pi / 4] # Esq, Frente, Dir
        self.sensor_range = 150.0
        self.sensor_readings = [self.sensor_range] * 3

    def cast_rays(self, obstacles):
        """Verifica a interseção dos raios com obstáculos retangulares."""
        self.sensor_readings = []
        for beta in self.sensor_angles:
            angle = self.theta + beta
            min_dist = self.sensor_range
            
            # Amostragem linear ao longo do raio (raymarch simplificado)
            for step in range(5, int(self.sensor_range), 4):
                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)
                
                # Checa colisão com as bordas da tela
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    min_dist = float(step)
                    break
                    
                # Checa colisão com retângulos de obstáculos
                hit = False
                for obs in obstacles:
                    if obs.collidepoint(rx, ry):
                        min_dist = float(step)
                        hit = True
                        break
                if hit:
                    break
            self.sensor_readings.append(min_dist)

    def draw(self, surface):
        # Desenha feixes sensores
        for i, beta in enumerate(self.sensor_angles):
            angle = self.theta + beta
            dist = self.sensor_readings[i]
            rx = self.x + dist * math.cos(angle)
            ry = self.y + dist * math.sin(angle)
            cor = COR_RAIO_COLISAO if dist < self.sensor_range else COR_RAIO_LIVRE
            pygame.draw.line(surface, cor, (int(self.x), int(self.y)), (int(rx), int(ry)), 2)
            pygame.draw.circle(surface, cor, (int(rx), int(ry)), 4)
            
        # Desenha corpo
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos, 16)
        fx = self.x + 24 * math.cos(self.theta)
        fy = self.y + 24 * math.sin(self.theta)
        pygame.draw.line(surface, (255, 50, 50), pos, (int(fx), int(fy)), 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("DEMO PROFESSOR: Raycasting e Percepção Sensorial")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    robot = RaycastDemoRobot(150, 300, 0.0)
    obstacles = [
        pygame.Rect(350, 150, 100, 350),
        pygame.Rect(600, 100, 150, 100),
        pygame.Rect(600, 400, 150, 150)
    ]

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Robô segue a posição do mouse para demonstrar a varredura sensorial
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - robot.x, my - robot.y
        robot.theta = math.atan2(dy, dx)
        robot.x += dx * 0.03
        robot.y += dy * 0.03

        robot.cast_rays(obstacles)

        screen.fill(COR_FUNDO)
        for obs in obstacles:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)
        
        robot.draw(screen)

        leituras = [f"Sensor {['Esq', 'Frente', 'Dir'][i]}: {dist:5.1f} px" for i, dist in enumerate(robot.sensor_readings)]
        for i, l in enumerate(leituras):
            screen.blit(font.render(l, True, (220, 220, 220)), (20, 20 + i * 20))
        screen.blit(font.render("Mova o mouse para testar a detecção dos sensores.", True, (255, 215, 0)), (20, 90))

        pygame.display.flip()
    pygame.quit()
if __name__ == "__main__":
    main()
#FIM DO CÓDIGO

Entregáveis LAB-1
	Rodar o código acima (ajustar qualquer erro detectado)
	Salvar o código como lab01_aula03.ipynb
	Colocar print da saída no arquivo resultados_aula03.md


Laboratório 2: Rotação In-Place (Giro de 〖90〗^∘)
	Objetivo: Validar a cinemática angular fazendo o robô girar sobre o próprio eixo.
	Passo a Passo:
	Crie o script lab02_aula03.ipynb.
	Calcule o tempo necessário para girar 90^∘ (π/2" rad" ) utilizando uma velocidade angular ω_z=0.5" rad/s" .
	Publique no tópico /cmd_vel a velocidade angular calculada até atingir o ângulo desejado.
	Garanta o envio de comando de zeramento de velocidade ao final.
	Resultado esperado: O robô deve mudar sua orientação (θ) em 90^∘ no sentido anti-horário mantendo sua posição (x,y) fixa no espaço.
	Colocar print da saída no arquivo resultados_aula03.md


Laboratório 3: Percepção com Múltiplos Sensores de Feixe
	Crie o script lab03_aula03.ipynb.
	Crie um módulo sensorial completo contendo 5 feixes (ângulos: -60^∘,-30^∘,0^∘,+30^∘,+60^∘) com alcance máximo de 200" px" .
	O algoritmo deve calcular a colisão com múltiplos retângulos e as paredes externas da janela.
	Adicionar ruído gaussiano simulado às medições com média μ=0 e desvio-padrão σ=2.0" px"  (np.random.normal(0, 2.0)).
	Renderizar na tela o valor de cada sensor em tempo real ao lado de cada raio.
	Colocar print da saída no arquivo resultados_aula03.md


Laboratório 4: Veículo de Braitenberg (Comportamento de Medo Puro)
	Crie o script lab04_aula03.ipynb.
	Faça o robô navegar em uma sala fechada cheia de obstáculos fixos sem colidir, utilizando estritamente a lei de controle reativo de Braitenberg (sem alvo).
	Velocidade base de cruzeiro v_"base" =100" px/s" .
	A roda esquerda deve acelerar proporcionalmente à proximidade de obstáculos detectados pelos sensores da direita, e vice-versa:
v_L=v_"base" +K_s⋅(S_"max" -s_"dir"  )
v_R=v_"base" +K_s⋅(S_"max" -s_"esq"  )
	Se o sensor central detectar obstáculo a menos de 40" px" , o robô deve inverter uma das rodas para realizar um giro imediato no próprio eixo.


Laboratório 5: Navegador Reativo Go-to-Goal com Desvio
	Crie o script lab05_aula03.ipynb.
	O robô deve ir até um ponto clicado pelo usuário com o mouse, mas, se encontrar obstáculos no caminho, deve desviar reativamente sem colidir e retomar a perseguição do objetivo assim que o caminho estiver desobstruído.
	Modo 1 (Atração ao Alvo): Controlador Proporcional clássico de aproximação ao alvo.
	Modo 2 (Desvio de Emergência): Caso qualquer sensor indique distância <60" px" , o robô sobrepõe a velocidade angular calculando um torque repulsivo:
ω_"total" =ω_"alvo" +∑▒K_"obs" /s_i ⋅"sign" (β_i )
	O robô deve parar a menos de 15" px"  do alvo.
	Colocar print da saída no arquivo resultados_aula03.md


ETAPA 3: Relatório Final (total: 0,15 ponto)
REGRAS DO RELATÓRIO:
	No relatório é proibido o uso de ferramentas de Inteligência Artificial.
Estrutura Obrigatória:
	Faça uma explicação simples dos resultados encontrados em cada um dos 5 exercícios
	Escolha qual foi o exercício de maior dificuldade de compreensão e explique o motivo.
	Descreva as impressões gerais sobre as dificuldades técnica até o momento de compreensão de algoritmos de Robôs Inteligentes Móveis
