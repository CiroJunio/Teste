# Importações para a extensão g_python

from gpt4all import GPT4All
import sys
from g_python.gextension import Extension
from g_python.hmessage import Direction, HMessage
from g_python.hpacket import HPacket
import re
import time

# Informações da extensão
extension_info = {
    "title": "Extension stuff",
    "description": "g_python test",
    "version": "1.0",
    "author": "sirjonasxx"
}
sys.argv = ['-p', '9092']
ext = Extension(extension_info, sys.argv)
ext.start()

# Carregar o modelo GPT-4-mini-4k-instruct
gpt4all_model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")

# Função para verificar se uma string está codificada em UTF-8
def is_utf8(data):
    try:
        data.encode('utf-8')
        return True
    except UnicodeError:
        return False

# Variável para armazenar mensagens já respondidas
already_responded = set()

# Função de interceptação e filtragem de mensagens
def all_packets(message):
    packet = message.packet
    packet_str = packet.g_string(ext)
    
    # Extrair a frase da mensagem removendo números, arrays e caracteres extras
    cleaned_message = re.sub(r'[\[\]\d+Æ!)]', '', packet_str).strip()
    
    # Verifica se a mensagem contém a palavra "Testkepler" (case-insensitive)
    if re.search(r'kepler', cleaned_message, re.IGNORECASE):
        # Verifica se a mensagem está codificada em UTF-8
        if is_utf8(cleaned_message):
            # Verifica se a mensagem já foi respondida
            if cleaned_message not in already_responded:
                # Armazena a mensagem capturada
                print(f"Mensagem capturada: {cleaned_message}")
                
                # Gerar resposta usando o modelo GPT4All com o cleaned_message como prompt
                gpt4all_output = gpt4all_model.generate(
                    prompt=cleaned_message, 
                    max_tokens=10,
                )
                
                # Verifica e corta o texto gerado pelo modelo GPT4All no primeiro ponto final
                if "." in gpt4all_output:
                    index = gpt4all_output.find(".")
                    gpt4all_output = gpt4all_output[:index]

                # Remove caracteres indesejados do texto gerado
                gpt4all_output_clean = gpt4all_output.replace("\\n", "").replace("\\t", "").replace("===", "").replace("<br />", "")
                
                # Enviar a resposta para o servidor
                ext.send_to_server(HPacket("Chat", gpt4all_output_clean, 1, 1))
                
                # Adiciona a mensagem à lista de mensagens já respondidas
                already_responded.add(cleaned_message)
            

# Intercepta pacotes indo para o cliente e para o servidor
ext.intercept(Direction.TO_CLIENT, all_packets)
