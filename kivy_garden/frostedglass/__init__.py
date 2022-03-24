"""
FrostedGlass
============

The :class:`FrostedGlass` is a translucent frosted glass effect widget, that
creates a context with the background behind it.

The effect is drawn on the FrostedGlass canvas, based on the widget passed in
as the background.
"""

__all__ = ('FrostedGlass', )

from ._version import __version__

from functools import partial
from time import perf_counter as now

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import (
    BindTexture,
    Color,
    ClearColor,
    ClearBuffers,
    Fbo,
    Rectangle,
    RenderContext,
    RoundedRectangle,
    Scale,
    SmoothLine,
    Translate
)
from kivy.properties import (
    ColorProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty
)
from kivy.uix.floatlayout import FloatLayout

# Used for type checking
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image


MEAN_RES = (Window.width + Window.height)/2


vertex_shader = ("""
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* vertex attributes */
attribute vec2     vPosition;
attribute vec2     vTexCoords0;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;


void main (void) {
  frag_color = color;
  tex_coord0 = vTexCoords0;
  gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}
""")


vertical_blur_shader = """
#ifdef GL_ES
    precision lowp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;


vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{{
  float mean_res = float({});
  float dt = (({} / 2.0) * 1.0 / mean_res);
  vec4 sum = vec4(0.0);

  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 3.0*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 2.5*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 2.0*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 1.5*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 1.0*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y - 0.5*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 0.5*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 1.0*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 1.5*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 2.0*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 2.5*dt)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y + 3.0*dt)) * 0.077;

  return frag_color * vec4(sum.rgba);
}}
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


vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{{
  float mean_res = float({});
  float dt = ({} / 2.0) * 1.0 / mean_res;
  vec4 sum = vec4(0.0);


  sum += texture2D(texture, vec2(tex_coords.x - 3.0*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x - 2.5*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x - 2.0*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x - 1.5*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x - 1.0*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x - 0.5*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x + 0.5*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x + 1.0*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x + 1.5*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x + 2.0*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x + 2.5*dt, tex_coords.y)) * 0.077;
  sum += texture2D(texture, vec2(tex_coords.x + 3.0*dt, tex_coords.y)) * 0.077;

  return  frag_color * vec4(sum.rgba);
}}
"""


