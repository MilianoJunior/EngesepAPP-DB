
from datetime import datetime
import time
from db.banco_db import DB
from db.mapa_asyncio import Registro
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from interface import interface
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex
import concurrent.futures
from threading import Thread, Lock
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelThreeLine
from kivy.properties import ObjectProperty,NumericProperty
import asyncio
import random
import asynckivy as ak
from kivy.properties import StringProperty
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import Screen
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.base import ExceptionManager, ExceptionHandler, EventLoopBase
from kivy.logger import Logger, LOG_LEVELS
from kivy.logger import LoggerHistory


class E(ExceptionHandler):
    dialog = None
    def __init__(self,reset):
        self.reset = reset
        pass
    def callback_not(self,dt):
        self.stopTouchApp()
        self.dialog.dismiss()
    def msg(self,texto,callback):
        if not self.dialog:
            self.dialog = MDDialog(
                text=texto,
                buttons=[
                    MDFlatButton(
                        text="OK", text_color=get_color_from_hex("#27979d"), on_release= callback
                    ),
                ],
            )
        self.dialog.open()
    def stopTouchApp(self):
        EventLoop = EventLoopBase()
        '''Stop the current application by leaving the main loop'''
        if EventLoop is None:
            return
        if EventLoop.status in ('stopped', 'closed'):
            return
        if EventLoop.status != 'started':
            if not EventLoop.stopping:
                EventLoop.stopping = True
                Clock.schedule_once(lambda dt: self.stopTouchApp(), 0)
            return
        Logger.info('Base: Leaving application in progress...')
        EventLoop.close()
        
    def handle_exception(self, inst):
        Logger.exception('Exception catched by ExceptionHandler')
        self.reset()
        self.msg(str(inst),self.callback_not)
        return ExceptionManager.PASS


