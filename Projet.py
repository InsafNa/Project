import tkinter as tk
from tkinter import ttk,messagebox
import paho.mqtt.client as mqtt

class MQTTTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Intrusion detection system")
        self.root.geometry("500x300")

        # Configuration MQTT
        self.broker_address = "broker.hivemq.com"
        self.port = 1883
        # Création du style pour les boutons
        self.style = ttk.Style()
        self.style.configure("Custom.TButton", background="#691D91",foreground="#691D91", borderwidth=2, relief="raised")

        # Interface graphique
        self.create_gui()

        # Connexion au serveur MQTT
        self.connect_to_mqtt()

    def create_gui(self):
          # Configuration de la couleur d'arrière-plan
          
        bg_color = "#C2BDE0"
        self.root.configure(bg=bg_color)
        
        padx_value = 20
        pady_value = 10
        
        # Label pour afficher les données
        title_style = {'font': ('Arial', 18,'bold'), 'foreground': '#691D91', 'background': bg_color, 'anchor': 'w'}

        label_style = {'font': ('Arial', 12), 'foreground': '#723E64', 'background': bg_color, 'anchor': 'w'}
        label_style1 = {'font': ('Arial', 16, 'bold'), 'foreground': '#CE0058', 'background': bg_color}
         # Titre des données captées par les capteurs
        self.title_label = ttk.Label(self.root, text=" Captured data ", **title_style)
        self.title_label.pack(pady=pady_value, padx=padx_value)
        
        self.motion_label = ttk.Label(self.root, text="Movement: ", **label_style)
        self.motion_label.pack(pady=(pady_value, 0), padx=padx_value, anchor="w")

        self.light_label = ttk.Label(self.root, text="Luminosity: ", **label_style)
        self.light_label.pack(pady=pady_value, padx=padx_value, anchor="w")

        self.temperature_label = ttk.Label(self.root, text="Temperature: ", **label_style)
        self.temperature_label.pack(pady=pady_value, padx=padx_value, anchor="w")
    
        self.relay_state_label = ttk.Label(self.root, text="", **label_style1)
        self.relay_state_label.pack(pady=pady_value, padx=padx_value)
        
       # self.relay_intrusion_label = ttk.Label(self.root, text="Alert:", **label_style)
        #self.relay_intrusion_label.pack(pady=pady_value, padx=padx_value, anchor="w")
        
         # Conteneur de cadre pour les boutons
        button_frame = ttk.Frame(self.root, padding=(0, pady_value))
        button_frame.pack()
     
           
        self.activate_button = ttk.Button(self.root, text="Activate Relay", command=self.activate_relay, style="Custom.TButton")
        self.activate_button.pack(side="left", padx=(150, padx_value), pady=pady_value)

        self.deactivate_button = ttk.Button(self.root, text="Disable Relay", command=self.deactivate_relay, style="Custom.TButton")
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
        client.subscribe("STATRELAY") 
        client.subscribe("myproject/intrusion")
        
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        if topic == "myproject/motion":
            self.motion_label.config(text=f"Movement: {payload}")
        elif topic == "myproject/lumiere":
            self.light_label.config(text=f"Luminosity: {payload}")
        elif topic == "myproject/temperature":
            self.temperature_label.config(text=f"Temperature: {payload} °C")
        elif topic == "STATRELAY":  
            self.relay_state_label.config(text=f"Relay status: {payload}")
        elif topic == "myproject/intrusion":  
            self.relay_state_label.config(text=f"{payload}")
        
        
         
    def activate_relay(self):
        self.client.publish("topicactivaterelay", "on")

    def deactivate_relay(self):
        self.client.publish("topicactivaterelay", "off")

    def show_alert(self, message, title):
        # Affichage de l'alerte pop-up...
        messagebox.showinfo(title, message)
if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTTestApp(root)
    root.mainloop()
