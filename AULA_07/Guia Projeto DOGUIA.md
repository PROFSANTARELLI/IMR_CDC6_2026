# GUIA DE PROJETO

**Projeto:** DOG-IA — Robô Cão-Guia Urbano de Inteligência Assistiva  
**Curso:** Ciência da Computação (6º Semestre)

---

## ETAPA 1: CONFIGURAÇÃO DO AMBIENTE

### 1.1 Explicação

O **DOG-IA** é um robô cão-guia assistivo desenvolvido para navegação urbana autônoma. Para construir esse sistema, utilizamos o **ROS 2 (Robot Operating System)**, que funciona como um *middleware* modular baseado na arquitetura de **Nós (Nodes)** e **Tópicos (Topics)** através do padrão *Publisher/Subscriber*.

Para a simulação do mundo real e análise de telemetria, utilizamos duas ferramentas chave:

1. **Gazebo:** Simulador 3D que recria a física (gravidade, superfícies, atrito, obstáculos e colisões).  
2. **RViz2:** Painel de visualização de dados dos sensores (LiDAR, Câmera RGB-D, odometria e sistemas de coordenadas TF2).

---

### 1.2 Passos Técnicos de Instalação e Primeiro Teste

#### Passo 1: Atualização do Sistema e Repositórios do ROS 2

Execute no terminal do seu **Ubuntu 22.04 LTS** (Nativo ou WSL2):

```sh
# 1. Atualizar a lista de pacotes do sistema
sudo apt update && sudo apt upgrade -y

# 2. Adicionar o repositório oficial do ROS 2
sudo apt install -y software-properties-common curl git
sudo add-apt-repository universe -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

#### Passo 2: Instalação dos Pacotes Essenciais

```sh
# Instalar o ROS 2 Humble e ferramentas da simulação
sudo apt update
sudo apt install -y \
  ros-humble-desktop-full \
  ros-dev-tools \
  gazebo \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-joint-state-publisher-gui \
  ros-humble-xacro \
  ros-humble-teleop-twist-keyboard \
  ros-humble-cv-bridge \
  python3-opencv
```

#### Passo 3: Configurar Variáveis de Ambiente

```sh
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

#### Passo 4: Teste de Validação de Comunicação (Smoke Test)

Abra dois terminais independentes:

* **Terminal 1:**

```sh
ros2 run demo_nodes_cpp talker
```

* **Terminal 2:**

```sh
ros2 run demo_nodes_py listener
```

> **Resultado Esperado:** O Terminal 2 deve exibir em tempo real os pacotes enviados pelo Terminal 1: `[INFO] [listener]: I heard: [Hello World: X]`.

---

## ETAPA 2: CRIAÇÃO DO WORKSPACE E CÓDIGO PYTHON

### 2.1 Explicação

Nesta etapa, organizamos a estrutura do repositório no **GitHub** e construímos nosso primeiro nó em Python utilizando a biblioteca cliente `rclpy`.

Para integrar o processamento de imagem com a visão computacional, utilizamos a biblioteca `cv_bridge`. Ela atua como um conversor entre os formatos de imagem do ROS 2 (`sensor_msgs/msg/Image`) e matrizes numéricas suportadas pela **OpenCV** (`numpy.ndarray`).

---

### 2.2 Passo a Passo Técnico e Criação do Pacote

#### Passo 1: Criar o Workspace e o Repositório Git

```sh
# 1. Criar diretório do workspace ROS 2
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# 2. Criar a pasta oficial do projeto do grupo
mkdir DOG-IA_ROBO_CAO-GUIA
cd DOG-IA_ROBO_CAO-GUIA

# 3. Documentação inicial
mkdir docs
echo "# Escopo do Projeto DOG-IA" > docs/escopo_dog-ia_robo.md
```

#### Passo 2: Criar o Pacote Python no ROS 2

```sh
cd ~/ros2_ws/src/DOG-IA_ROBO_CAO-GUIA
ros2 pkg create --build-type ament_python dog_ia_core --dependencies rclpy sensor_msgs cv_bridge std_msgs
```

---

### 2.3 Código Python Comentado Linha a Linha

Crie o arquivo `valida_ambiente.py` no caminho:  
`~/ros2_ws/src/DOG-IA_ROBO_CAO-GUIA/dog_ia_core/dog_ia_core/valida_ambiente.py`

