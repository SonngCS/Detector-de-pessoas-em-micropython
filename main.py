import machine
import time 
import ntptime      # Para garantir a formatação atual do tempo

#gc.threshold(999999)  # Evitar erro MBEDTLS_ERR_SSL_CONN_EOF
gc.disable()  # Evitar erro MBEDTLS_ERR_SSL_CONN_EOF

import umail        # Para enviar e-mails via SMTP
import network      # Para conectar-se ao WIFI

import urequests    # Para enviar as ocorrências para o Thingspeak

# PINs para o controle do sensor
echo=machine.Pin(18,machine.Pin.IN)
trig=machine.Pin(5,machine.Pin.OUT)

#horariop thingspeak
f_horas = 0.0

# Funcao para se conectar ao WIFI do WOKWI
def connect_wifi():
    
    print("Conectando-se ao Wi-Fi", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('Wokwi-GUEST', '')
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.1)
    print(" Conectado!")

    #Sincronizando o horário com o servidor ntp
    ntptime.host = "0.br.pool.ntp.org"
    ntptime.settime()


# Informacoes basicas para envio de emails
sender_email = 'gdistribuidos@gmail.com'    # Email do remetente
sender_name = 'ESP32'                       # Nome do remetente
sender_app_password = 'PASSWORD'    # Senha de aplicativo do remetente
recipient_email ='gdistribuidos@gmail.com'  # Email do destinatario
email_subject ='Sensor ATIVADO'             # Titulo do email

# Enviando e-mail
def send_mail():

    time.sleep_us(2)

    now = time.localtime()  # Pegando o tempo da mensagem

    hora = 24

    if(int(now[3]) - 3 < 0):
        hora -= (int(now[3]) - 3)
    else:
        hora = int(now[3]) - 3
    
    message = "Sensor foi ativado em {:02d}/{:02d}/{} {:02d}:{:02d}\n".format(now[2], now[1], now[0], hora, now[4])
    
    global f_horas

    f_horas = 0
    f_horas += hora + float(now[4]/100)

    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)         # SSL Suporte para GMAIL
    smtp.login(sender_email, sender_app_password)
    smtp.to(recipient_email)
    smtp.write("From:" + sender_name + "<"+ sender_email+">\n")
    smtp.write("Subject:" + email_subject + "\n")
    smtp.write("\n" "AVISO: " + message + "\n")
    smtp.send()
    smtp.quit()

# Enviando a ocorrencia para o Thingspeak quando o sensor e' ativado
def send_occurence():
    
    global f_horas

    url = "http://api.thingspeak.com/update?api_key= PLACE YOUR API KEY HERE=%f" % (f_horas)
    response = urequests.get(url)
    response.close()

# Conectando ao WIFI no inicio do codigo
connect_wifi()

# Loop principal
while True:

    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    d = machine.time_pulse_us(echo,1)
    distancia = (0.034*d)/2                     # Calculando a distancia em centimetros
    print(f'Distancia: {distancia} cm')
    if(distancia <= 15):                        # Condicao em que alguem passaria na porte
        send_mail()
        send_occurence()
    time.sleep(1)
