from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp
from datetime import datetime
import ast
import os
import time


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

        for f, d in sorted(dic_foods.items(), key=lambda x: x[1]):
            if datetime.fromtimestamp(d).strftime('%Y-%m-%d') == datetime.today().strftime('%Y-%m-%d') or not self.Tod:
                fd = f.decode('u8') + ' ' + (datetime.fromtimestamp(d).strftime('%Y-%m-%d'))
                btn = Button(text=fd, size_hint_y=None, height=dp(40))
                self.layout.add_widget(btn)

    def on_enter(self):
        self.build()

    def on_leave(self):

        self.layout.clear_widgets()


class AddFood(Screen):

    def buttonClicked(self, btn1):
        pass

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
        self.result = Label(text='')
        box.add_widget(self.result)
        self.add_widget(box)


class FoodOptionsApp(App):
    def __init__(self, **kvargs):
        super(FoodOptionsApp, self).__init__(**kvargs)

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'user_data', '{}')

    def set_value_from_config(self):
        self.config.read(os.path.join(self.directory, '%(appname)s.ini'))

        self.user_data = ast.literal_eval(self.config.get(
            'General', 'user_data'))

    def get_application_config(self, **kwargs):
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

if __name__ == '__main__':
    FoodOptionsApp().run()
