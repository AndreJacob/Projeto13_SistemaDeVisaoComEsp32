import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt  # Importa a biblioteca para MQTT

# Configurações do broker MQTT
broker = "10.0.0.97"  # Endereço do broker MQTT público
port = 1885  # Porta padrão para conexões MQTT sem TLS
topico = "test/topic"  # Tópico onde publicaremos o contador

# Inicializa o cliente MQTT
client = mqtt.Client("simple_publisher", protocol=mqtt.MQTTv311)

# Conecta ao broker MQTT
client.connect(broker, port)

# Inicializa a captura de vídeo da webcam
video = cv2.VideoCapture(1) # Esse valor 1 está escolhendo a camera 1, normalmente a web cam é a 0

# Configurações para a detecção de mãos
hands = mp.solutions.hands  # Inicializa o módulo de detecção de mãos do MediaPipe
Hands = hands.Hands(max_num_hands=1)  # Limita a detecção a uma única mão
mpDraw = mp.solutions.drawing_utils  # Utilitário para desenhar landmarks na imagem

# Variáveis para o filtro de estabilidade
contador_anterior = -1
contador_estavel = -1
quadros_estaveis = 0
limite_quadros_estaveis = 10  # Número de quadros que o valor precisa manter para ser considerado estável

while True:
    success, img = video.read()  # Lê um quadro do vídeo
    frameRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converte o quadro para RGB (necessário para MediaPipe)
    results = Hands.process(frameRGB)  # Processa a imagem para detectar mãos
    handPoints = results.multi_hand_landmarks  # Obtém os pontos da mão detectada (se houver)
    h, w, _ = img.shape  # Obtém as dimensões da imagem
    pontos = []  # Lista para armazenar os pontos dos landmarks

    if handPoints:  # Verifica se há pontos de uma mão detectada
        for points in handPoints:
            mpDraw.draw_landmarks(img, points, hands.HAND_CONNECTIONS)  # Desenha os pontos e conexões da mão
            
            # Itera sobre os landmarks (pontos) e armazena as coordenadas na lista "pontos"
            for id, cord in enumerate(points.landmark):
                cx, cy = int(cord.x * w), int(cord.y * h)  # Converte coordenadas normalizadas para pixels
                pontos.append((cx, cy))  # Adiciona a posição do ponto à lista

            # Identifica os dedos usando os landmarks dos dedos
            dedos = [8, 12, 16, 20]  # IDs dos pontos das pontas dos dedos (indicador, médio, anelar e mínimo)
            contador = 0  # Contador de dedos levantados
            
            if pontos:  # Se há pontos detectados
                # Detecta se o polegar está levantado comparando com a posição do ponto da articulação
                if pontos[4][0] < pontos[3][0]:  # Verifica se o polegar está à esquerda da articulação
                    contador += 1

                # Verifica se os outros dedos estão levantados comparando a ponta com a articulação
                for x in dedos:
                    if pontos[x][1] < pontos[x - 2][1]:  # Verifica se o dedo está levantado
                        contador += 1

            # Verifica estabilidade do contador antes de publicar
            if contador == contador_anterior:
                quadros_estaveis += 1
            else:
                quadros_estaveis = 0  # Reseta contagem de quadros estáveis se o valor mudar

            contador_anterior = contador

            # Publica o valor se ele estiver estável pelo número de quadros definido
            if quadros_estaveis >= limite_quadros_estaveis and contador != contador_estavel:
                contador_estavel = contador
                client.publish(topico, str(contador_estavel))

            # Desenha um retângulo e imprime o número de dedos levantados na imagem
            cv2.rectangle(img, (80, 10), (200, 110), (255, 0, 0), -1)  # Cria o fundo do texto
            cv2.putText(img, str(contador_estavel), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 5)  # Imprime o contador
            print(contador_estavel)

    cv2.imshow('Imagem', img)  # Exibe a imagem com o contador de dedos
    cv2.waitKey(1)  # Atualiza a exibição da imagem (e captura o pressionamento de tecla, caso ocorra)

# Desconecta o cliente MQTT quando o script é interrompido (pode ser colocado em um bloco "finally" para garantir desconexão)
client.disconnect()
