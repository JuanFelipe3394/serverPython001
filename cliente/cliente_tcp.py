#biblioteca
import socket
import os
import threading 
#ip do servidor
ip = "127.0.0.1"
#porta do servidor
porta = 65000
#transformo os dados em uma tupla
meu_server = (ip, porta)
#crio um socket com as configurações tcp para uma conexão ipv4
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#inicio a conexão com o servidor
tcp.connect(meu_server)
#thread para ficar escrevendo o que o cliente deseja
def escrever():
    while True:
        #mensagem padrão
        mensagem = input("\n>").encode('utf-8')
        tamanho = len(mensagem).to_bytes(16, 'big')
        tcp.send(tamanho + mensagem)
        #se ele quer enviar um arquivo, ai as coisas mudam
        opc = mensagem.decode('utf').split(":")
        if opc[0] == '/u' and len(opc) >= 2:
            try:
                #vejo se consigo abrir o arquivo e etc
                caminho = os.path.join(os.getcwd(), opc[1])
                if "cliente" not in caminho:
                    pasta = os.getcwd() + "\cliente"
                    
                    if os.path.isdir(pasta) == False:
                        pasta = os.getcwd() + "/cliente"
        
                    caminho = os.path.join(os.path.realpath(pasta), opc[1])

                print(caminho)
                tamanho_arquivo = os.path.getsize(caminho)
                print(tamanho_arquivo)
                #envio o tamanho total do arquivo convertido para bytes
                tcp.send(tamanho_arquivo.to_bytes(16, "big"))
                
                buffer = []
                #faço um buffer com os dados do arquivo
                with open(caminho, 'rb') as file:
                    
                    dados = file.read(2048)
                    while dados != b"":
                        #print(dados)
                        buffer.append(dados)
                        dados = file.read(2048)
                #envio todos os dados para o servidor
                for dado in buffer:
                    tcp.send(dado)
                #se não conseguir abrir, aviso que deu ruim
            except:
                print("Erro ao tentar enviar tal arquivo.")
#thread para ficar recebendo mensagens do lado do servidor
def ler():
    while True:
        tamanho = int.from_bytes(tcp.recv(16), "big")
        requerido = tcp.recv(tamanho).decode('utf-8')
        print(requerido)


#instâncio as duas threads, cada uma de forma autônoma, uma pra escrever e eoutra para falar
mandando = threading.Thread(target=escrever, args=())
lendo = threading.Thread(target=ler, args=())

mandando.start()
lendo.start()