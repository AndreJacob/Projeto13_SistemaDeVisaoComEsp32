# Projeto12_SystemVisionEsp32
Sistema de Visão com Esp32
links para ver pronto: 

https://www.instagram.com/p/DCIRroNAB-u/

https://www.youtube.com/shorts/6jKbiLAcVhY

Utilizando:
Python
C++
Protocolo Mqtt

Hardware:
ESP32
webcam
protoboard com leds
cabos
lampada
rele de estado solido

Python:
Com a biblioteca mediapipe e CV2 fazendo um rastreio da mão atraves de uma camera USB ou webcam.
Esse rastreamento mostra os valores dos dedos.
Busco esse valor dos dedos e atraves do protocolo mqtt envio esses dados ao Esp32
No esp32 leio esses dados e ativo os leds  e lampada de acordo com o valor.
