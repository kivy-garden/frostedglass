# FrostedGlass

**FrostedGlass** is a translucent frosted glass effect widget, that creates a context with the background behind it.

The effect is drawn on the FrostedGlass canvas, based on the widget passed in as the background.

![](https://github.com/kivy-garden/frostedglass/blob/main/doc/images/img1.png?raw=true)

[![Github Build Status](https://github.com/kivy-garden/frostedglass/workflows/Garden%20flower/badge.svg)](https://github.com/kivy-garden/frostedglass/actions)
[![PyPI](https://img.shields.io/pypi/v/kivy_garden.frostedglass?)](https://pypi.org/project/kivy-garden.frostedglass/)

## Install
    pip install kivy_garden.frostedglass

## Import
    from kivy_garden.frostedglass import FrostedGlass

## Example:

![](https://github.com/kivy-garden/frostedglass/blob/main/doc/images/img2.png?raw=true)

```python
Image:
    id: bg_image
    pos_hint: {'center_x': 0.5,'center_y': 0.5}
    size_hint: (None, None)
    size: (350, 350)
    source: 'live/kivy_logo.png'

FrostedGlass:
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    size_hint: (None, None)
    size: (180, 150)
    background: bg_image
    blur_size: 25
    luminosity: 1.1
    overlay_color: 0.75, 0.75, 0, 0.65
    border_radius: 0, 150, 0, 150
Label:
    text: 'FrostedGlass'
    color: 'black'
    font_size: '26sp'
    bold: True
```

### **You can find more usage examples, including uses with ScrollView in the [*examples*](https://github.com/kivy-garden/frostedglass/tree/main/examples) folder.**

---

## FrostedGlass creation process, guidelines and contribuition

To reach the final result of the FrostedGlass widget, the steps described in the image below are followed

![](https://github.com/kivy-garden/frostedglass/blob/main/doc/images/FrostedGlass_components.png?raw=true)

### Guidelines
- When using FrostedGlass with static backgrounds, it is not necessary to update the FrostedGlass effect, but if necessary at some point, just call the `update_effect()` method.
- If the background moves relative to FrostedGlass, or FrostedGlass moves relative to the background, it is necessary to call the `start_auto_update_effect` method to update the effect automatically. Don't forget to call the `stop_auto_update_effect` method, to avoid FPS drop, when the movement stops and it is **not necessary** to keep the effect updating continuously. The recommended way to do this is found in the [examples](https://github.com/kivy-garden/frostedglass/tree/main/examples) folder.
- In the current version (**v0.1.1rc1**) the less FrostedGlass you use, the smaller they are, and the less you need to continually update them, the better the performance, and you will notice very few changes in the FPS.
- If you use FrostedGlass efficiently, there will be no performance drop, and you will still enjoy a modern look in your apps.

### FrostedGlass is currently under development, and some issues can be noticed in version *0.1.1rc1*:
- FPS drop when using large or multiple FrostedGlass widgets, which need to be continuously automatically updated.
- Temporary FPS drop when you touch the screen, even using static FrostedGlass widgets (which don't need to be automatically updated). The FPS goes up right after touch up.




### 🔴 Encouraged contributions and starting point guides 🔴
- Considering the issues mentioned above, it is recommended that work be done to resolve these issues.
- Improving shader performance in performing Gaussian blur can significantly increase FrostedGlass performance. Knowledge in OpenGL can help a lot here!
- Adding manipulations to the Vertex Shader, in addition to what is done here (only Fragment Shader), can be important in improving performance.
- FBO manipulations are a hypothetical point for performance improvement.
- Perhaps saving the effect temporarily in cache, and computing just its position can be an important factor. Other caching implementations may also be useful.

---
## API

    background

> Target widget/layout that will be used as a background to FrostedGlass.
> The recomended way to pass the widget is through the widget/layout **id**.
> 
> `background` is defaults to None.

<br/>

    blur_size

> Size of the gaussian blur aplied to the background.
>
> `blur_size` is defaults to 60.

<br/>

    luminosity

> Luminosity boost that will be aplied to the background.
> 
> `luminosity` is defaults to 1.25.

<br/>

    overlay_color

> Color/tint overlay.
> 
> `overlay_color` is defaults to [1, 1, 1, 0.6].

<br/>

    noise_opacity

> Opacity of the noise texture layer.
> 
> `noise_opacity` is a defaults to 0.1.

<br/>

    downscale_factor

> Determine how many times the FBO size will be reduced.
> This property affects the performane directly. As bigger the FBO is, more slow will be the process to compute the gaussian blur resulting in significative fps drop.
> 
> `downscale_factor` is defaults to 8.

<br/>

    border_radius

> Border radius that will be used by the default canvas shape (RoundedRectangle).
> 
> `border_radius` is defaults to [0, 0, 0, 0].

<br/>

    update_effect()

> Updates the effect only once with each method call. If you only need to change the effect once in a while, it is recommended that you call this method.
> If you need constant updates, it is recommended to use `start_auto_update_effect` and `start_auto_update_effect` to manage this.

<br/>

    start_auto_update_effect()

> Start automatic update of effect. The automatic update will remain active until you call the `stop_auto_update_effect()` method.
> Can be called multiple times without problems, but will only run once.

<br/>

    stop_auto_update_effect()

> Stop automatic update of effect.
> It is recommended that you call this method whenever you do not need the effect to keep updating automatically. As this prevents FPS drop.

<br/>

CI
--

Every push or pull request run the [GitHub Action](https://github.com/kivy-garden/flower/actions) CI.
It tests the code on various OS and also generates wheels that can be released on PyPI upon a
tag. Docs are also generated and uploaded to the repo as well as artifacts of the CI.

Contributing
--------------

Check out our [contribution guide](CONTRIBUTING.md) and feel free to improve the FrostedGlass flower.

🔴 If you have a bug or an idea, create a report to help us improve or suggest an idea for this project by opening an issue

🔴 Every contribution is welcome and appreciated!!!

License
---------

This software is released under the terms of the MIT License.
Please see the [LICENSE.txt](LICENSE.txt) file.