```py
#!/usr/bin/env python3
# Linha 1: Define o interpretador Python 3 para a execução do script.

import rclpy
# Linha 4: Importa a biblioteca oficial do ROS 2 para Python (rclpy).

from rclpy.node import Node
# Linha 6: Importa a classe base 'Node' necessária para criar nós do ROS 2.

import cv2
# Linha 8: Importa a biblioteca OpenCV para processamento de imagens e visão.

from cv_bridge import CvBridge
# Linha 10: Importa o conversor de mensagens de imagem do ROS para OpenCV.

from std_msgs.msg import String
# Linha 12: Importa o tipo de mensagem textual padrão (String).


class ValidaAmbienteNode(Node):
    """
    Linha 16: Classe principal do nó de validação do ambiente.
    Herda da classe 'Node' do ROS 2.
    """

    def __init__(self):
        super().__init__('valida_ambiente_node')
        # Linha 22: Inicializa o nó com o nome registrado 'valida_ambiente_node'.

        self.bridge = CvBridge()
        # Linha 25: Instancia o objeto para ponte entre ROS e OpenCV.

        self.publisher_ = self.create_publisher(String, 'dog_ia/status', 10)
        # Linha 28: Cria o publicador no tópico 'dog_ia/status' com limite de fila 10.

        self.timer = self.create_timer(2.0, self.publica_status)
        # Linha 32: Configura um temporizador para rodar a cada 2.0 segundos.

        self.get_logger().info("✅ Nó de Validação do DOG-IA iniciado com sucesso!")
        # Linha 35: Exibe mensagem no log do terminal confirmando a inicialização.

    def publica_status(self):
        """
        Linha 39: Callback executado periodicamente pelo temporizador.
        """
        msg = String()
        # Linha 42: Instancia uma nova mensagem do tipo String.

        msg.data = "DOG-IA Operacional: ROS 2 + OpenCV Prontos!"
        # Linha 45: Atribui o conteúdo textual à mensagem.

        self.publisher_.publish(msg)
        # Linha 48: Envia a mensagem para o tópico registrado.

        self.get_logger().info(f'Mensagem Publicada: "{msg.data}"')
        # Linha 51: Registra no console a confirmação do envio.


def main(args=None):
    """
    Linha 55: Função de inicialização e execução do nó.
    """
    rclpy.init(args=args)
    # Linha 58: Inicializa as comunicações do ROS 2.

    node = ValidaAmbienteNode()
    # Linha 61: Instancia a classe do nó.

    try:
        rclpy.spin(node)
        # Linha 65: Mantém o nó rodando e aguardando eventos até interrupção.
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # Linha 70: Finaliza e destrói o nó.
        
        rclpy.shutdown()
        # Linha 73: Encerra o sistema de comunicação do ROS 2.


if __name__ == '__main__':
    main()
    # Linha 78: Ponto de entrada do script.
```

---

#### Passo 3: Registrar o Executável no `setup.py`

Abra o arquivo `~/ros2_ws/src/DOG-IA_ROBO_CAO-GUIA/dog_ia_core/setup.py` e adicione a instrução dentro de `entry_points`:

```py
entry_points={
    'console_scripts': [
        'valida_ambiente = dog_ia_core.valida_ambiente:main',
    ],
},
```

#### Passo 4: Compilação e Execução

```sh
# 1. Navegar até a raiz do workspace
cd ~/ros2_ws

# 2. Compilar o workspace
colcon build --symlink-install

# 3. Atualizar o ambiente
source install/setup.bash

# 4. Executar o nó
ros2 run dog_ia_core valida_ambiente
```

---

## CHECKLIST DE AVALIAÇÃO E NIVELAMENTO

| Requisito | Status |
| :---- | :---: |
| ROS 2 Humble e Gazebo instalados e operacionais | \[ \] |
| Repositório no GitHub criado com o arquivo `docs/escopo_dog-ia_robo.md` | \[ \] |
| Professor adicionado no GitHub (`flavio.santarelli@pro.fecaf.com.br`) | \[ \] |
| Workspace `~/ros2_ws` compilado com o pacote `dog_ia_core` | \[ \] |
| Nó `valida_ambiente` transmitindo mensagens no tópico `dog_ia/status` | \[ \] |

&nbsp;