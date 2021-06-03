from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp
from datetime import datetime
import os
import ast
import time
from googletrans import Translator
import requests
import json


class Product:
    def __init__(self):
        self.Weight = ""
        self.Calories = ""
        self.Proteins = ""
        self.Fats = ""
        self.Carboh = ""
        self.Name = ""


P = Product()


class MenuScreen(Screen):
    def __init__(self, **kw):
        super(MenuScreen, self).__init__(**kw)
        box = BoxLayout(orientation='vertical')
        box.add_widget(Button(text='Дневник питания', on_press=lambda x:
        set_screen('list_food')))
        box.add_widget(Button(text='Добавить продукт в дневник питания',
                              on_press=lambda x: set_screen('add_food')))
        self.add_widget(box)


class SortedListFood(Screen):
    def __init__(self, **kw):
        super(SortedListFood, self).__init__(**kw)
        self.TodayOrNot = Button(text='Сегодня', size_hint_y=None, height=dp(40))
        self.Tod = False

    def Today_func(self, btn):
        self.Tod = not self.Tod
        self.layout.clear_widgets()
        if self.Tod:
            self.TodayOrNot.text = 'Всё время'
        else:
            self.TodayOrNot.text = 'Сегодня'
        self.build()

    def build(self):
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        back_button = Button(text='< Назад в главное меню',
                             on_press=lambda x: set_screen('menu'),
                             size_hint_y=None, height=dp(40))
        self.layout.add_widget(back_button)
        self.TodayOrNot.bind(on_press=self.Today_func)
        self.layout.add_widget(self.TodayOrNot)
        root = RecycleView(size_hint=(1, None), size=(Window.width,
                                                      Window.height))
        root.add_widget(self.layout)
        self.add_widget(root)

        dic_foods = ast.literal_eval(
            App.get_running_app().config.get('General', 'user_data'))
        TodayCalories = 0.0
        TodayProt = 0.0
        TodayFat = 0.0
        TodayCarboh = 0.0
        arr = []
        for f, d in sorted(dic_foods.items(), key=lambda x: x[1], reverse=True):
            if datetime.fromtimestamp(d).strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d') or not self.Tod:
                product = f.decode('u8')
                fd = product + ' ' + (datetime.fromtimestamp(d).strftime('%Y-%m-%d'))
                TodayCalories += float(product[product.find("гр., ") + 5:product.find("ккал") - 1])
                TodayProt += float(product[product.find("ккал, ") + 6:product.find("белк") - 1])
                TodayFat += float(product[product.find("белк, ") + 6:product.find("жир") - 1])
                TodayCarboh += float(product[product.find("жир, ") + 5:product.find("углв") - 1])
                btn = Button(text=fd, size_hint_y=None, height=dp(40))
                arr.append(btn)
        if self.Tod:
            btn1 = Button(text="За сегодня вы съели: %s ккал, %s белк, %s жир, %s углв"
                               % (TodayCalories, TodayProt, TodayFat, TodayCarboh), size_hint_y=None, height=dp(40))
            self.layout.add_widget(btn1)
        for i in arr:
            self.layout.add_widget(i)

    def on_enter(self):
        self.build()

    def on_leave(self):
        self.layout.clear_widgets()


class LibraryFood(Screen):
    def __init__(self, **kw):
        super(LibraryFood, self).__init__(**kw)
        self.Liblayout = GridLayout(cols=1, spacing=10, size_hint_y=1)
        self.Liblayout.bind(minimum_height=self.Liblayout.setter('height'))
        self.back_button = Button(text='< Назад',
                                  on_press=lambda x: set_screen('add_food'),
                                  size_hint_y=None, height=dp(40))
        self.Seach_Text = TextInput(text='', multiline=False, height=dp(40),
                                    size_hint_y=None, hint_text="Поиск")
        self.Seach_Btn = Button(text='Поиск', size_hint_y=None, height=dp(40))
        self.Seach_Btn.bind(on_press=self.Search_Func)
        self.Liblayout.add_widget(self.back_button)
        self.Liblayout.add_widget(self.Seach_Text)
        self.Liblayout.add_widget(self.Seach_Btn)
        self.Buflayout = GridLayout(cols=1, spacing=10, size_hint_y=0.75)
        self.add_widget(self.Buflayout)
        self.add_widget(self.Liblayout)

    def on_enter(self):
        self.Seach_Text.text = ''
        self.Buflayout.clear_widgets()

    def Choice(self, btn):
        product = btn.text
        global P
        P.Name = product[0:product.find("(")]
        P.Weight = product[product.find("(") + 1:product.find(" ", product.find("("))]
        P.Calories = product[product.find("гр., ") + 5:product.find("ккал") - 1]
        P.Proteins = product[product.find("ккал, ") + 6:product.find("белк") - 1]
        P.Fats = product[product.find("белк, ") + 6:product.find("жир") - 1]
        P.Carboh = product[product.find("жир, ") + 5:product.find("углв") - 1]
        set_screen('add_food')

    def Search_Func(self, btn):
        Product = self.Seach_Text.text
        translator = Translator()
        result = translator.translate(Product)
        link = 'https://api.nal.usda.gov/fdc/v1/foods/search?query=%s' \
               '&pageSize=5&api_key=BZeMvKQVspWyoAgB3wJxy1MXdq6Ot5WNgvD3K5Bf' % result.text
        #print(link)
        try:
            if requests.get(link).ok:
                response = requests.get(link).text
                response = json.loads(response)
                response = response['foods']
                for i in range(len(response)):
                    prod = Product + "(%s гр., %s ккал, %s белк, %s жир, " \
                                     "%s углв)" % ("100", response[i]['foodNutrients'][3]['value'],
                                                   response[i]['foodNutrients'][0]['value'],
                                                   response[i]['foodNutrients'][1]['value'],
                                                   response[i]['foodNutrients'][2]['value'])
                    btn = Button(text=prod, size_hint_y=None, height=dp(40))
                    btn.bind(on_press=self.Choice)
                    self.Buflayout.add_widget(btn)
        except:
            pass


