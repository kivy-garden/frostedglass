import fps_monitor
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform

from kivy_garden.frostedglass import FrostedGlass  # FrostedGlass import

if platform not in ("android", "ios"):
    Window.size = (480, 854)
    Window.top = 50

Builder.load_file('test.kv')


class UI(FloatLayout):
    pass


class Screen1(Screen):
    pass


class Screen2(Screen):
    pass


class Screen3(Screen):
    pass


class Screen4(Screen):
    pass


class FrostedGlassApp(App):
    def build(self):
        return UI()


fps_monitor.start(Window, FrostedGlassApp)

FrostedGlassApp().run()
