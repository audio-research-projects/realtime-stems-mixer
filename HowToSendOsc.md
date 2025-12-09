📡 Control OSC:
from pythonosc import udp_client
client = udp_client.SimpleUDPClient("localhost", 5005)

# Enviar energía del público
client.send_message("/energy", 0.8)  # Alta energía
client.send_message("/energy", 0.2)  # Baja energía
El sistema comenzará automáticamente con BPM 120, cargará los stems disponibles y responderá a los mensajes /energy para adaptar la performance al público.

