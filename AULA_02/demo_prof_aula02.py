import pygame
import math
import numpy as np

# Configurações de Display
LARGURA, ALTURA = 900, 650
FPS = 60
COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_RODA_ESQ = (255, 100, 100)
COR_RODA_DIR = (100, 255, 100)
COR_VETOR = (255, 230, 0)
COR_RASTRO = (0, 150, 100)

class DemoRobot:
    def __init__(self, x, y, theta=0.0, wheelbase=40.0, radius=20.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        self.L = float(wheelbase)
        self.radius = float(radius)
        
        self.v_l = 0.0
        self.v_r = 0.0
        self.v = 0.0
        self.omega = 0.0
        self.history = []

    def set_wheels(self, v_left, v_right):
        self.v_l = v_left
        self.v_r = v_right
        # Equações de Cinemática Direta
        self.v = (self.v_r + self.v_l) / 2.0
        self.omega = (self.v_r - self.v_l) / self.L

    def update(self, dt):
        self.theta += self.omega * dt
        self.theta = (self.theta + math.pi) % (2 * math.pi) - math.pi
        
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        
        # Guarda histórico para visualização de trajetória
        if len(self.history) == 0 or np.hypot(self.x - self.history[-1][0], self.y - self.history[-1][1]) > 3:
            self.history.append((self.x, self.y))
            if len(self.history) > 800:
                self.history.pop(0)

    def draw(self, surface):
        # 1. Rastro
        if len(self.history) > 1:
            pygame.draw.lines(surface, COR_RASTRO, False, self.history, 2)
            
        pos = (int(self.x), int(self.y))
        
        # 2. Corpo do robô
        pygame.draw.circle(surface, COR_ROBO, pos, int(self.radius), 2)
        pygame.draw.circle(surface, (40, 60, 80), pos, int(self.radius) - 2)
        
        # 3. Desenho das Rodas (para mostrar quem está tracionando)
        cos_t = math.cos(self.theta)
        sin_t = math.sin(self.theta)
        
        # Posições das rodas esquerda e direita perpendiculares a theta
        w_esq_x = self.x - (self.L / 2) * sin_t
        w_esq_y = self.y + (self.L / 2) * cos_t
        w_dir_x = self.x + (self.L / 2) * sin_t
        w_dir_y = self.y - (self.L / 2) * cos_t
        
        pygame.draw.circle(surface, COR_RODA_ESQ, (int(w_esq_x), int(w_esq_y)), 5)
        pygame.draw.circle(surface, COR_RODA_DIR, (int(w_dir_x), int(w_dir_y)), 5)
        
        # 4. Vetor Direção (Heading Vector)
        frente_x = self.x + (self.radius + 15) * cos_t
        frente_y = self.y + (self.radius + 15) * sin_t
        pygame.draw.line(surface, COR_VETOR, pos, (int(frente_x), int(frente_y)), 3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("DEMO PROFESSOR: Cinemática Diferencial Interativa")
    clock = pygame.time.Clock()
    font_bold = pygame.font.SysFont("monospace", 16, bold=True)
    font = pygame.font.SysFont("monospace", 14)

    robot = DemoRobot(x=LARGURA // 2, y=ALTURA // 2, theta=0.0)
    modo_atual = "Parado (Aguardando comando)"

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    robot.set_wheels(-60.0, 60.0)
                    modo_atual = "Modo 1: Giro no Eixo (vL = -60, vR = +60 -> v = 0, omega != 0)"
                elif event.key == pygame.K_2:
                    robot.set_wheels(0.0, 90.0)
                    modo_atual = "Modo 2: Pivô na Roda Esquerda (vL = 0, vR = +90)"
                elif event.key == pygame.K_3:
                    robot.set_wheels(60.0, 110.0)
                    modo_atual = "Modo 3: Arco Suave (vL = 60, vR = 110)"
                elif event.key == pygame.K_SPACE:
                    robot.set_wheels(0.0, 0.0)
                    modo_atual = "Modo: Parado (Freio Acionado)"
                elif event.key == pygame.K_c:
                    robot.history.clear()

        robot.update(dt)

        # Renderização
        screen.fill(COR_FUNDO)
        robot.draw(screen)

        # Painel Didático de Telemetria
        painel = [
            f"ESTADO: {modo_atual}",
            f"-----------------------------------------------------------------",
            f"Pose Real: x = {robot.x:6.1f} px | y = {robot.y:6.1f} px | theta = {math.degrees(robot.theta):6.1f}° ({robot.theta:5.2f} rad)",
            f"Entradas de Roda:   v_Esquerda (Vermelha) = {robot.v_l:5.1f} px/s | v_Direita (Verde) = {robot.v_r:5.1f} px/s",
            f"Cinemática Direta:  v Linear = {robot.v:5.1f} px/s | omega Angular = {robot.omega:5.2f} rad/s",
            f"-----------------------------------------------------------------",
            f"[Teclas de Demonstração]: 1: Giro Puro | 2: Pivô Roda | 3: Arco | ESPAÇO: Parar | C: Limpar Rastro"
        ]

        for i, linha in enumerate(painel):
            cor = (255, 215, 0) if i == 0 else (220, 220, 220)
            f = font_bold if i in [0, 2, 4] else font
            rendered = f.render(linha, True, cor)
            screen.blit(rendered, (20, 20 + i * 22))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
