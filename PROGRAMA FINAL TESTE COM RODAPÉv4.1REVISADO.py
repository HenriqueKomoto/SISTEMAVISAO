# ╔═══════════════════════════════════════════════════════════════════════════════════════════╗ #

                   # PROGRAMA DE DETECÇÃO DE PEÇAS POR COR E FORMATO #
                       # ESCOLA TÉCNICA ESTADUAL PRESIDENTE VARGAS #
       # ESTEIRA SEPARADORA DE PEÇAS COM SISTEMA DE MONITORAMENTO E CONTROLE POR VíDEO #
                             ##PROJETADO POR HENRIQUE KOMOTO##

# ╚═══════════════════════════════════════════════════════════════════════════════════════════╝#

import cv2
import RPi.GPIO as gpio
import numpy as np
from functools import partial

# ANTES DE ABRIR PROGRAMA RODAR O COMANDO sudo modprobe bcm2835-v4l2# NO TERMINAL RASPBERRY

# COMANDO PARA DESATIVAR AVISO DO USO DAS GPIOS
gpio.setwarnings(False)

# COMANDOS PARA CONFIGURAR OS PINOS GPIO
gpio.setmode(gpio.BOARD)
gpio.setup(40, gpio.OUT)
gpio.setup(38, gpio.OUT)
gpio.setup(36, gpio.IN)
gpio.setup(32, gpio.IN)

Objetos=0
Objetos1=0 


# COMANDO PARA CONFIGURAR A WEBCAM
cap = cv2.VideoCapture(0)

# COMANDO PARA DEFINIR TAMANHOS DAS JANELAS
largura = 500
altura = 400


# ESTAS LINHAS DE PROGRAMAÇÃO É REFERENTE A BARRA DE CORES
def nothing(x):
    pass


cv2.namedWindow("Trackbars")
cv2.namedWindow("Trackbars2")

