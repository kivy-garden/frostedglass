"""
============
FrostedGlass
============

FrostedGlass is a widget with translucent frosted glass effect, that
creates a context with the background behind it.

The effect created is based on the widget/layout passed in as the background.
You can control the blur size, saturation, luminosity, overlay color, noise
opacity, border radius and the outline (color and width).
"""

__all__ = ("FrostedGlass",)

from ._version import __version__

import kivy
kivy.require('2.2.0')

import os
from time import perf_counter as now

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import (
    BindTexture,
    ClearBuffers,
    ClearColor,
    Color,
    Fbo,
    Rectangle,
    RenderContext,
    RoundedRectangle,
    Scale,
    SmoothLine,
    Translate,
)
from kivy.metrics import dp
from kivy.properties import (
    ColorProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.floatlayout import FloatLayout

# Used for type checking
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.video import Video

MEAN_RES = (Window.width + Window.height) / 2


vertical_blur_shader = """
#ifdef GL_ES
    precision lowp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;

uniform float mean_res;
uniform float blur_size;

vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{{
    float dt = ((blur_size / 2.0) * 1.0 / mean_res);
    vec4 sum = vec4(0.0);

    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y+3.0*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y+2.5*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y+2.0*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y+1.5*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y+1.0*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y+0.5*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y-0.5*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y-1.0*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y-1.5*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y-2.0*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y-2.5*dt))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y-3.0*dt))*0.077;

    return frag_color * vec4(sum.rgba);
}}

void main (void){
  vec4 normal_color = frag_color * texture2D(texture0, tex_coord0);
  vec4 effect_color = effect(
      normal_color, texture0, tex_coord0, gl_FragCoord.xy
  );
  gl_FragColor = effect_color;
}
"""


horizontal_blur_shader = """
#ifdef GL_ES
    precision lowp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;

uniform float mean_res;
uniform float blur_size;

vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{{
    float dt = (blur_size / 2.0) * 1.0 / mean_res;
    vec4 sum = vec4(0.0);

    sum += texture2D(texture, vec2(tex_coords.x+3.0*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x+2.5*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x+2.0*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x+1.5*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x+1.0*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x+0.5*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x-0.5*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x-1.0*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x-1.5*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x-2.0*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x-2.5*dt, tex_coords.y))*0.077;
    sum += texture2D(texture, vec2(tex_coords.x-3.0*dt, tex_coords.y))*0.077;

    return  frag_color * vec4(sum.rgba);
}}

void main (void){
  vec4 normal_color = frag_color * texture2D(texture0, tex_coord0);
  vec4 effect_color = effect(
      normal_color, texture0, tex_coord0, gl_FragCoord.xy
  );
  gl_FragColor = effect_color;
}
"""


noise_shader = """
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;


vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{{
    vec4 sum = vec4(0.0);
    float a = 12.9898;
    float b = 78.233;
    float c = 43758.5453;
    float dt2 = dot(tex_coords.xy, vec2(a, b));
    float sn= mod(dt2, 3.14);
    vec4 noise = vec4(fract(sin(sn) * c));

    vec4 bg = texture2D(texture0, tex_coord0);
    sum = mix(bg, vec4(noise.xyz, 1.0), 1.0);

    return vec4(sum.rgba);
}}

void main (void){
  vec4 normal_color = frag_color * texture2D(texture0, tex_coord0);
  vec4 effect_color = effect(
      normal_color, texture0, tex_coord0, gl_FragCoord.xy
  );
  gl_FragColor = effect_color;
}
"""


final_shader_effect = """
#ifdef GL_ES
    precision highp float;
#endif

$HEADER$

uniform int add_child_texture;
uniform float opacity;
uniform float luminosity;
uniform float saturation;
uniform float noise_opacity;
uniform vec2 position;
uniform vec2 resolution;
uniform vec4 color_overlay;
uniform sampler2D texture1;
uniform sampler2D texture2;

void main(void)
{
    vec2 pos = (gl_FragCoord.xy - position.xy) / resolution.xy;
    float noise = 0.0;
    vec4 textureResult = vec4(0.0);
    vec4 effect_texture = texture2D(texture1, pos);
    vec4 noise_texture = texture2D(texture2, tex_coord0);

    const vec3 W = vec3(0.2125, 0.7154, 0.0721);
    vec3 intensity = vec3(dot(effect_texture.rgb, W));
    effect_texture = vec4(mix(intensity, effect_texture.rgb, saturation), 1.0);
    effect_texture *= luminosity;

    effect_texture = mix(
        effect_texture.rgba,
        vec4(color_overlay.rgb, 1.0),
        min(1.0, color_overlay.a)
    );
    effect_texture = mix(
        effect_texture.rgba,
        vec4(noise_texture.rgb, 1.0),
        min(1.0, noise_opacity)
    );

    gl_FragColor = vec4(effect_texture.rgb, opacity);
}
"""


class VerticalBlur(Fbo):
    def __init__(self, *args, **kwargs):
        super(VerticalBlur, self).__init__(
            *args, fs=vertical_blur_shader, **kwargs
        )
        self["mean_res"] = MEAN_RES
        self["blur_size"] = dp(25)


class HorizontalBlur(Fbo):
    def __init__(self, *args, **kwargs):
        super(HorizontalBlur, self).__init__(
            *args, fs=horizontal_blur_shader, **kwargs
        )
        self.rect = Rectangle()
        self["mean_res"] = MEAN_RES
        self["blur_size"] = dp(25)


class Noise(Fbo):
    def __init__(self, *args, **kwargs):
        super(Noise, self).__init__(*args, fs=noise_shader, **kwargs)
        self.rect = Rectangle()


class FrostedGlass(FloatLayout):

    background = ObjectProperty(None, allownone=True)

    """Target widget/layout that will be used as a background to FrostedGlass.
    The recomended way to pass the widget is through the id.

    :attr:`background` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None."""

    blur_size = NumericProperty(25)
    """Size of the gaussian blur aplied to the background.

    Note: Do not pass relative values such as dp or sp. FrostedGlass already
    manages this automatically, according to the device's screen density.

    :attr:`blur_size` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 25."""

    noise_opacity = NumericProperty(0.1)
    """Opacity of the noise layer.

    :attr:`noise_opacity` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0.1."""

    saturation = NumericProperty(1.2)
    """Saturation boost that will be aplied to the background.

    :attr:`saturation` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 1.2."""

    luminosity = NumericProperty(1.3)
    """Luminosity boost that will be aplied to the background.

    :attr:`luminosity` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 1.3."""

    overlay_color = ColorProperty([0.5, 0.5, 0.5, 0.5])
    """Color/tint overlay that will be aplied over the background.

    :attr:`overlay_color` is a :class:`~kivy.properties.ColorProperty` and
    defaults to [0.5, 0.5, 0.5, 0.35]."""

    border_radius = ListProperty([0, 0, 0, 0])
    """Specifies the radius used for the rounded corners clockwise:
    top-left, top-right, bottom-right, bottom-left.

    :attr:`border_radius` is a :class:`~kivy.properties.ListProperty` and
    defaults to [0, 0, 0, 0]."""

    outline_color = ColorProperty([1.0, 1.0, 1.0, 1.0])
    """FrostedGlass outline color.

    :attr:`outline_color` is a :class:`~kivy.properties.ColorProperty` and
    defaults to [1.0, 1.0, 1.0, 1.0]."""

    outline_width = NumericProperty(1)
    """FrostedGlass outline width.

    :attr:`outline_width` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 1."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fbind = self.fbind
        fbind("outline_width", self._update_canvas)
        fbind("outline_color", self._update_canvas)
        fbind("border_radius", self._update_canvas)
        fbind("noise_opacity", self.update_effect)
        fbind("luminosity", self.update_effect)
        fbind("saturation", self.update_effect)
        fbind("overlay_color", self.update_effect)
        fbind("border_radius", self.update_effect)

        self.frosted_glass_effect = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True,
            fs=final_shader_effect
        )
        with self.frosted_glass_effect:
            self.bt_1 = BindTexture(index=1)
            self.bt_2 = BindTexture(index=2)
            self.fbo_rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=self.border_radius,
            )
        self.frosted_glass_effect["texture1"] = 1
        self.frosted_glass_effect["texture2"] = 2

        self.canvas.add(self.frosted_glass_effect)

        with self.canvas:
            self._outline_color = Color(rgba=self.outline_color)
            self.outline = SmoothLine(
                width=1,
                overdraw_width=2,
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    1, 1, 1, 1, 45,
                ),
            )

        self.noise = Noise(size=(100, 100))
        self.h_blur = HorizontalBlur(size=(100, 100))
        self.v_blur = VerticalBlur(size=(100, 100))

        with self.h_blur:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            self.h_blur_scale = Scale(1, 1, 1)
            self.h_blur_translate = Translate(0, 0)

        with self.v_blur:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            self.v_blur_scale = Scale(1, 1, 1)
            self.v_blur_translate = Translate(0, 0)

        self.last_value = 0
        self.last_update_time = 0
        self.last_value_list = [0, 0]
        self.last_blur_size_value = None
        self.last_fbo_pos = [None, None]
        self._pos = [0, 0]
        self.popup_parent = None
        self.parent_screen = None
        self.parents_list = []
        self.background_children_list = []
        self.background_parents_list = []
        self._last_background_canvas = None

        self.is_movable = False
        self.adapted_fbo_size = False

        self._update_glsl_ev = Clock.create_trigger(self._update_glsl, 0)
        self._update_fbo_ev = Clock.create_trigger(self._update_fbo_effect, 0)
        self._update_texture_ev = Clock.create_trigger(
            self._set_final_texture, 0
        )
        self._refresh_effect_ev = Clock.create_trigger(
            self.refresh_effect, 0.033333, True
        )

        if not os.environ.get("FG_ASK_UPDATE_CANVAS_ACTIVE"):
            os.environ["FG_ASK_UPDATE_CANVAS_ACTIVE"] = "1"
            Clock.schedule_interval(lambda dt: Window.canvas.ask_update(), 0)

    def update_effect(self, *args):
        self._update_glsl_ev()

    def refresh_effect(self, *args):
        self._update_fbo_ev()
        self._update_glsl_ev()

    def _update_glsl(self, *args):
        self._pos = self.to_window(*self.pos)
        if (
            self.not_current_screen
            or self.out_of_the_window
            and self.background_loaded
        ):
            return

        effect = self.frosted_glass_effect
        effect["position"] = [float(v) for v in self._pos]
        effect["resolution"] = [float(v) for v in self.size]
        effect["luminosity"] = float(self.luminosity)
        effect["saturation"] = float(self.saturation)
        effect["noise_opacity"] = float(self.noise_opacity)
        effect["color_overlay"] = [float(v) for v in self.overlay_color]

        if self.is_movable:
            if not self.adapted_fbo_size:
                self.refresh_effect()
                self.adapted_fbo_size = True

            self.h_blur_translate.x = self.v_blur_translate.x = -self._pos[0]
            self.h_blur_translate.y = self.v_blur_translate.y = (
                -self._pos[1] - self.size[1]
            )

        self._update_texture_ev()

    def _set_final_texture(self, pos):
        if not self.background:
            return

        if self._last_background_canvas not in self.h_blur.children:
            self.h_blur.add(self._last_background_canvas)
            self.v_blur.add(self.h_blur.rect)

        if self.h_blur.rect.texture != self.h_blur.texture:
            self.h_blur.rect.texture = self.h_blur.texture

        self.h_blur.rect.size = self.size
        self.h_blur.rect.pos = self._pos

        self.h_blur.draw()
        self.h_blur.ask_update()
        self.v_blur.draw()
        self.v_blur.ask_update()

        self.bt_1.texture = self.v_blur.texture

        if self._update_texture_ev.timeout == 0:
            self._update_texture_ev.timeout = -1

    def _update_noise_texture(self):
        fbo_size = max(1, self.width / dp(1)), max(1, self.height / dp(1))
        self.noise.size = fbo_size
        self.noise.rect.size = self.size
        self.noise.add(self.noise.rect)
        self.noise.draw()
        self.noise.remove(self.noise.rect)
        self.bt_2.texture = self.noise.texture

    def _update_fbo_effect(self, *args):
        if self.is_movable:
            fbo_size = (min(self.width, 150), min(self.height, 150))
        else:
            fbo_size = (min(self.width, 250), min(self.height, 250))

        size = max(1, self.width), max(1, self.height)
        fbo_size = max(1, fbo_size[0]), max(1, fbo_size[1])

        self.h_blur.size = fbo_size
        self.v_blur.size = fbo_size

        pos = self.to_window(*self.pos)
        x = 1 / (size[0] / fbo_size[0])
        y = 1 / (size[1] / fbo_size[1])

        self.h_blur_scale.x = self.v_blur_scale.x = x
        self.h_blur_scale.y = self.v_blur_scale.y = -y
        self.h_blur_translate.x = self.v_blur_translate.x = -pos[0]
        self.h_blur_translate.y = self.v_blur_translate.y = -pos[1] - size[1]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_down(touch)
            return True
        return super().on_touch_down(touch)

    def on_size(self, instance, size):
        self._update_canvas()
        self._update_noise_texture()
        self.refresh_effect()

    def on_pos(self, *args):
        self._update_canvas()
        self.refresh_effect()

    def _update_canvas(self, *args):
        border_radius = list(
            map(
                lambda x: max(1, min(min(self.width, self.height) / 2, x)),
                self.border_radius,
            )
        )
        self.fbo_rect.size = self.size
        self.fbo_rect.pos = self.pos
        self.fbo_rect.radius = border_radius

        self._outline_color.rgba = self.outline_color
        self.outline.width = self.outline_width
        self.outline.rounded_rectangle = (
            self.x, self.y,
            self.width, self.height,
            *border_radius, 45,
        )

    def on_blur_size(self, instance, blur_size):
        blur_size = int(blur_size)
        if blur_size != self.last_blur_size_value:
            self.v_blur["blur_size"] = dp(blur_size)
            self.h_blur["blur_size"] = dp(blur_size)
            self.update_effect()
            self.last_blur_size_value = blur_size

    def on_background(self, _, background):
        if not background:
            return

        if self._last_background_canvas in self.h_blur.children:
            self.h_blur.remove(self._last_background_canvas)
            self.update_effect()
            self._unbind_parent_properties(self.background_parents_list)
            self._unbind_children_properties(self.background_children_list)

        self._last_background_canvas = background.canvas

        self.background_parents_list = self._get_all_parents(self.background)
        self.background_children_list = self._get_all_children(self.background)
        self._bind_parent_properties(self.background_parents_list)
        self._bind_children_properties(self.background_children_list)

    def on_parent(self, _, parent):
        if not parent:
            return

        self.parents_list = self._get_all_parents(parent)
        for p in self.parents_list:
            if isinstance(p, ModalView):
                self.popup_parent = p
            if isinstance(p, Screen):
                self.parent_screen = p
            if isinstance(p, ScrollView):
                self.is_movable = True
        self._bind_parent_properties(self.parents_list)

    def _get_all_parents(self, widget):
        widgets_list = []
        parent = widget
        while True:
            widgets_list.append(parent)
            if parent.parent and parent != parent.parent:
                parent = parent.parent
            else:
                break
        return widgets_list

    def _get_all_children(self, widget):
        widgets_list = [widget]
        children_widgets = [widget]
        while children_widgets:
            parent_widgets = children_widgets
            children_widgets = []
            for w in parent_widgets:
                if w.children:
                    widgets_list.extend(w.children)
                    children_widgets.extend(w.children)
        return widgets_list

    def _bind_children_properties(self, children_list):
        properties_to_bind = (
            "pos",
            "size",
            "scroll_x",
            "scroll_y",
            "on_open",
            "on_enter",
            "texture",
        )
        for widget in children_list:
            for property in properties_to_bind:
                try:
                    if property == "texture":
                        if isinstance(widget, Image):
                            widget.bind(
                                texture=self._trigger_update_effect
                            )
                        if isinstance(widget, Video):
                            widget.bind(
                                position=self._trigger_update_effect
                            )
                    elif hasattr(widget, property):
                        widget.fbind(
                            property,
                            self._trigger_update_effect,
                        )
                except Exception as e:
                    print(e)
                    pass

    def _bind_parent_properties(self, parents_list):
        for widget in parents_list:

            if isinstance(widget, ScrollView):
                widget.bind(
                    size=self._trigger_update_effect,
                    pos=self._trigger_update_effect,
                    scroll_x=self._trigger_update_effect,
                    scroll_y=self._trigger_update_effect,
                )
            if isinstance(widget, ModalView):
                widget.bind(
                    on_pre_open=self._trigger_update_effect
                )
            elif isinstance(widget, Screen):
                widget.bind(
                    on_pre_enter=lambda *args: self._refresh_effect_ev()
                )
                widget.bind(
                    on_enter=lambda *args: self._refresh_effect_ev.cancel()
                )

            else:
                widget.bind(size=self._trigger_update_effect)
                try:
                    widget.bind(pos=self._trigger_update_effect)
                except Exception:
                    pass

    def _unbind_children_properties(self, children_list):
        properties_to_unbind = (
            "pos",
            "size",
            "scroll_x",
            "scroll_y",
            "on_open",
            "on_enter",
            "texture",
        )
        for widget in children_list:
            for property in properties_to_unbind:
                try:
                    if property == "texture":
                        if isinstance(widget, Image):
                            widget.unbind(
                                texture=self._trigger_update_effect
                            )
                        if isinstance(widget, Video):
                            widget.unbind(
                                position=self._trigger_update_effect
                            )
                    elif hasattr(widget, property):
                        widget.funbind(
                            property,
                            self._trigger_update_effect,
                        )
                except Exception as e:
                    print(e)
                    pass

    def _unbind_parent_properties(self, parents_list):
        for widget in parents_list:

            if isinstance(widget, ScrollView):
                widget.unbind(
                    size=self._trigger_update_effect,
                    pos=self._trigger_update_effect,
                    scroll_x=self._trigger_update_effect,
                    scroll_y=self._trigger_update_effect,
                )
            if isinstance(widget, ModalView):
                widget.unbind(
                    on_pre_open=self._trigger_update_effect
                )
            elif isinstance(widget, Screen):
                widget.unbind(
                    on_pre_enter=lambda *args: self._refresh_effect_ev()
                )
                widget.unbind(
                    on_enter=lambda *args: self._refresh_effect_ev.cancel()
                )

            else:
                widget.unbind(size=self._trigger_update_effect)
                try:
                    widget.unbind(pos=self._trigger_update_effect)
                except Exception:
                    pass

    def _trigger_update_effect(self, widget, value=None):
        if (
            isinstance(value, (int, float))
            and self.update_by_timeout
            and round(value, 3) != self.last_value
        ):
            self.update_effect()
            self.last_value = round(value, 3)

        elif (
            isinstance(value, list)
            and self.update_by_timeout
            and (
                round(value[0], 2) != self.last_value_list[0]
                or round(value[1], 2) != self.last_value_list[1]
            )
        ):
            self.update_effect()
            self.last_value_list = round(value[0], 2), round(value[1], 2)

        elif self.update_by_timeout:
            self.update_effect()

    @property
    def popup_closed(self):
        return self.popup_parent and not self.popup_parent.parent

    @property
    def not_current_screen(self):
        if self.parent_screen is None or self.parent_screen.manager is None:
            return False
        return self.parent_screen.manager.current != self.parent_screen.name

    @property
    def out_of_the_window(self):
        x, y = self.to_window(self.x, self.y)
        right, top = self.to_window(self.right, self.top)
        return right < 0 or top < 0 or x > Window.width or y > Window.height

    @property
    def update_by_timeout(self):
        _now = now()
        if _now - self.last_update_time >= 0.016666:
            self.last_update_time = _now
            return True
        return False

    @property
    def background_loaded(self):
        if not self.background:
            return False
        return self.background.canvas in self.h_blur.children
