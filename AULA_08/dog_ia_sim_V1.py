import pygame
import math
import random

# ==================== CONFIGURAÇÕES GERAIS ====================
LARGURA, ALTURA = 1050, 680
FPS = 60
AREA_MAPA_LARGURA = LARGURA - 260

# Paleta de Cores Urbanas e Assistivas
BRANCO = (245, 245, 245)
PRETO = (20, 22, 28)
ASFALTO = (42, 45, 52)
CALÇADA_CLARA = (130, 134, 142)
MEIO_FIO = (175, 180, 188)
PISO_TATIL = (235, 190, 20)
GRAMA = (46, 115, 65)

# Cores do Cão-Robô e Sensores
CORPO_ROBO = (30, 136, 229)
DETALHE_ROBO = (15, 76, 129)
CABECA_ROBO = (230, 236, 245)
ARNES_GUIA = (255, 215, 0)
VERDE_LIVRE = (46, 204, 113)
LARANJA_ALERTA = (255, 140, 0)
VERMELHO_PERIGO = (225, 55, 55)
ROXO_SUSPENSO = (155, 89, 182)


def rotacionar_ponto(cx, cy, px, py, angulo):
    """Rotaciona um ponto (px, py) ao redor de (cx, cy) dado um ângulo em radianos."""
    s = math.sin(angulo)
    c = math.cos(angulo)
    dx = px - cx
    dy = py - cy
    nx = cx + (dx * c - dy * s)
    ny = cy + (dx * s + dy * c)
    return (int(nx), int(ny))


