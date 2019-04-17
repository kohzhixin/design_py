from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.clock import Clock

from collections import OrderedDict
import time

import firebase_admin
from firebase_admin import firestore, credentials

cred = credentials.Certificate("C:/Users/kohzh/Downloads/design-8d4ff-firebase-adminsdk-b7b9t-0a11c527ed.json")
app = firebase_admin.initialize_app(cred)

Window.size = (800, 480)

class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.change_face_2(), 30)
    def on_touch_down(self, touch):
        global event
        if self.collide_point(*touch.pos):
            self.manager.current = "menu"
            event = Clock.schedule_once(lambda dt: MenuScreen.return_to_main_start(self), 60)
    def change_face_2(self):
        self.ids.cutepic.source = "cuteface2.png"
        Clock.schedule_interval(lambda dt: self.change_face_1(), 30)
    def change_face_1(self):
        self.ids.cutepic.source = "cuteface.png"
        Clock.schedule_interval(lambda dt: self.change_face_2(), 30)


class MenuScreen(Screen):
    def __init__(self, **kw):
        self.info_clicked = False
        return super().__init__(**kw)
    def switch_page(self, num):
        global event
        event.cancel()
        event = Clock.schedule_once(lambda dt: MenuScreen.return_to_main(self), 60)
        curr_pg = pages.get_curr(self.ids.pages)
        diff = num - curr_pg
        if curr_pg == 1:
            DataBox.clear_widgets(self.ids.info)
        if num == 1:
            DataBox.add(self.ids.info)
        return pages.go_next(self.ids.pages, diff)
    def return_to_main_start(self):
        self.manager.current = "main"
    def return_to_main(self):
        self.ids.menu_toggle.state = "down"
        self.ids.info_toggle.state = "normal"
        self.ids.barcode_toggle.state = "normal"
        self.ids.directory_toggle.state = "normal"
        self.ids.map_toggle.state = "normal"
        self.switch_page(0)
        self.manager.current = "main"
    def read_barcode(self):
        global event
        event.cancel()
        event = Clock.schedule_once(lambda dt: MenuScreen.return_to_main(self), 60)
        string = self.ids.custominput.text
        if len(string) < 10:
            self.ids.dynamictext.text = "Please scan the barcode on your flight ticket"
        else:
            for row in deps.get():
                d = row.to_dict()
                if d["Flight No"] in string:
                    self.ids.dynamictext.text = "Flight Time: {0} \nGate: {1} \nTerminal: {2} \nCheck-in Row/Door: {3}".format(d["Time"], d["Boarding Gate"], d["Terminal"], d["Check-in Row/Door"])
                    return
            self.ids.dynamictext.text = "Flight not found"
    def clear_barcode(self):
        global event
        event.cancel()
        event = Clock.schedule_once(lambda dt: MenuScreen.return_to_main(self), 60)
        self.ids.custominput.text = ""

class sm(ScreenManager):
    pass

class pages(PageLayout):
    def get_curr(self):
        return self.page
    def go_next(self, diff):
        self.page += diff

class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        self.item = None
        return super().__init__(**kwargs)
    def on_press(self):
        if "clicked" not in self.source:
            print("clicked")
        ##self.item = self.source
        ##self.source = "cuteface.png"
            self.source = "clicked" + self.source
        else:
            self.source = self.source[7:]
        global event
        event.cancel()
        event = Clock.schedule_once(lambda dt: MenuScreen.return_to_main(self.parent.parent.parent.parent.parent.parent), 60)

class boxes(BoxLayout):
    def change_text(self, item):
        self.children[1].text += "\n" + item
    def clear_text(self):
        self.children[1].text = "Your order:"

class DataBox(GridLayout):
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)
    def add(self):
        db = firestore.client()
        deps = db.collection("departures_2h")
        curr_time = time.ctime()[11:16]
        keys = ["Status", "Time", "Flight No", "Flight", "To", "Revised Time", "Boarding Gate", "Check-in Row/Door", "Terminal"]
        if len([i for i in deps.get()]) == 0:
            self.add_widget(Label(text="Loading...", font_size="12sp", color=(0, 0, 0, 1)))
            time.sleep(2)
            self.clear_widgets()
        for k in keys:
            self.add_widget(Label(text=str(k), font_size="12sp", color=(0, 0, 0, 1)))
        for row in deps.where(u'Time', u'>=', curr_time).order_by("Time").limit(10).get():
            d = row.to_dict()
            for k in keys:
                v = d[k]
                if "via" in v:
                    i = v.index("via")
                    v = v[:i] + "\n" + v[i:]
                self.add_widget(Label(text=str(v), font_size="12sp", color=(0, 0, 0, 1), halign="center"))

class uwuApp(App):
    def build(self):
        m = sm(transition=FadeTransition())
        return m

if __name__ == "__main__":
    uwuApp().run()

"""
Barcode Scanner String:

"Name" + "Passport No." + "Flight" + "To" + "DDMMYY" + "HHMM" 

Passport No.: A1234567B
Flight: 9C8550
To: HYD

string: A1234567B3K831XUZ
"""