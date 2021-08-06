from time import time

import chardet
import pandas as pd
import sys
import os
from multiprocessing.pool import ThreadPool
import concurrent.futures
import asyncio

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

class registro:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, 'wago_enderecos.xlsx')
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        self.tabela = pd.read_excel(db_path)
    def mapa(self,letras,numero):
        print('buscando no mapa')
        return self.tabela.query(f'{letras} == {numero}')
    def run(self,port_a,port_b,port_c):
        try:
            s1 = port_a.split()[0][0:2]
            s2 = port_a.split()[0][2:6]
            s3 = port_b.split()[0][0:2]
            s4 = port_b.split()[0][2:6]
            s5 = port_c.split()[0][0:2]
            s6 = port_c.split()[0][2:6]
            nivel_registro = int(self.mapa(s5, int(s6)).DEC.values[0])
            energia_Registro_a = int(self.mapa(s1, int(s2)).DEC.values[0])
            energia_Registro_b = int(self.mapa(s3, int(s4)).DEC.values[0])
            return energia_Registro_a,energia_Registro_b,nivel_registro
        except:
            return -1,-1,-1