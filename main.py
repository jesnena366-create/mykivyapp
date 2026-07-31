from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class DemoApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        self.label = Label(text="Tap the button", font_size=32)
        button = Button(text="Tap me", font_size=28, size_hint=(1, 0.4))
        button.bind(on_press=self.on_tap)
        layout.add_widget(self.label)
        layout.add_widget(button)
        return layout

    def on_tap(self, instance):
        self.count = getattr(self, "count", 0) + 1
        self.label.text = f"Count: {self.count}"


if __name__ == "__main__":
    DemoApp().run()