class RoboCaoGuia:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0.0
        self.raio = 20
        self.velocidade_base = 2.5
        self.alcance_lidar = 165
        self.num_raios = 19
        self.fov = math.radians(150)
        self.leituras_lidar = []
        self.status_assistivo = "Caminho livre. Seguindo pelo piso tátil."
        self.cor_alerta = VERDE_LIVRE
        self.passo_animacao = 0.0  # Para animar as patas andando

    def ler_lidar(self, obstaculos):
        """Simula o sensor LiDAR 2D + Câmera Superior (Raycasting)."""
        self.leituras_lidar = []
        angulo_inicial = self.angulo - (self.fov / 2)
        passo_angulo = self.fov / (self.num_raios - 1)

        for i in range(self.num_raios):
            ang_raio = angulo_inicial + i * passo_angulo
            dist_encontrada = self.alcance_lidar
            tipo_detectado = None

            for dist in range(self.raio, self.alcance_lidar, 4):
                rx = self.x + math.cos(ang_raio) * dist
                ry = self.y + math.sin(ang_raio) * dist

                # Limites das calçadas / paredes dos prédios
                if rx <= 15 or rx >= AREA_MAPA_LARGURA - 15 or ry <= 15 or ry >= ALTURA - 15:
                    dist_encontrada = dist
                    tipo_detectado = "parede"
                    break

                colidiu = False
                for obs in obstaculos:
                    if obs["rect"].collidepoint(rx, ry):
                        dist_encontrada = dist
                        tipo_detectado = obs["tipo"]
                        colidiu = True
                        break
                if colidiu:
                    break

            self.leituras_lidar.append({
                "angulo": ang_raio,
                "distancia": dist_encontrada,
                "tipo": tipo_detectado
            })

    def decidir_navegacao(self, alvo):
        """Cérebro Assistivo do DOG-IA: desvia de obstáculos urbanos e guia até o destino."""
        terco = self.num_raios // 3
        esquerda = self.leituras_lidar[:terco]
        centro = self.leituras_lidar[terco: 2 * terco]
        direita = self.leituras_lidar[2 * terco:]

        min_esq = min(r["distancia"] for r in esquerda)
        min_cen = min(r["distancia"] for r in centro)
        min_dir = min(r["distancia"] for r in direita)

        suspenso_frente = any(
            r["tipo"] == "suspenso" and r["distancia"] < 115 for r in centro
        )

        if min_cen < 85:
            self.cor_alerta = VERMELHO_PERIGO
            if suspenso_frente:
                self.status_assistivo = "ALERTA CABEÇA: Galho/Toldo baixo! Desviando..."
            else:
                self.status_assistivo = "OBSTÁCULO NA CALÇADA: Contornando..."

            if min_esq > min_dir:
                self.angulo -= 0.075
            else:
                self.angulo += 0.075
            vel = 0.85

        elif min_esq < 65:
            self.cor_alerta = LARANJA_ALERTA
            self.status_assistivo = "Obstáculo à esquerda. Deslocando à direita."
            self.angulo += 0.045
            vel = self.velocidade_base * 0.85

        elif min_dir < 65:
            self.cor_alerta = LARANJA_ALERTA
            self.status_assistivo = "Obstáculo à direita. Deslocando à esquerda."
            self.angulo -= 0.045
            vel = self.velocidade_base * 0.85

        else:
            self.cor_alerta = VERDE_LIVRE
            self.status_assistivo = "Caminho livre. Guiando até a travessia."
            dx = alvo[0] - self.x
            dy = alvo[1] - self.y
            angulo_alvo = math.atan2(dy, dx)
            diff = (angulo_alvo - self.angulo + math.pi) % (2 * math.pi) - math.pi
            self.angulo += max(-0.035, min(0.035, diff))
            vel = self.velocidade_base

        self.x += math.cos(self.angulo) * vel
        self.y += math.sin(self.angulo) * vel
        self.passo_animacao += vel * 0.25

    def desenhar(self, tela):
        # 1. Feixes do LiDAR (Leque de varredura)
        for r in self.leituras_lidar:
            fim_x = self.x + math.cos(r["angulo"]) * r["distancia"]
            fim_y = self.y + math.sin(r["angulo"]) * r["distancia"]
            cor_raio = (46, 204, 113) if r["distancia"] >= self.alcance_lidar - 5 else VERMELHO_PERIGO
            pygame.draw.line(tela, cor_raio, (self.x, self.y), (fim_x, fim_y), 1)
            if r["tipo"]:
                pygame.draw.circle(tela, BRANCO, (int(fim_x), int(fim_y)), 3)

        # 2. Haste do Arnês e Usuário Acompanhante (atrás do cão-guia)
        usu_x = self.x - math.cos(self.angulo) * 42
        usu_y = self.y - math.sin(self.angulo) * 42
        # Linha rígida do arnês (guia rígida usada em cães-guia)
        pygame.draw.line(tela, ARNES_GUIA, (self.x, self.y), (usu_x, usu_y), 4)
        # Pessoa acompanhada (vista de cima)
        pygame.draw.circle(tela, (235, 235, 240), (int(usu_x), int(usu_y)), 12)
        pygame.draw.circle(tela, PRETO, (int(usu_x), int(usu_y)), 12, 2)

        # 3. Patas articuladas (animadas conforme o robô anda)
        balanco = math.sin(self.passo_animacao) * 5
        offsets_patas = [
            (10 + balanco, -14),   # Frente esquerda
            (10 - balanco, 14),    # Frente direita
            (-12 - balanco, -14),  # Traseira esquerda
            (-12 + balanco, 14),   # Traseira direita
        ]
        for ox, oy in offsets_patas:
            px, py = rotacionar_ponto(self.x, self.y, self.x + ox, self.y + oy, self.angulo)
            pygame.draw.circle(tela, DETALHE_ROBO, (px, py), 5)

        # 4. Tronco do Cão-Robô (Retângulo rotacionado)
        pontos_corpo = [
            rotacionar_ponto(self.x, self.y, self.x + 16, self.y - 11, self.angulo),
            rotacionar_ponto(self.x, self.y, self.x + 16, self.y + 11, self.angulo),
            rotacionar_ponto(self.x, self.y, self.x - 18, self.y + 11, self.angulo),
            rotacionar_ponto(self.x, self.y, self.x - 18, self.y - 11, self.angulo),
        ]
        pygame.draw.polygon(tela, CORPO_ROBO, pontos_corpo)
        pygame.draw.polygon(tela, BRANCO, pontos_corpo, 2)

        # 5. Cabeça, Orelhas Robóticas e Focinho/Câmera RGB-D
        cab_x, cab_y = rotacionar_ponto(self.x, self.y, self.x + 21, self.y, self.angulo)
        pygame.draw.circle(tela, CABECA_ROBO, (cab_x, cab_y), 9)
        pygame.draw.circle(tela, DETALHE_ROBO, (cab_x, cab_y), 9, 2)

        # Orelhas
        orelha_esq = rotacionar_ponto(self.x, self.y, self.x + 19, self.y - 10, self.angulo)
        orelha_dir = rotacionar_ponto(self.x, self.y, self.x + 19, self.y + 10, self.angulo)
        pygame.draw.circle(tela, DETALHE_ROBO, orelha_esq, 4)
        pygame.draw.circle(tela, DETALHE_ROBO, orelha_dir, 4)

        # 6. Torre do LiDAR no dorso (círculo laranja giratório)
        lidar_x, lidar_y = rotacionar_ponto(self.x, self.y, self.x + 3, self.y, self.angulo)
        pygame.draw.circle(tela, LARANJA_ALERTA, (lidar_x, lidar_y), 5)


