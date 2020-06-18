#!/usr/bin/env python

import re
import unicodedata
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='coronavirus')

def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = text.decode("utf-8")
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    print('TEXT PARA UTF-8 {}'.format(text))
    return str(text)

def text_to_id(text):
    """
    Convert input text to id.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = strip_accents(text.lower())
    text = re.sub('[ \t\n\r\f\v]+', '_', text)
    text = re.sub('[^0-9a-zA-Z_-]', '', text)
    text = re.sub('_', ' ', text)
    return text

with open("input.txt","a") as f:
	def callback(ch, method, properties, body):
	    #print('	Recebido: {}'.format(body.decode("utf-8")))
	    print('	Recebido: {}'.format(body))
	    #depois de consumir a mensagem da fila ela será mapeada
	    #sem_acento=strip_accents(body)
	    so_texto=text_to_id(body)
	    print (' Decodificado: {}'.format(so_texto))
	    f.write(so_texto + "\n")

	channel.basic_consume(queue='coronavirus', on_message_callback=callback, auto_ack=True)

	print('~ Esperando por mensagens. Para sair: CTRL+C')
	channel.start_consuming()

#file.close() 
