import time
import unidecode
from kivymd.toast import toast
from db.banco_db import DB
from db.mapa import registro
import concurrent.futures
import time
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

class interface():
    def __init__(self,nome_usina,local,ip_a,ip_b,port_a,port_b,reg_a,reg_b,nivel,tempo,name_table=None):
        self.nome_usina = nome_usina
        self.local =local
        self.ip_a =ip_a
        self.ip_b = ip_b
        self.port_a= port_a
        self.port_b = port_b
        self.reg_a = reg_a
        self.reg_b = reg_b
        self.nivel = nivel
        self.tempo = tempo
        self.adress = None
        self.name_table = name_table
    def existeDB(self):
        try:
            if self.name_table is None:
                self.nome_usina = unidecode.unidecode(self.nome_usina).replace(' ','_')
                name_db = 'usina_'+self.nome_usina
                self.db = DB()
                result = self.db.create_table(name_db)
                toast("Tabela criada com sucesso", duration=5)
                return True
            else:
                self.db = DB()
                return True
        except :
            toast("Erro ao criar a tabela", duration=5)
            return False

    def conectarCLP(self,ip):
        objeto_conexao = ModbusClient(host=ip, auto_open=True, auto_close=True)
        return objeto_conexao

    def leitura(self,objeto,addr_a,nivel):
        objeto.open()
        if objeto.is_open():
            nivel = objeto.read_holding_registers(nivel, 8)
            energia = objeto.read_holding_registers(addr_a, 8)
            # print('valores func: leitura: ',nivel,energia)
            objeto.close()
            return nivel,energia
        else:
            return False,False

    def persistirDados(self,nivel,energia_a,energia_b):
        try:
            print('---------------------------------')
            print('nome da usina: ',self.nome_usina)
            print('local: ',self.local)
            print('Identificação: ', str(self.reg_a))
            print('Ultima medição -'+ str(self.reg_a)+' : ',str(energia_a))
            print('Identificação: ', str(self.reg_b))
            print('Ultima medição -' + str(self.reg_b) + ' : ',str(energia_b))
            print('Nivel d reservatorio: ',str(nivel))
            print('-----------------------------------------------')
            if energia_a is None:
                energia_a = 'NULL'
            else:
                energia_a = float(energia_a)
    
            if energia_b is None:
                energia_b = 'NULL'
            else:
                energia_b = float(energia_b)
            nivel = float(nivel)
            print('¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨')
            print('Energia A: ',energia_a)
            print('Energia B: ',energia_b)
            print('Nível: ',nivel)
            print('¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨')
            
            return self.db.inserir(self.name_table,energia_a,energia_b,self.reg_a,self.reg_b, nivel, self.local,self.nome_usina)
        except ValueError:
            return ValueError
