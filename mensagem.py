from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import urllib



    
def inicio():
    navegador = webdriver.Chrome()
    navegador.get("https://web.whatsapp.com/")
    while len(self.navegador.find_elements_by_id("side")) < 1:
        time.sleep(1)


inicio()


def enviar(self,mensagem):
    
    pessoa = 'Leticia'
    numero = '554991253417'
    texto = urllib.parse.quote(f"Oi {pessoa}! {mensagem}")
    link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"
    self.navegador.get(link)
    while len(self.navegador.find_elements_by_id("side")) < 1:
        time.sleep(1)
    self.navegador.find_element_by_xpath('/html/body/div/div[1]/div[1]/div[4]/div[1]/footer/div[1]/div[2]/div/div[2]').send_keys(Keys.ENTER)
    time.sleep(10)
        



oenviar('mensagem automatica')
