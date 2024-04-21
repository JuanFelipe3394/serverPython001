#bibliotecas
import socket
import os
from datetime import datetime
import threading 
from os import walk
#ip e porta
server_dados = ("127.0.0.1", 65000)
#crio um socket com as configurações tcp para uma conexão ipv4
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#mando meu server com tcp ficar escutando nessa porta e ip para redirecionar o atendimento
#mando ouvir um cliente
tcp.bind(server_dados)
tcp.listen()
#guardar informações de login
conexoes = []
clientes = []

#função thread que fica responsável por cuidar de um cliente
def responder(conexao, cliente):
    #enquanto ele desejar, o sistema irá atender ele
    while True:
        #recebe o pedido que ele enviou para o servidor
        tamanho = int.from_bytes(conexao.recv(16), "big")
        requerido = conexao.recv(tamanho).decode('utf-8')

        #print(requerido)
        #adiciona ao log a mensagem que ele repassou para o servidor
        with open("mensagens.log", 'a') as file_arquivo:
            file_arquivo.write(f"[ {datetime.now()} ] {cliente} - {requerido}\n")
        #se for /u, é para listar os ips dos outros usuários
        if requerido == "/u":
            ips = ''
            #pego os ips que logaram e vou adicionando eles
            for usuarios in clientes:
                ips = ips + usuarios[0] + ", "
                print(usuarios[0])
            #envio a mensagem formatada para o cliente
            resposta = f"Clientes conectados = {ips}".encode('utf-8')
            conexao.send(len(resposta).to_bytes(16, 'big') + resposta)
        #se for /f, é para listar o nome dos arquivos e seus tamanhos
        elif requerido == "/f":
            #pego o diretorio atual para ir caminhando
            arquivos_diretorio = ""
            pasta = os.getcwd()
            for diretorio, subpastas, arquivos in os.walk(pasta):
                for arquivo in arquivos:
                    caminho = os.path.join(os.path.realpath(diretorio), arquivo)
                    print(caminho)
                    #só considero os arquivos da pasta server_files
                    if 'server_files' in caminho:
                        arquivos_diretorio = arquivos_diretorio + f"Arquivo:{arquivo}, tamanho:{os.path.getsize(caminho)}\n"
            #envio a resposta para o cliente
            resposta = arquivos_diretorio.encode('utf-8')
            conexao.send(len(resposta).to_bytes(16, 'big') + resposta)
        #se for /h, envio uma mensagem de ajuda para o cliente
        elif requerido == "/h":
            resposta = f"/l - listar mensagens do log\n/q - sair do sistema\n/u - listar ips logados\n/h - listar ajuda\n/f - listar arquivos server_files\n/d:nome - baixar arquivo do server_files\n/u:nome - upload de arquivo para server_files\n/m:ip:mensagem - enviar mensagem para outro ip\n/b:mensagem - mensagem em broadcast".encode('utf-8')
            conexao.send(len(resposta).to_bytes(16, 'big') + resposta)
        #envia a mensagem para todos os usuários logados no sistema
        elif requerido[0:2] == "/b":
            resposta = (f"{cliente[0]}>"+requerido[3:len(requerido)]).encode('utf-8')
            #percorro em todas conexões enviando as mensagens
            for usuario in conexoes:
                usuario.send(len(resposta).to_bytes(16, 'big') + resposta)
        #vou catar o ip que o cara quer e vou enviar a mensagem para ele
        elif requerido[0:2] == "/m":
            dados = requerido.split(":")
            ip = dados[1]
            resposta = (f"{ip}>{dados[2]}").encode('utf-8')
            #se eu encontrar o ip, eu envio a mensagem para ele
            for x in range(len(clientes)):
                if ip == clientes[x][0]:
                    conexoes[x].send(len(resposta).to_bytes(16, 'big') + resposta)
                    break
        #baixo os arquivos da pasta server_files para a pasta download
        elif requerido[0:2] == "/d":
            dados = requerido.split(":")
            #pego o nome do arquivo
            nome = dados[1]
            arquivos_diretorio = ""
            #seto o diretorio atual
            pasta = os.path.dirname(os.path.realpath(__file__))
            existe = 0
            #vou ver se o arquivo existe e eu consigo acessar ele
            for diretorio, subpastas, arquivos in os.walk(pasta):
                for arquivo in arquivos:
                    caminho = os.path.join(os.path.realpath(diretorio), arquivo)
                    #print(caminho)
                    if 'server_files' in caminho and nome in caminho:
                        arquivos_diretorio = print(os.path.join(os.path.realpath(diretorio), arquivo))
                        existe = 1
                        break
            #se existir, vou mandar uma mensagem de confirmação e vou começar a baixar o mesmo em outra pasta
            if existe > 0:
                #buffer com os dados do arquivo
                buffer = []
                #com arquivo aberto, eu começo a adicionar no buffer
                with open(caminho, 'rb') as file1:
                    dados = file1.read(2048)
                    while dados != b"":
                        #print(dados)
                        buffer.append(dados)
                        dados = file1.read(2048)
                #depois, eu repasso para a nova pasta
                with open(caminho.replace("server_files", "download"), 'wb') as file2:
                    for dados in buffer:
                        file2.write(dados)

                #print(buffer)
                #mensagem de confirmação avisando que o processo deu certo
                resposta = f"Arquivo encontrado e baixado para o local requerido.".encode('utf-8')
                conexao.send(len(resposta).to_bytes(16, 'big') + resposta)

            
            else:
                #mensagem que eu digo caso não encontre ele
                resposta = f"Arquivo nao encontrado.".encode('utf-8')
                conexao.send(len(resposta).to_bytes(16, 'big') + resposta)
        #deslogo o usuário do sistema e fecho a conexao com ele e mato a thread
        elif requerido == "/q":
            conexoes.remove(conexao)
            clientes.remove(cliente)
            conexao.close()
            break
        #envio todas as mensagens do log para o usuário
        elif requerido == "/l":
            resposta = ""
            with open("mensagens.log", 'r') as file:
                for linha in file:
                    resposta = resposta + linha
            
            conexao.send(len(resposta).to_bytes(16, 'big') + resposta.encode('utf-8'))

        #o usuário envia um arquivo para server_files
        elif requerido[0:2] == "/u":
            try:
                #seto na pasta correta para download
                print("Upload files")
                dados = requerido.split(":")
                nome = dados[1]
                print(nome)
                tamanho_arquivo =  int.from_bytes(conexao.recv(16), "big")
                print(f"tamanho em bytes:{tamanho_arquivo}")
                
                pasta = os.path.dirname(os.path.realpath(__file__))
                pasta = pasta.replace("server_tcp.py", "\server_files")
                pasta = pasta + "\server_files"

                #print(pasta)
                #vejo se dá bom setar na pasta
                if os.path.isdir(pasta) == False:
                    pasta = os.path.dirname(os.path.realpath(__file__))
                    pasta = pasta.replace("server_tcp.py", "/server_files")
                    pasta = pasta + "/server_files"
                    #print(pasta)
                
                caminho = os.path.join(os.path.realpath(pasta), nome)

                #print(caminho)
                #se der bom, eu começo a receber os dados do cliente
                #fico escrevendo os dados parte a parte até chegar no tamhanho final do arquivo
                with open(caminho, 'wb') as file:
                    while tamanho_arquivo > 0:
                        file.write(conexao.recv(2048))
                        tamanho_arquivo = tamanho_arquivo - 2048
                        #aqui é caso for pouca coisa pra receber
                        if tamanho_arquivo < 2048 and tamanho_arquivo > 0:
                            file.write(conexao.recv(tamanho_arquivo))
                            tamanho_arquivo = tamanho_arquivo - 2048

                #envio a mensagem dizendo que deu bom
                resposta = f"Upload concluido.".encode('utf-8')
                conexao.send(len(resposta).to_bytes(16, 'big') + resposta)
                

            except:
                #envio a mensagem dizendo que deu ruim
                resposta = f"Falha no upload.".encode('utf-8')
                conexao.send(len(resposta).to_bytes(16, 'big') + resposta)
        #se não for nada disso, digo que ele errou e mando ele tentar de novo
        else:
            resposta = f"Pedido não está na lista de opcoes.".encode('utf-8')
            conexao.send(len(resposta).to_bytes(16, 'big') + resposta)
#laço que permite vários clientes ficarem se conectando
while True:
    #fica preso esperando uma nova conexao
    print("Aguardando conexão ...")
    conexao, cliente = tcp.accept()
    print(f"Nova conexão ... {cliente[0]}.")
    conexoes.append(conexao)
    clientes.append(cliente)
    #cria uma thread para atender aquele cliente e libera espaço para novas requisições
    respondendo = threading.Thread(target=responder, args=(conexao,cliente))
    respondendo.start()