shader_footer_effect = """
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


float noise(vec2 co)
{
    float a = 12.9898;
    float b = 78.233;
    float c = 43758.5453;
    float dt= dot(co.xy, vec2(a, b));
    float sn= mod(dt, 3.14);
    return fract(sin(sn) * c);
}

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


class VerticalBlur(FloatLayout):

    glsl = StringProperty('')
    fbo = ObjectProperty(None, allownone=True)
    blur_size = NumericProperty(0.0)

    def __init__(self, *args, **kwargs):
        super(VerticalBlur, self).__init__(*args, **kwargs)
        self.bind(
            fbo=self.set_fbo_shader,
            blur_size=self.update_glsl,
        )
        self.glsl = horizontal_blur_shader.format(
            MEAN_RES, float(self.blur_size)
        )

        with self.canvas:
            self.rect = Rectangle()

    def set_fbo_shader(self, *args):
        if self.fbo is None:
            return
        self.fbo.shader.fs = self.glsl + shader_footer_effect

    def update_glsl(self, *args):
        self.glsl = horizontal_blur_shader.format(
            MEAN_RES, float(self.blur_size)
        )


class HorizontalBlur(FloatLayout):

    glsl = StringProperty('')
    fbo = ObjectProperty(None, allownone=True)
    blur_size = NumericProperty(0.0)

    def __init__(self, *args, **kwargs):
        super(HorizontalBlur, self).__init__(*args, **kwargs)
        self.bind(
            fbo=self.set_fbo_shader,
            blur_size=self.update_glsl,
        )
        self.glsl = vertical_blur_shader.format(
            MEAN_RES, float(self.blur_size)
        )

    def set_fbo_shader(self, *args):
        if self.fbo is None:
            return
        self.fbo.shader.fs = self.glsl + shader_footer_effect

    def update_glsl(self, *args):
        self.glsl = vertical_blur_shader.format(
            MEAN_RES, float(self.blur_size)
        )


class Noise(FloatLayout):

    glsl = StringProperty('')
    fbo = ObjectProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super(Noise, self).__init__(*args, **kwargs)
        self.bind(fbo=self.set_fbo_shader)
        with self.canvas:
            self.rect = Rectangle()
        self.glsl = noise_shader

    def set_fbo_shader(self, *args):
        if self.fbo is None:
            return
        self.fbo.shader.fs = self.glsl + shader_footer_effect


class FrostedGlass(FloatLayout):

    background = ObjectProperty(None)
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
        self.bind(
            blur_size=self.update_effect,
            noise_opacity=self.update_effect,
            luminosity=self.update_effect,
            saturation=self.update_effect,
            overlay_color=self.update_effect,
            border_radius=self.update_effect
        )

        self.frosted_glass_effect = FloatLayout()
        self.frosted_glass_effect.canvas = RenderContext(
            use_parent_projection=True,
            use_parent_modelview=True,
            use_parent_frag_modelview=True
        )
        with self.frosted_glass_effect.canvas:
            self.bt_1 = BindTexture(index=1)
            self.bt_2 = BindTexture(index=2)
            self.fbo_rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=self.border_radius,
            )
        self.frosted_glass_effect.canvas.shader.fs = final_shader_effect
        self.frosted_glass_effect.canvas.shader.vs = vertex_shader

        self.canvas.add(self.frosted_glass_effect.canvas)

        with self.canvas:
            self._outline_color = Color(rgba=self.outline_color)
            self.outline = SmoothLine(
                width=1,
                overdraw_width=dp(1.5),
                rounded_rectangle=(
                    self.x, self.y, self.width, self.height, 1, 1, 1, 1
                )
            )

        self.horizontal_blur = HorizontalBlur(blur_size=self.blur_size)
        self.vertical_blur = VerticalBlur(blur_size=self.blur_size)
        self.noise = Noise()

        self.last_value = 0
        self.last_update_time = 0
        self.last_blur_size_value = 0
        self.last_value_list = [0, 0]
        self.last_fbo_pos = [None, None]

        self.update_fbo_effect()

    def update_effect(self, *args, type=None):
        Clock.schedule_once(lambda _: self.update_glsl(type), 0)

    def refresh_effect(self, *args):
        self.update_fbo_effect()
        self.update_effect(type=type)

    def update_glsl(self, *args):
        pos = self.to_window(*self.pos)
        fge_canvas = self.frosted_glass_effect.canvas

        fge_canvas["position"] = [float(v) for v in pos]
        fge_canvas["resolution"] = [float(v) for v in self.size]
        fge_canvas["luminosity"] = float(self.luminosity)
        fge_canvas["saturation"] = float(self.saturation)
        fge_canvas["noise_opacity"] = float(self.noise_opacity)
        fge_canvas["color_overlay"] = [float(v) for v in self.overlay_color]

        performance_fbo_size = (min(self.width, 150), min(self.height, 150))
        if "in_motion" in args:
            if (
                self.fbo_1.size != performance_fbo_size
                or self.fbo_2.size != performance_fbo_size
            ):
                if None in self.last_fbo_pos:
                    Clock.schedule_once(lambda *args: self.update_fbo_effect(
                        True, self.to_window(*self.pos, initial=False)), 0
                    )
                else:
                    Clock.schedule_once(lambda *args: self.update_fbo_effect(
                        True, pos), 0
                    )

            if None in self.last_fbo_pos:
                self.last_fbo_pos = pos

            _pos = [
                -(pos[0] - self.last_fbo_pos[0]),
                -(pos[1] - self.last_fbo_pos[1])
            ]
            self.fbo_1_translate.x += _pos[0]
            self.fbo_2_translate.x += _pos[0]
            self.fbo_1_translate.y += _pos[1]
            self.fbo_2_translate.y += _pos[1]

        elif (
            self.fbo_1.size == performance_fbo_size
            or self.fbo_2.size == performance_fbo_size
        ):
            self.last_fbo_pos = [None, None]
            Clock.schedule_once(lambda *args: self.update_fbo_effect(), 0)
        self.last_fbo_pos = pos

        self.bt_1.texture = self._get_final_texture(pos)
        fge_canvas["texture1"] = 1
        fge_canvas.ask_update()

    def _get_final_texture(self, pos):
        self.fbo_1.add(self.background.canvas)
        self.fbo_1.draw()
        self.vertical_blur.rect.size = self.size
        self.vertical_blur.rect.pos = pos
        self.fbo_1.remove(self.background.canvas)
        self.vertical_blur.rect.texture = self.fbo_1.texture

        self.fbo_2.add(self.vertical_blur.canvas)
        self.fbo_2.draw()
        texture = self.fbo_2.texture
        self.fbo_2.remove(self.vertical_blur.canvas)

        return texture

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_down(touch)
            return True
        return super().on_touch_down(touch)

    def on_size(self, instance, size):
        self.update_canvas()
        self.update_fbo_effect()
        self.update_effect()
        self.update_noise_texture()

    def update_noise_texture(self):
        fbo_size = max(1, self.width/dp(1)), max(1, self.height/dp(1))
        self.fbo_noise = Fbo(size=fbo_size)
        self.noise.fbo = self.fbo_noise
        self.noise.rect.size = self.size
        self.noise.fbo.add(self.noise.canvas)
        self.noise.fbo.draw()
        self.noise.fbo.remove(self.noise.canvas)
        self.bt_2.texture = self.fbo_noise.texture
        self.frosted_glass_effect.canvas["texture2"] = 2

    def on_pos(self, *args):
        self.update_canvas()
        self.update_fbo_effect()
        self.update_effect()

    def on_border_radius(self, *args):
        self.update_canvas()

    def update_canvas(self):
        border_radius = list(
            map(
                lambda x: max(1, min(min(self.width/2, self.height/2), x)),
                self.border_radius
            )
        )
        self.fbo_rect.size = self.size
        self.fbo_rect.pos = self.pos
        self.fbo_rect.radius = border_radius

        self._outline_color.rgba = self.outline_color
        self.outline.width = self.outline_width
        self.outline.rounded_rectangle = (
            self.x, self.y, self.width, self.height,
            border_radius[3],
            border_radius[2],
            border_radius[1],
            border_radius[0],
        )

    def on_blur_size(self, instance, blur_size):
        blur_size = int(blur_size)
        if blur_size != self.last_blur_size_value:
            self.vertical_blur.blur_size = dp(blur_size)
            self.horizontal_blur.blur_size = dp(blur_size)
            self.update_fbo_effect()
            self.update_effect()
            self.last_blur_size_value = int(blur_size)

    def update_fbo_effect(self, improve_performance=False, pos=None):
        if improve_performance:
            fbo_size = (min(self.width, 150), min(self.height, 150))
        else:
            fbo_size = (min(self.width, 250), min(self.height, 250))

        size = max(1, self.width), max(1, self.height)
        fbo_size = max(1, fbo_size[0]), max(1, fbo_size[1])

        self.fbo_1 = Fbo(size=fbo_size)
        self.fbo_2 = Fbo(size=fbo_size)

        pos = pos or self.to_window(*self.pos)
        x = 1/(size[0]/fbo_size[0])
        y = 1/(size[1]/fbo_size[1])
        z = 1

        with self.fbo_1:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            Scale(x, y, z)
            self.fbo_1_translate = Translate(-pos[0], -pos[1])

        with self.fbo_2:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()
            Scale(x, y, z)
            self.fbo_2_translate = Translate(-pos[0], -pos[1])

        self.vertical_blur.fbo = self.fbo_1
        self.horizontal_blur.fbo = self.fbo_2

    def on_background(self, *args):
        self.bind_parent_properties(self.background)
        self.bind_children_properties(self.background)

    def on_parent(self, *args):
        self.bind_parent_properties(self.parent, check_in_motion=True)

    def bind_children_properties(self, widget):
        children_list = widget.children
        children_list_temp = []
        while children_list:
            for w in children_list:
                if isinstance(w, ScrollView):
                    w.bind(
                        size=self.trigger_update_effect,
                        pos=self.trigger_update_effect,
                        scroll_x=self.trigger_update_effect,
                        scroll_y=self.trigger_update_effect
                    )
                elif isinstance(w, Screen):
                    w.bind(
                        on_enter=lambda dt: Clock.schedule_once(
                            self.refresh_effect, 0
                        )
                    )
                elif isinstance(w, Image):
                    w.bind(
                        source=lambda instance, _: instance._coreimage.bind(
                            on_texture=lambda instance:
                            self.trigger_update_effect(instance, None)
                        )
                    )

                else:
                    w.bind(
                        size=self.trigger_update_effect,
                        pos=self.trigger_update_effect
                    )

                if w.children:
                    for wi in w.children:
                        children_list_temp.append(wi)
            children_list = children_list_temp
            children_list_temp = []

    def bind_parent_properties(self, widget, check_in_motion=False):
        while True:
            if isinstance(widget, ScrollView):
                widget.bind(
                    size=partial(
                        self.trigger_update_effect,
                        type="in_motion" if check_in_motion else None
                    ),
                    pos=partial(
                        self.trigger_update_effect,
                        type="in_motion" if check_in_motion else None
                    ),
                    scroll_x=partial(
                        self.trigger_update_effect,
                        type="in_motion" if check_in_motion else None
                    ),
                    scroll_y=partial(
                        self.trigger_update_effect,
                        type="in_motion" if check_in_motion else None
                    )
                )
            elif isinstance(widget, Screen):
                widget.bind(on_enter=self.refresh_effect)
            else:
                widget.bind(size=self.update_effect)
                try:
                    widget.bind(pos=self.update_effect)
                except Exception:
                    pass

            if widget.parent and widget != widget.parent:
                widget = widget.parent
            else:
                break

    def trigger_update_effect(self, widget=None, value=None, type=None):
        allow_update_by_timeout = (now() - self.last_update_time) >= 0.016
        if value is None:
            self.update_effect(type=type)

        if (
            (isinstance(value, int) or isinstance(value, float))
            and allow_update_by_timeout and round(value, 3) != self.last_value
        ):
            self.update_effect(type=type)
            self.last_value = round(value, 3)
            self.last_update_time = now()

        elif (
            isinstance(value, list) and allow_update_by_timeout
            and (
                round(value[0], 2) != self.last_value_list[0]
                or round(value[1], 2) != self.last_value_list[1]
            )
        ):
            self.update_effect(type=type)
            self.last_value_list = round(value[0], 2), round(value[1], 2)
            self.last_update_time = now()