def desenhar_ambiente_urbano(tela):
    """Desenha as ruas, calçadas, piso tátil e faixa de pedestres."""
    # Fundo geral: Calçada
    tela.fill(CALÇADA_CLARA)

    # Canteiros verdes nas bordas superior e inferior
    pygame.draw.rect(tela, GRAMA, (0, 0, AREA_MAPA_LARGURA, 28))
    pygame.draw.rect(tela, GRAMA, (0, ALTURA - 28, AREA_MAPA_LARGURA, 28))

    # Avenida horizontal no meio da tela (Asfalto)
    rua_y = 250
    rua_altura = 170
    pygame.draw.rect(tela, ASFALTO, (0, rua_y, AREA_MAPA_LARGURA, rua_altura))

    # Meio-fio (bordas da calçada)
    pygame.draw.line(tela, MEIO_FIO, (0, rua_y), (AREA_MAPA_LARGURA, rua_y), 4)
    pygame.draw.line(tela, MEIO_FIO, (0, rua_y + rua_altura), (AREA_MAPA_LARGURA, rua_y + rua_altura), 4)

    # Faixa tracejada central da rua
    for x in range(15, AREA_MAPA_LARGURA - 20, 45):
        if not (570 <= x <= 680):  # Não desenha em cima da faixa de pedestre
            pygame.draw.line(tela, BRANCO, (x, rua_y + rua_altura // 2), (x + 22, rua_y + rua_altura // 2), 3)

    # Faixa de Pedestres (Travessia segura)
    faixa_x = 580
    faixa_largura = 95
    for y in range(rua_y + 12, rua_y + rua_altura - 12, 22):
        pygame.draw.rect(tela, BRANCO, (faixa_x, y, faixa_largura, 12))

    # Piso Tátil Direcional (Amarelo na calçada superior e levando à faixa)
    pygame.draw.rect(tela, PISO_TATIL, (40, 120, 595, 14))
    pygame.draw.rect(tela, PISO_TATIL, (621, 120, 14, 130))
    # Piso tátil na calçada inferior após a travessia
    pygame.draw.rect(tela, PISO_TATIL, (621, rua_y + rua_altura, 14, 130))
    pygame.draw.rect(tela, PISO_TATIL, (150, 536, 485, 14))


def criar_cenario():
    """Cria obstáculos urbanos realistas (solo e suspensos)."""
    return [
        # Obstáculos de Solo (Postes, Bancas, Lixeiras)
        {"rect": pygame.Rect(230, 85, 45, 75), "tipo": "solo", "nome": "Banca / Hidrante"},
        {"rect": pygame.Rect(460, 160, 32, 32), "tipo": "solo", "nome": "Poste de Luz"},
        {"rect": pygame.Rect(380, 460, 40, 40), "tipo": "solo", "nome": "Lixeira Urbana"},
        # Obstáculos Suspensos (Galhos de árvores e toldos de lojas)
        {"rect": pygame.Rect(350, 75, 85, 65), "tipo": "suspenso", "nome": "Copa de Árvore"},
        {"rect": pygame.Rect(520, 485, 95, 65), "tipo": "suspenso", "nome": "Toldo de Loja"},
    ]


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("DOG-IA — Simulador Urbano de Cão-Guia Autônomo")
    clock = pygame.time.Clock()
    fonte_titulo = pygame.font.SysFont("arial", 20, bold=True)
    fonte_texto = pygame.font.SysFont("arial", 15)
    fonte_pequena = pygame.font.SysFont("arial", 12, bold=True)

    robo = RoboCaoGuia(95, 127)  # Começa sobre o piso tátil da calçada superior
    obstaculos = criar_cenario()
    alvo = [628, 543]  # Destino após atravessar a faixa de pedestres
    modo_autonomo = True

    rodando = True
    while rodando:
        clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mx < AREA_MAPA_LARGURA:
                    if evento.button == 1:
                        alvo = [mx, my]
                    elif evento.button == 3:
                        obstaculos.append({
                            "rect": pygame.Rect(mx - 22, my - 22, 44, 44),
                            "tipo": random.choice(["solo", "suspenso"]),
                            "nome": "Obstáculo"
                        })
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    modo_autonomo = not modo_autonomo
                elif evento.key == pygame.K_r:
                    robo = RoboCaoGuia(95, 127)
                    obstaculos = criar_cenario()

        teclas = pygame.key.get_pressed()
        if not modo_autonomo:
            if teclas[pygame.K_LEFT]:
                robo.angulo -= 0.05
            if teclas[pygame.K_RIGHT]:
                robo.angulo += 0.05
            if teclas[pygame.K_UP]:
                robo.x += math.cos(robo.angulo) * 3
                robo.y += math.sin(robo.angulo) * 3
                robo.passo_animacao += 0.5

        # Sensoriamento e Navegação
        robo.ler_lidar(obstaculos)
        if modo_autonomo:
            dist_alvo = math.hypot(alvo[0] - robo.x, alvo[1] - robo.y)
            if dist_alvo > 25:
                robo.decidir_navegacao(alvo)
            else:
                robo.status_assistivo = "DESTINO ALCANÇADO COM SEGURANÇA!"
                robo.cor_alerta = VERDE_LIVRE

        # ==================== RENDERIZAÇÃO ====================
        desenhar_ambiente_urbano(tela)

        # Desenha Ponto de Destino
        pygame.draw.circle(tela, VERDE_LIVRE, alvo, 20, 3)
        pygame.draw.circle(tela, VERDE_LIVRE, alvo, 7)

        # Desenha Obstáculos Urbanos
        for obs in obstaculos:
            rect = obs["rect"]
            if obs["tipo"] == "suspenso":
                # Sombra no chão + copa/toldo roxo translúcido visualmente destacado
                pygame.draw.rect(tela, (90, 95, 102), rect.move(5, 5), border_radius=12)
                pygame.draw.rect(tela, ROXO_SUSPENSO, rect, border_radius=12)
                pygame.draw.rect(tela, BRANCO, rect, 2, border_radius=12)
                lbl = fonte_pequena.render("ALTO", True, BRANCO)
                tela.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - 7))
            else:
                pygame.draw.rect(tela, (70, 74, 82), rect, border_radius=5)
                pygame.draw.rect(tela, BRANCO, rect, 2, border_radius=5)
                lbl = fonte_pequena.render("SOLO", True, BRANCO)
                tela.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - 7))

        # Desenha Cão-Robô + Usuário + LiDAR
        robo.desenhar(tela)

        # Painel Lateral de Telemetria
        painel_x = AREA_MAPA_LARGURA
        pygame.draw.rect(tela, PRETO, (painel_x, 0, LARGURA - painel_x, ALTURA))
        pygame.draw.line(tela, BRANCO, (painel_x, 0), (painel_x, ALTURA), 2)

        y_txt = 20
        tela.blit(fonte_titulo.render("TELEMETRIA DOG-IA", True, CORPO_ROBO), (painel_x + 15, y_txt))
        y_txt += 40

        modo_str = "AUTÔNOMO (IA)" if modo_autonomo else "MANUAL (Setas)"
        tela.blit(fonte_texto.render(f"Modo: {modo_str}", True, BRANCO), (painel_x + 15, y_txt))
        y_txt += 28

        min_dist = min(r["distancia"] for r in robo.leituras_lidar)
        tela.blit(fonte_texto.render(f"Sensor LiDAR: {min_dist} px", True, BRANCO), (painel_x + 15, y_txt))
        y_txt += 38

        # Caixa de Alerta Assistivo
        pygame.draw.rect(tela, robo.cor_alerta, (painel_x + 15, y_txt, 230, 88), border_radius=8)
        palavras = robo.status_assistivo.split(" ")
        linha_atual = ""
        y_alerta = y_txt + 10
        for p in palavras:
            if len(linha_atual + p) < 25:
                linha_atual += p + " "
            else:
                tela.blit(fonte_texto.render(linha_atual, True, PRETO), (painel_x + 25, y_alerta))
                y_alerta += 20
                linha_atual = p + " "
        tela.blit(fonte_texto.render(linha_atual, True, PRETO), (painel_x + 25, y_alerta))

        # Legenda e Controles
        y_leg = 325
        legenda = [
            ("ELEMENTOS DA CENA:", BRANCO),
            ("▬ Amarelo: Piso Tátil", PISO_TATIL),
            ("■ Cinza: Obstáculo Solo", (150, 155, 165)),
            ("■ Roxo: Galho/Toldo (Alto)", ROXO_SUSPENSO),
            ("● Branco: Pessoa Guiada", BRANCO),
            ("", BRANCO),
            ("CONTROLES:", BRANCO),
            ("Clique Esq: Novo Destino", BRANCO),
            ("Clique Dir: Criar Obstáculo", BRANCO),
            ("ESPAÇO: Manual / IA", BRANCO),
            ("R: Reiniciar Travessia", BRANCO),
        ]
        for texto, cor in legenda:
            tela.blit(fonte_texto.render(texto, True, cor), (painel_x + 15, y_leg))
            y_leg += 27

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()