import tkinter as tk
from tkinter import ttk
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
          # Configuration de la couleur d'arrière-plan
          
        bg_color = "#98bad5"
        self.root.configure(bg=bg_color)
        
        padx_value = 20
        pady_value = 10
        
        # Label pour afficher les données
        label_style1 = {'font': ('Arial', 18), 'foreground': '#3350FF', 'background': bg_color, 'anchor': 'w'}

        label_style = {'font': ('Arial', 12), 'foreground': 'black', 'background': bg_color, 'anchor': 'w'}
        
         # Titre des données captées par les capteurs
        self.title_label = ttk.Label(self.root, text=" Données captées ", **label_style1)
        self.title_label.pack(pady=pady_value, padx=padx_value)
        
        self.motion_label = ttk.Label(self.root, text="Mouvement: ", **label_style)
        self.motion_label.pack(pady=(pady_value, 0), padx=padx_value, anchor="w")

        self.light_label = ttk.Label(self.root, text="Luminosité: ", **label_style)
        self.light_label.pack(pady=pady_value, padx=padx_value, anchor="w")

        self.temperature_label = ttk.Label(self.root, text="Température: ", **label_style)
        self.temperature_label.pack(pady=pady_value, padx=padx_value, anchor="w")

         # Conteneur de cadre pour les boutons
        button_frame = ttk.Frame(self.root, padding=(0, pady_value))
        button_frame.pack()
        # Boutons pour activer et désactiver le relais
        self.activate_button = ttk.Button(self.root, text="Activer Relais", command=self.activate_relay)
        self.activate_button.pack(side="left", padx=(100, padx_value), pady=pady_value)

        self.deactivate_button = ttk.Button(self.root, text="Désactiver Relais", command=self.deactivate_relay)
        self.deactivate_button.pack(side="left", padx=(0, padx_value), pady=pady_value)
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
