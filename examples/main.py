import fps_monitor
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.frostedglass import FrostedGlass

Builder.load_file('test.kv')


class UI(FloatLayout):
    pass


class Screen1(Screen):
    pass


class Screen2(Screen):
    pass


class Screen3(Screen):
    pass


class FrostedGlassApp(App):
    def build(self):
        return UI()


fps_monitor.start(Window, FrostedGlassApp)

FrostedGlassApp().run()