class EngesepAPP(MDApp):
    dialog = None
    nome_usina = None 
    local = None 
    name_table = None
    R0 = 0
    R1 = 0
    R2 = 0
    R3 = 0
    alerta = 0
    clpa = False
    clpb= False
    energia_a = 'None' 
    energia_b = 'None'
    nivel_a = 'None' 
    nivel_b = 'None'
    text_register = StringProperty()
    one = True
    
    def __init__(self, **kwargs):
        super(EngesepAPP, self).__init__(**kwargs)
        Window.soft_input_mode = "below_target"
        self.title = "Engesep "

        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.primary_hue = "500"

        self.theme_cls.accent_palette = "Cyan"
        self.theme_cls.accent_hue = "500"

        self.theme_cls.theme_style = "Light"
        

    def build(self):
        self.conectado = False
        ExceptionManager.add_handler(E(self.reset))       
        return Builder.load_file("extensaoback.kv")
    def reset(self):
        self.conectar()
        print('testando')
    def close_application(self):
        # closing application
        MDApp.get_running_app().stop()

    def on_save(self, instance, value, date_range):
        pass

    def rail_open(self):
        if self.root.ids.rail.rail_state == "open":
            self.root.ids.rail.rail_state = "close"
        else:
            self.root.ids.rail.rail_state = "open"
    def msg(self,texto,callback):
        if not self.dialog:
            self.dialog = MDDialog(
                text=texto,
                buttons=[
                    MDFlatButton(
                        text="OK", text_color=self.theme_cls.primary_color, on_release= callback
                    ),
                ],
            )
        self.dialog.open()
    def on_start(self):
        try:
            self.db = DB()
            tabelas = self.db.list_tables()
            for table in tabelas:
                dados = self.db.consulta(table[0])
                if len(dados) > 0:
                    msg_ = f'Usina com banco de dados ativo, não é possível criar nova tabela.'
                    self.local = dados[0][6]
                    self.nome_usina = dados[0][7]
                    self.name_table = table[0]
                    self.msg(msg_,self.callback_set)
                    return
            msg_ = f'Usina não possui banco de dados, preencha todos os campos.'
        except ValueError:
            self.msg('Erro ao iniciar o software: '+ ValueError,self.callback_not)
        
        self.msg(msg_,self.callback_not)
    def callback_not(self,dt):
        self.dialog.dismiss()
    def callback_set(self,dt):
        self.root.ids.nome.hint_text = self.nome_usina
        self.root.ids.nome.normal_color= get_color_from_hex("#F72808")
        self.root.ids.nome.disabled = True
        self.root.ids.local.hint_text = self.local
        self.root.ids.local.normal_color= get_color_from_hex("#F72808")
        self.root.ids.local.disabled = True
        self.dialog.dismiss()
    def registros_text(self):
        self.md_box_a = MDBoxLayout(orientation='horizontal',size=(200,0), size_hint=(None, 1))
        for i in range(0,4):
            self.input_text = MDTextField(hint_text="R" +str(i),
                                          pos_hint={'center_x':0.5,'center_y':0.5},
                                          size_hint =(None, 0.2),width=50,current_hint_text_color= get_color_from_hex("#27e548"))
            self.input_text.bind(text=self.on_text)
            self.md_box_a.add_widget(self.input_text)
        self.root.ids.registros.add_widget(self.md_box_a)
        
    def setar_registro(self,dt):
        try:
            for c in list(self.root.ids):
                if c ==  'panel_read': 
                    self.root.ids.registros.remove_widget(self.root.ids.panel_read)
            self.md_box_b = MDBoxLayout(orientation='horizontal')
            self.root.ids['panel_read']= self.md_box_b
            array_text = ['CLP1 E','CLP1 N','CLP2 E','CLP2 N']
            for i in range(0,4):
                self.md_label = MDTextField(text=self.text_register,
                                            hint_text=array_text[i],
                                            pos_hint={'center_x':0.5,'center_y':0.5},
                                            size_hint =(0.5, 1),
                                            current_hint_text_color= get_color_from_hex("#27e548"),
                                            font_size="8sp")
                self.root.ids['n'+str(i)] = self.md_label 
                self.md_box_b.add_widget(self.md_label)
            self.root.ids.registros.add_widget(self.md_box_b)
        except ValueError:
            self.msg('Houve erro no setar o registro, código: '+ ValueError,self.callback_not)
        
    def on_text(self,instance, value):
        try:
            value_text = instance.hint_text 
            value = int(value) if value.isnumeric() else -1
            setattr(self, instance.hint_text , int(value))
            if isinstance(self.energia_a,list) and self.R0 != -1 and self.R0 < 8:
                self.root.ids.n0.text = str(self.energia_a[self.R0])
                self.root.ids.n0.font_size="14sp"
            else:
                self.root.ids.n0.text = ":".join(str(x) for x in self.energia_a) if isinstance(self.energia_a,list) else 'sem leitura'
                self.root.ids.n0.font_size="8sp"
            #--------------------------------------------------------------------          
            if isinstance(self.nivel_a,list) and self.R1 != -1 and self.R1 < 8:
                self.root.ids.n1.text = str(self.nivel_a[self.R1])
                self.root.ids.n1.font_size="14sp"
            else:
                self.root.ids.n1.text = ":".join(str(x) for x in self.nivel_a) if isinstance(self.nivel_a,list) else 'sem leitura'
                self.root.ids.n1.font_size="8sp"
                
            if isinstance(self.energia_b,list) and self.R2 != -1 and self.R2 < 8:
                self.root.ids.n2.text = str(self.energia_b[self.R2])
                self.root.ids.n2.font_size="14sp"
            else:
                self.root.ids.n2.text = ":".join(str(x) for x in self.energia_b) if isinstance(self.energia_b,list) else 'sem leitura'
                self.root.ids.n2.font_size="8sp"
                
            if isinstance(self.nivel_b,list) and self.R3 != -1 and self.R3 < 8:
                self.root.ids.n3.text = str(self.nivel_b[self.R3])
                self.root.ids.n3.font_size="14sp"
            else:
                self.root.ids.n3.text = ":".join(str(x) for x in self.nivel_b) if isinstance(self.nivel_b,list) else 'sem leitura'
                self.root.ids.n3.font_size="8sp"
        except ValueError:
            self.msg('Houve erro no setar o registro, código: '+ ValueError,self.callback_not)
    def leitura(self,dt):
        try:
            a = None;self.nivel_a= None 
            b = None;self.nivel_b = None 
            c = None;self.energia_b = None
            d = None;self.energia_a = None
            if self.conectado:
                if self.clpa:
                    self.energia_a,self.nivel_a = self.drive.leitura(objeto=self.clp1,addr_a=self.r1,nivel=self.n1)
                    pa = True
                else:
                    pa = False
                if self.clpb:
                    self.energia_b,self.nivel_b = self.drive.leitura(objeto=self.clp2,addr_a=self.r2,nivel=self.n1)
                    pb = True
                else:
                    pb = False
                self.root.ids.conectado.title = f"Conectado:  IP1 {self.root.ids.ip_a.text} : {pa}       IP2 {self.root.ids.ip_b.text} : {pb}"
                self.root.ids.conectado.md_bg_color = get_color_from_hex("#209F7E")
                
                # self.energia_a[5]=189
                # self.nivel_a[5]=562889
                array = [self.energia_a,self.nivel_a,self.energia_b,self.nivel_b]
                print(array)
                if self.one:
                    self.one = False
                    self.root.ids.n0.text = ":".join(str(x) for x in self.energia_a) if isinstance(self.energia_a,list) else 'sem leitura'
                    self.root.ids.n1.text = ":".join(str(x) for x in self.nivel_a) if isinstance(self.nivel_a,list) else 'sem leitura'
                    self.root.ids.n2.text = ":".join(str(x) for x in self.energia_b) if isinstance(self.energia_b,list) else 'sem leitura'
                    self.root.ids.n3.text = ":".join(str(x) for x in self.nivel_b) if isinstance(self.nivel_b,list) else 'sem leitura'
            else:
                return False
            try:
                if not self.energia_a is None and  not self.nivel_a is None:
                    # persistir os dados
                    a = array[0][self.R0]
                    c = array[1][self.R1]
    
                if not self.energia_b is None and  not self.nivel_b is None:
                    pass
                    b = array[2][self.R2]
                    d = array[3][self.R3]
            except:
                self.msg('Escolha um numero inteiro de 1 a 8 para o registro',self.callback_not)
        except ValueError:
            self.msg('Houve erro na leitura dos dados, código: '+ ValueError,self.callback_not)
                # persistir os dados
        try:
            if self.clpa or self.clpb:
                if not isinstance(a,int):
                    a = None
                if not isinstance(b,int):
                    b = None
                if not isinstance(c,int):
                    c = None
                if not isinstance(d,int):
                    d = None
                if not c is None and c > 0:
                    c = c
                if not d is None and d > 0:
                    c = d
                self.drive.persistirDados(nivel=c,energia_a=a,energia_b=b)
        except ValueError:
            self.msg('Houve erro no armazenamento de dados, código: '+ ValueError,self.callback_not)
            
        
    def conectar(self):
        if self.conectado:
            try:
                self.one = True
                self.conectado = False
                self.leitura(10)
                self.root.ids.ligar.text = "Conectar"
                self.root.ids.ligar.md_bg_color = get_color_from_hex("#27979d")
                self.root.ids.conectado.title = "Configurações de CLP e Banco de dados - Desconectado"
                self.root.ids.conectado.md_bg_color = get_color_from_hex("#4F4F4F")
                return
            except ValueError:
                self.msg('Houve erro no armazenamento de dados, código: '+ ValueError,self.callback_not)            
        else:
            try:
                self.nome_usina = self.root.ids.nome.text if self.nome_usina is None else self.nome_usina
                self.local = self.root.ids.local.text if self.local is None else self.local
                self.ip_a = self.root.ids.ip_a.text
                self.ip_b = self.root.ids.ip_b.text
                port_a = self.root.ids.port_a.text
                port_b = self.root.ids.port_b.text
                reg_a = self.root.ids.id_a.text
                reg_b = self.root.ids.id_b.text
                nivel = self.root.ids.nivel.text
                self.tempo = self.root.ids.tempo.text
                if self.tempo == '99999':
                    db = DB()
                    db.delete_all()
                    self.root.ids.conectado.title = "Dados deletados com sucesso: crie uma nova tabela"
                    self.root.ids.conectado.md_bg_color = get_color_from_hex("#08F7B8")
                    return 
                entradas = [self.nome_usina,self.local,self.ip_a,self.ip_b,port_a,port_b,reg_a,reg_b,nivel,self.tempo]
                for entrada in entradas:
                    if entrada == '':
                        self.root.ids.conectado.title = "Desconectado - Todos os valores devem ser preenchidos!"
                        self.root.ids.conectado.md_bg_color = get_color_from_hex("#DC143C")
                        return 0
                self.root.ids.conectado.title = "Conectando..."
                self.root.ids.conectado.md_bg_color = get_color_from_hex("#08F7B8")
                print(self.nome_usina,self.local,self.ip_a,self.ip_b,port_a,port_b,reg_a,reg_b,nivel,self.tempo)
                if self.name_table is None:
                    self.drive = interface(self.nome_usina,self.local,self.ip_a,self.ip_b,port_a,port_b,reg_a,reg_b,nivel,self.tempo)
                else:
                    self.drive = interface(self.nome_usina,self.local,self.ip_a,self.ip_b,port_a,port_b,reg_a,reg_b,nivel,self.tempo,self.name_table)
                    
                passo_one = self.drive.existeDB()
                if not passo_one:
                    return
                print('passo um')         
                def criar_registro():
                    return Registro()
                def criar_conexao1():
                    clp1 = self.drive.conectarCLP(self.ip_a) 
                    clp1.open()
                    if clp1.is_open():
                        self.clpa= True
                        clp1.close()
                    return clp1
                def criar_conexao2():
                    clp2 = self.drive.conectarCLP(self.ip_b) 
                    clp2.open()
                    if clp2.is_open():
                        self.clpb= True
                        clp2.close()
                    return clp2
                async def task_A(port_a,port_b,nivel):
                    with concurrent.futures.ThreadPoolExecutor() as executer:
                        inicio = time.time()
                        obj = await ak.run_in_executer(criar_registro, executer)
                        self.r1,self.r2,self.n1 = obj.run(port_a,port_b,nivel)
                        self.clp1 = await ak.run_in_executer(criar_conexao1, executer)
                        self.clp2 = await ak.run_in_executer(criar_conexao2, executer)
                        fim = time.time()
                        print(' Tempo gasto para se conectar no ASYNC: ',fim - inicio)
                        if self.clpa or self.clpb:
                            self.setar_registro(10)
                            self.registros_text()
                            self.leitura(10)
                            self.event = Clock.schedule_interval(self.leitura, int(self.tempo))
                            self.conectado = True
                            self.root.ids.conectado.title = "Conectado"
                            self.root.ids.conectado.md_bg_color = get_color_from_hex("#08F7B8")
                            self.root.ids.ligar.text = "Desconectar"
                            self.root.ids.ligar.md_bg_color = get_color_from_hex("#4F4F4F")
                        else:
                            self.root.ids.conectado.title = "Desconectado - ips não encontrado!"
                            self.root.ids.conectado.md_bg_color = get_color_from_hex("#DC143C")
                            self.root.ids.ip_a.md_bg_color = get_color_from_hex("#DC143C")
                            self.root.ids.ip_b.md_bg_color = get_color_from_hex("#DC143C")
                inicio = time.time()
                ak.start(task_A(port_a,port_b,nivel))
                fim = time.time()
                print(' Tempo gasto para se conectar no OBJ 2: ',fim - inicio)
            except ValueError:
                self.msg('Houve erro na conexão, código: '+ ValueError,self.callback_not)
            
 

if __name__ == "__main__":
    EngesepAPP().run()


