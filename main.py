# importar a bibliotecas 
import os
import sys
from pathlib import Path
from kivy.core.window import Window
from kivy.factory import Factory  # NOQA: F401
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.base import ExceptionManager, ExceptionHandler, EventLoopBase
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from libs.baseclass.fonts import Fonts


# Tratamento de execeção controle geral de todos os erros
class E(ExceptionHandler):
    dialog = None
    def __init__(self,obj):
        self.obj = obj
    def callback_not(self,dt):
        self.stopTouchApp()
        self.dialog.dismiss()
    def msg(self,texto,callback):
        self.obj.root.central.limpar(texto)
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
        Clock.schedule_once(callback, 7)
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
        EventLoop.close()
        
    def handle_exception(self, inst):
        self.msg(str(inst),self.callback_not)
        return ExceptionManager.PASS

# verificação do sistema operacional e apontamento da pasta relativa geral
os.environ["ENGESEP_LANG"] = "1"

if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["ENGESEP_ROOT"] = sys._MEIPASS
else:
    sys.path.append(os.path.abspath(__file__).split("demos")[0])
    os.environ["ENGESEP_ROOT"] = str(Path(__file__).parent)
os.environ["ENGESEP_ASSETS"] = os.path.join(
    os.environ["ENGESEP_ROOT"], f"assets{os.sep}"
)

# Instancia da classe principal através de herança
class EngesepApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ExceptionManager.add_handler(E(self))
        self.title = "EngeSEP"
        self.icon = os.path.join(os.environ["ENGESEP_ASSETS"], "logo.png")
        self.theme_cls.primary_palette = "Teal"
        Window.system_size = [900, 600]
        Window.softinput_mode = "below_target"
        font = 'Oswald-Regular'
        # self.theme_cls.font_styles.update(Fonts()(font))
    def build(self):
        KV_DIR = f"{os.environ['ENGESEP_ROOT']}/libs/kv/"
        for kv_file in os.listdir(KV_DIR):
            with open(os.path.join(KV_DIR, kv_file), encoding="utf-8") as kv:
                build = Builder.load_string(kv.read())
        
        return build
    def rail_open(self):
        pass

    
if __name__ == "__main__":
    app = EngesepApp()
    app.run()
