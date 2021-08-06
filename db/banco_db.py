import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import sqlite3
from datetime import datetime
from pytz import timezone
import random
class DB():
    def __init__(self,name='Banco_de_Dados_ENGESEP'):
        self.name = name
        self.name_db = 'usina_db.db'
    def create_connection(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR,self.name_db)
        con = sqlite3.connect(db_path)
        return con
    def list_tables(self):
        con = self.create_connection()
        cursor = con.cursor()
        query_list = "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
        cursor.execute(query_list)
        dados = []
        for linha in cursor.fetchall():
            dados.append(list(linha))
        con.close()
        return dados
    def create_table(self,tabela):
        try:
            con = self.create_connection()
            cursor = con.cursor()
            query = "SELECT name from sqlite_master WHERE type='table' AND name='{" + tabela + "}';"
            result = cursor.execute(query)
            query_create = f"CREATE TABLE IF NOT EXISTS {tabela}(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,energia_a real,energia_b real,id_a text,id_b text,nivel real,cidade text,usina text,criado_em DATE NOT NULL,ts timestamp)"
            test = cursor.execute(query_create)
            if result.fetchone() == None:
                print('tabela nao existe: ',result.fetchone(),test.fetchone())
                return 0
            else:
                print('tabela ja existe: ',result.fetchone(),test.fetchone())
                return 1
        except ValueError:
            print(ValueError)
            return 2

    def seeddb(self):
        con = self.create_connection()
        cursor = con.cursor()
        tabela = 'cgh_seed'
        query_create = f"CREATE TABLE IF NOT EXISTS {tabela}(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,energia_a real,energia_b real,id_a text,id_b text,nivel real,cidade text,usina text,criado_em DATE NOT NULL,ts timestamp)"
        cursor.execute(query_create)
        i = 0
        nivel_m = 1000
        dados = []
        alta = 0
        baixa = 0
        z= 7
        aux = 0
        energia1 = 0
        energia2 = 0
        for ano in range(0,3):
            for mes in range(1, 13):
                for dia in range(1, 32):
                    for horas in range(0, 24):
                        aux = 0
                        for minutos in range(0, 4):
                            try:
                                i += 1
                                ip_a = '198.162.10.3'
                                ip_b = '198.162.10.3'
                                anos = 2019 +ano
                                if anos == 2021 and mes >= 6:
                                    break
                                min_date = datetime(anos, mes, dia, horas, aux, 5, 299)
                                id_a = 'UG-01'
                                id_b = 'UG-02'
                                timestamp = datetime.timestamp(min_date)
                                fuso_horario = timezone('America/Sao_Paulo')
                                min_date = min_date.astimezone(fuso_horario)
                                cidade = "Monte Carlo"
                                usina = "CGH Ponte Caida"
                                if random.randrange(0, 10) < z:
                                    nivel_m = nivel_m - random.randrange(0, 2)
                                    alta += 1
                                else:
                                    baixa += 1
                                    nivel_m = nivel_m + random.randrange(0, 2)
                                aux += 15
                                if anos == 2019:
                                    anoss = anos
                                if anos != anoss:
                                    anoss= anos
                                    print('dados: ', energia1, energia2,ip_a, ip_b, nivel_m, id_a, id_b, cidade, usina,min_date,timestamp, alta,baixa)
                                if nivel_m > 1400:
                                    z = 6
                                if nivel_m < 600:
                                    z = 3
                                query = f"""insert into {tabela} (energia_a,energia_b,id_a,id_b,nivel, cidade, usina, criado_em, ts) values (?,?,?,?,?,?,?,?,?)"""
                                cursor.execute(query, (energia1,energia2,id_a,id_b,nivel_m,cidade,usina,min_date,timestamp))
                                con.commit()
                                energia1 = energia1 + random.randrange(15, 25)
                                energia2 = energia2 + random.randrange(15, 25)
                            except ValueError:
                                pass
        con.close()
        print("Seed Realizado!")

    def inserir(self,tabela,energia_a,energia_b,id_a,id_b,nivel,cidade,usina):
        try:
            con = self.create_connection()
            cursor = con.cursor()
            data = datetime.now()
            fuso_horario = timezone('America/Sao_Paulo')
            data_hora = data.astimezone(fuso_horario)
           # data_hora = data_hora.strftime('%d-%m-%Y %H:%M')
            print(data_hora)
            print(type(data_hora))
            timestamp = datetime.timestamp(data)
            query = f"""insert into {tabela} (energia_a,energia_b,id_a,id_b,nivel, cidade, usina, criado_em, ts) values (?,?,?,?,?,?,?,?,?)"""
            print(timestamp)
            print('----')
            print('nome tabela: ',tabela, type(tabela))
            print('energia a: ',energia_a,type(energia_a))
            print('energia b: ', energia_b, type(energia_b))
            print('id a: ',id_a,type(id_a))
            print('id b: ', id_b, type(id_b))
            print('nivel: ',nivel,type(nivel))
            print('cidade: ',cidade,type(cidade))
            print('query: ',query)

            cursor.execute(query, (energia_a,energia_b,id_a,id_b,nivel,cidade,usina,data_hora,timestamp))
            con.commit()
            con.close()
            print('salvo com sucesso',data_hora,timestamp)
            return 1
        except:
            con.close()
            return 0


    def consulta(self,name_table):
        con = self.create_connection()
        cursor = con.cursor()
        query = f'SELECT * FROM {name_table};'
        cursor.execute(query)
        dados = []
        for linha in cursor.fetchall():
            dados.append(list(linha))
        con.close()
        return dados

    def delete_all(self):
        con = self.create_connection()
        cur = con.cursor()
        for s in self.list_tables():
            sql = f"""DELETE FROM {s[0]}"""
            cur.execute(sql)
            con.commit()
        con.close()
        return True
        
if __name__ == "__main__":
    banco = DB()
    tabelas = banco.list_tables()
    print(tabelas)
    for table in tabelas:
        dados = banco.consulta(table[0])
        print(len(dados))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