cv2.createTrackbar("L - H", "Trackbars", 33, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 101, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 26, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 123, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

cv2.createTrackbar("L - H", "Trackbars2", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars2", 0, 179, nothing)
cv2.createTrackbar("L - V", "Trackbars2", 70, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars2", 69, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars2", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars2", 255, 255, nothing)

# DEFINE OS SENSORES IF COMO ENTRADA
sensor_ir2 = partial(gpio.input, 32)
sensor_ir = partial(gpio.input, 36)



while True:
    
    #ESTE COMANDO SERVE PARA DESLIGAR OS RELÉS E PRINTAR A QUANTIDADE DE OBJETOS QUE PASSAM PELA RAMPA    
    if sensor_ir() == 0:
        Objetos += 1
        # Enquanto o objeto não sair da frente...
        while sensor_ir() != 1:
            pass
        print("Objetos Detectados Rampa1 =", Objetos)
        gpio.output(40,1)
        
        
             
    #if sensor_ir2() == 0:
        #Objetos1 += 1
        #Enquanto o objeto não sair da frente...
        #while sensor_ir2() != 1:
            #pass
        #print("Objetos Detectados Rampa2 =", Objetos1)
        #gpio.output(38,1)     


    #COMANDO QUE ADICIONA AS IMAGENS DA WEBCAM EM UM FRAME
    _, frame = cap.read()
   

    # ADICIONAR BLUR NA IMAGEM, FAZENDO COM QUE SE TENHA MENOS IMPERFEIÇÕES NA IMAGEM CAPTURADA
    blurred_frame = cv2.GaussianBlur(frame, (9, 9), 0)

    # COMANDO PARA A TELA NEGATIVA DE BARRAS ONDE EU CONSIGO ISOLAR AS CORES
    hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    l_h1 = cv2.getTrackbarPos("L - H", "Trackbars2")
    l_s1 = cv2.getTrackbarPos("L - S", "Trackbars2")
    l_v1 = cv2.getTrackbarPos("L - V", "Trackbars2")
    u_h1 = cv2.getTrackbarPos("U - H", "Trackbars2")
    u_s1 = cv2.getTrackbarPos("U - S", "Trackbars2")
    u_v1 = cv2.getTrackbarPos("U - V", "Trackbars2")

    # COMANDO PARA DEFINIR O ALCANCE DE COR NO QUAL AS BARRAS SÃO RESPONSAVEIS
    lower_blue = np.array([l_h, l_s, l_v])
    upper_blue = np.array([u_h, u_s, u_v])
    lower_green = np.array([l_h1, l_s1, l_v1])
    upper_green = np.array([u_h1, u_s1, u_v1])

    # MASK REPRESENTAM A TELA EM NEGATIVO DAS CORES
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask2 = cv2.inRange(hsv, lower_green, upper_green)

    # RESULTADOS MOSTRAM A COR ISOLADA NA TELA
    RESULTADO1 = cv2.bitwise_and(frame, frame, mask=mask)
    RESULTADO2 = cv2.bitwise_and(frame, frame, mask2, mask2)

    # ESTES COMANDOS SÃO RESPONSAVEIS POR FAZER O CONTORNO DO OBJETO

    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    _, contours2, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # ESTE COMANDO SERVE PARA COLOCAR REFERENCIA NOS OBJETOS QUE O DETECTOR IRA CONTORNAR NO QUAL A AREA TEM Q SER CALCULADA USANDO O COMANDO print(area) ###NÃO ESQUECER DE USAR ELE QUANDO TIVERMOS AS PEÇAS DE TESTE DEFINIDAS
    # O COMANDO QUE DEVE SER USADO APOS O for contour in contours: are = cv2.contourArea (contour) é if area > "NUMERO DA AREA) >(MAIOR) OU <(MENOR)

    # COMANDO PARA DEFINIR A FONTE QUE APARECERA NA TELA
    font = cv2.FONT_HERSHEY_COMPLEX

    for contour in contours:
        area = cv2.contourArea(contour)
        approx = cv2.approxPolyDP(contour, 0.03 * cv2.arcLength(contour, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]


        if area > 9000:
            cv2.drawContours(frame, contours, -1, (0, 255, 0), 4)

        if len(approx) == 4:
            cv2.putText(frame, "QUADRADO", (x, y), font, 1, (0, 255, 255))
            gpio.output(40, 0)


        elif len(approx) == 5:
            cv2.putText(frame, "PENTAGONO", (x, y), font, 1, (0, 255, 255))
            # gpio.output(40 , 0)

    for contour in contours2:
        area = cv2.contourArea(contour)
        approx = cv2.approxPolyDP(contour, 0.03 * cv2.arcLength(contour, True), True)
        x = approx.ravel()[0]
        y = approx.ravel()[1]

        if area > 9000:
            cv2.drawContours(frame, contours2, -1, (0, 255, 255), 4)

            if len(approx) == 8:
                cv2.putText(frame, "CIRCULO", (x, y), font, 1, (0, 255, 0))
                # gpio.output(38, 0)

            elif len(approx) == 3:
                # gpio.output(38, 0)
                cv2.putText(frame, "TRIANGULO", (x, y), font, 1, (0, 255, 0))





    # COMANDO PARA DIMENSIONAR TAMANHO DAS JANELAS

    frame = cv2.resize(frame, (largura, altura))
    # RESULTADO1 = cv2.resize(RESULTADO1, (largurax, alturay))
    # RESULTADO2 = cv2.resize(RESULTADO2, (largurax, alturay))
    # mask = cv2.resize(mask, (largurax, alturay))
    # mask2 = cv2.resize(mask2, (largurax, alturay))

    # COMANDO QUE FAZ APARECER NA TELA O OBJETO DESEJADO

    cv2.imshow("MONITORAMENTO", frame)
    # cv2.imshow("RESULTADO2", RESULTADO2)
    # cv2.imshow("RESULTADO1", RESULTADO1)
    # cv2.imshow("mask2", mask2)
    # cv2.imshow("mask", mask)
    

    # ESTES COMANDOS SERVEM PARA A PARTE FINALIZAR O PROGRAMA

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

    # PARA FECHAR O PROGRAMA BASTA APERTAR ESC
cap.release()
cv2.destroyAllWindows()