class AddFood(Screen):

    def Prep(self, znach):
        try:
            return round((float(znach) / 100) * float(self.Weight.text))
        except:
            return 0

    def buttonClicked(self, btn1):
        if not self.txt1.text or not self.Calories.text \
                or not self.Protein.text or not self.Fat.text or not self.Carboh.text or not self.Weight.text:
            return
        text = self.txt1.text + "(%s гр., %s ккал, %s белк, %s жир, %s углв)" % (self.Weight.text,
                                                                                 self.Prep(self.Calories.text),
                                                                                 self.Prep(self.Protein.text),
                                                                                 self.Prep(self.Fat.text),
                                                                                 self.Prep(self.Carboh.text))
        self.result.text = text
        self.app = App.get_running_app()
        self.app.user_data = ast.literal_eval(
            self.app.config.get('General', 'user_data'))
        self.app.user_data[self.result.text.encode('u8')] = int(time.time())

        self.app.config.set('General', 'user_data', self.app.user_data)
        self.app.config.write()
        self.result.text = "Последний добавленный продукт: " + text
        self.txt1.text = ''
        self.Carboh.text = ''
        self.Fat.text = ''
        self.Weight.text = ''
        self.Protein.text = ''
        self.Calories.text = ''

    def __init__(self, **kw):
        super(AddFood, self).__init__(**kw)
        box = BoxLayout(orientation='vertical')
        back_button = Button(text='< Назад в главное меню', on_press=lambda x:
        set_screen('menu'), size_hint_y=None, height=dp(40))
        box.add_widget(back_button)
        self.txt1 = TextInput(text='', multiline=False, height=dp(40),
                              size_hint_y=None, hint_text="Название продукта")
        box.add_widget(self.txt1)
        self.Calories = TextInput(text='', multiline=False, height=dp(40),
                                  size_hint_y=None, hint_text="Калории(на 100гр.)")
        box.add_widget(self.Calories)
        self.Protein = TextInput(text='', multiline=False, height=dp(40),
                                 size_hint_y=None, hint_text="Белки(на 100гр.)")
        box.add_widget(self.Protein)
        self.Fat = TextInput(text='', multiline=False, height=dp(40), size_hint_y=None, hint_text="Жиры(на 100гр.)")
        box.add_widget(self.Fat)
        self.Carboh = TextInput(text='', multiline=False, height=dp(40),
                                size_hint_y=None, hint_text="Углеводы(на 100гр.)")
        box.add_widget(self.Carboh)
        self.Weight = TextInput(text='', multiline=False, height=dp(40),
                                size_hint_y=None, hint_text="Масса(грамм)")
        box.add_widget(self.Weight)
        AddBtn = Button(text="Добавить продукт", size_hint_y=None, height=dp(40))
        AddBtn.bind(on_press=self.buttonClicked)
        box.add_widget(AddBtn)
        LibBtn = Button(text="Библиотека продуктов", size_hint_y=None, height=dp(40),
                        on_press=lambda x: set_screen('lib_food'))
        box.add_widget(LibBtn)
        self.result = Label(text='')
        box.add_widget(self.result)
        self.add_widget(box)

    def on_enter(self):
        global P
        self.txt1.text = P.Name
        self.Fat.text = P.Fats
        self.Carboh.text = P.Carboh
        self.Weight.text = P.Weight
        self.Protein.text = P.Proteins
        self.Calories.text = P.Calories
        P = Product()


class FoodOptionsApp(App):
    def __init__(self, **kvargs):
        super(FoodOptionsApp, self).__init__(**kvargs)
        self.config = ConfigParser()

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'user_data', '{}')

    def set_value_from_config(self):
        self.config.read(os.path.join(self.directory, '%(appname)s.ini'))
        self.user_data = ast.literal_eval(self.config.get(
            'General', 'user_data'))

    def get_application_config(self):
        return super(FoodOptionsApp, self).get_application_config(
            '{}/%(appname)s.ini'.format(self.directory))

    def build(self):
        return sm


def set_screen(name_screen):
    sm.current = name_screen


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(SortedListFood(name='list_food'))
sm.add_widget(AddFood(name='add_food'))
sm.add_widget(LibraryFood(name='lib_food'))

if __name__ == '__main__':
    FoodOptionsApp().run()
