import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import paho.mqtt.client as mqtt

class MQTTTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Systéme de détection d'intrusion")
        self.root.geometry("400x300")

        # Configuration MQTT
        self.broker_address = "broker.hivemq.com"
        self.port = 1883

        # Interface graphique
        self.create_gui()

        # Connexion au serveur MQTT
        self.connect_to_mqtt()

    def create_gui(self):
        # Charger l'image pour l'arrière-plan
        self.bg_image = Image.open("bg1.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        
        # Label pour afficher les données
        self.motion_label = ttk.Label(self.root, text="Mouvement: ")
        self.motion_label.pack(pady=10)

        self.light_label = ttk.Label(self.root, text="Luminosité: ")
        self.light_label.pack(pady=10)

        self.temperature_label = ttk.Label(self.root, text="Température: ")
        self.temperature_label.pack(pady=10)

        # Boutons pour activer et désactiver le relais
        self.activate_button = ttk.Button(self.root, text="Activer Relais", command=self.activate_relay)
        self.activate_button.pack(pady=10)

        self.deactivate_button = ttk.Button(self.root, text="Désactiver Relais", command=self.deactivate_relay)
        self.deactivate_button.pack(pady=10)

    def connect_to_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Souscription aux topics
        client.subscribe("myproject/motion")
        client.subscribe("myproject/lumiere")
        client.subscribe("myproject/temperature")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        if topic == "myproject/motion":
            self.motion_label.config(text=f"Motion: {payload}")
        elif topic == "myproject/lumiere":
            self.light_label.config(text=f"Luminosité: {payload}")
        elif topic == "myproject/temperature":
            self.temperature_label.config(text=f"Température: {payload} °C")

    def activate_relay(self):
        self.client.publish("topicactivaterelay", "on")

    def deactivate_relay(self):
        self.client.publish("topicactivaterelay", "off")

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTTestApp(root)
    root.mainloop()
