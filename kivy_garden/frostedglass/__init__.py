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

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import (ListProperty, ObjectProperty, ColorProperty,
                             NumericProperty)
from kivy.graphics import (RenderContext, Fbo, Color, RoundedRectangle, Scale,
                           Translate, PushMatrix, PopMatrix, ClearColor,
                           ClearBuffers, BindTexture)

shader_effect = '''
$HEADER$


uniform float opacity;
uniform float blur_size;
uniform float luminosity;
uniform float noiseOpacity;
uniform vec2 position;
uniform vec2 resolution;
uniform vec4 color_overlay;
uniform sampler2D bg;


void main(void)
{
    vec2 pos = (gl_FragCoord.xy - position.xy) / resolution.xy;

    float noise = 0.0;
    vec2 blurRadius = blur_size/resolution.xy;
    vec3 noiseTexture = vec3(0.0);
    vec4 textureResult = vec4(0.0);
    vec4 textureSum = texture2D(bg, pos);

    textureSum += texture2D(bg, (pos + vec2(cos(0.00),sin(0.00)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(0.00),sin(0.00)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(0.00),sin(0.00)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(0.00),sin(0.00)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(0.63),sin(0.63)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(0.63),sin(0.63)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(0.63),sin(0.63)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(0.63),sin(0.63)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(1.26),sin(1.26)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(1.26),sin(1.26)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(1.26),sin(1.26)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(1.26),sin(1.26)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(1.88),sin(1.88)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(1.88),sin(1.88)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(1.88),sin(1.88)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(1.88),sin(1.88)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(2.51),sin(2.51)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(2.51),sin(2.51)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(2.51),sin(2.51)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(2.51),sin(2.51)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(3.14),sin(3.14)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(3.14),sin(3.14)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(3.14),sin(3.14)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(3.14),sin(3.14)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(3.77),sin(3.77)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(3.77),sin(3.77)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(3.77),sin(3.77)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(3.77),sin(3.77)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(4.40),sin(4.40)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(4.40),sin(4.40)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(4.40),sin(4.40)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(4.40),sin(4.40)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(5.03),sin(5.03)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(5.03),sin(5.03)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(5.03),sin(5.03)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(5.03),sin(5.03)) * blurRadius
                            * 1.0));
    textureSum += texture2D(bg, (pos + vec2(cos(5.65),sin(5.65)) * blurRadius
                            * 0.25));
    textureSum += texture2D(bg, (pos + vec2(cos(5.65),sin(5.65)) * blurRadius
                            * 0.5));
    textureSum += texture2D(bg, (pos + vec2(cos(5.65),sin(5.65)) * blurRadius
                            * 0.75));
    textureSum += texture2D(bg, (pos + vec2(cos(5.65),sin(5.65)) * blurRadius
                            * 1.0));

    textureSum /= 4.0 * 10.0 - 15.0;
    textureSum *= luminosity;

    noise = fract(sin(dot((vec2(sin(pos) / 1.0)).xy, vec2(12.9898, 78.233)))
                  * 43758.5453);
    noiseTexture = vec3(noise);

    textureSum = mix(textureSum.rgba, vec4(color_overlay.rgb, 1.0),
                     color_overlay.a);
    textureSum = mix(textureSum.rgba, vec4(noiseTexture.rgb, 1.0),
                     noiseOpacity);

    gl_FragColor = vec4(textureSum.rgb, opacity);

}
'''


class FrostedGlass(FloatLayout):

    background = ObjectProperty(None)
    '''Target widget/layout that will be used as a background to FrostedGlass.
    The recomended way to pass the widget is through the id.

    :attr:`background` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None.'''

    blur_size = NumericProperty(60)
    '''Size of the gaussian blur aplied to the background.

    :attr:`blur_size` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 60.'''

    noise_opacity = NumericProperty(0.1)
    '''Opacity of the noise layer.

    :attr:`noise_opacity` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0.1.'''

    luminosity = NumericProperty(1.25)
    '''Luminosity boost that will be aplied to the background.

    :attr:`luminosity` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 1.25.'''

    overlay_color = ColorProperty([1, 1, 1, 0.75])
    '''Color/tint overlay that will be aplied to the background.

    :attr:`overlay_color` is a :class:`~kivy.properties.ColorProperty` and
    defaults to [1, 1, 1, 0.6].'''

    border_radius = ListProperty([0, 0, 0, 0])
    '''Border radius that will be used by the default canvas shape
    (RoundedRectangle).

    :attr:`border_radius` is a :class:`~kivy.properties.ListProperty` and
    defaults to [0, 0, 0, 0].'''

    downscale_factor = NumericProperty(8)
    '''Determine how many times the fbo size will be reduced.

    This property affects the performane directly. As bigger the FBO is,
    more slow will be the process to compute the gaussian blur resulting in
    significative fps drop.

    :attr:`downscale_factor` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 8.'''

    def __init__(self, **kwargs):
        super(FrostedGlass, self).__init__(**kwargs)

        self.canvas = RenderContext(use_parent_projection=True,
                                    use_parent_modelview=True,
                                    use_parent_frag_modelview=True)
        with self.canvas:
            self.fbo_color = Color(1, 1, 1, 1)
            self.bt = BindTexture(texture=self.background, index=2)
            self.fbo_rect = RoundedRectangle(size=self.size,
                                             pos=self.pos,
                                             radius=self.border_radius)

        self.canvas.shader.fs = shader_effect

        self.auto_update = Clock.schedule_interval(self.update_shader, 1/30)
        self.auto_update.cancel()

        self.stop_auto_update_effect = Clock.schedule_once(
            lambda dt: self.auto_update.cancel(), 2
        )
        self.stop_auto_update_effect.cancel()

        self.bind(on_kv_post=self.update_effect)

    def update_effect(self, *args):
        Clock.schedule_once(self.update_shader, 1/60)

    def start_auto_update_effect(self):
        if self.stop_auto_update_effect.is_triggered:
            self.stop_auto_update_effect.cancel()
        if not self.auto_update.is_triggered:
            self.auto_update()

    def update_shader(self, *largs):
        self.fbo_rect.radius = self.border_radius

        self.canvas['opacity'] = float(self.opacity)
        self.canvas['blur_size'] = float(dp(self.blur_size))
        self.canvas['luminosity'] = float(self.luminosity)
        self.canvas['noiseOpacity'] = float(self.noise_opacity)
        self.canvas['color_overlay'] = [float(x) for x in self.overlay_color]

        pos = self.to_window(*self.pos)
        self.canvas['resolution'] = [float(v) for v in self.size]
        self.canvas['position'] = [float(v) for v in pos]

        self.fbo = Fbo(size=(self.width/self.downscale_factor,
                             self.height/self.downscale_factor))

        with self.fbo.before:
            PushMatrix()
        with self.fbo:
            ClearColor(0.7, 0.7, 0.7, 1)
            ClearBuffers()
            Scale(1/self.downscale_factor)
            Translate(-pos[0], -pos[1])
        with self.fbo.after:
            PopMatrix()

        self.fbo.add(self.background.canvas)
        self.fbo.draw()
        self.bt.texture = self.fbo.texture
        self.canvas['bg'] = 2
        self.fbo.remove(self.background.canvas)

    def on_size(self, instance, value):
        self.fbo_rect.size = value
        self.update_effect()

    def on_pos(self, instance, value):
        self.fbo_rect.pos = value
        self.update_effect()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return True
