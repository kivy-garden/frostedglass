# FrostedGlass

**FrostedGlass** is a widget with translucent frosted glass effect, that creates a context with the background behind it.

The effect created is based on the widget passed in as the background. You can control the blur size, saturation, luminosity, overlay color, noise opacity, border radius and the outline (color and width).

![](https://github.com/DexerBR/frostedglass/blob/pre-release/doc/images/example_1.png?raw=true)
![](https://github.com/DexerBR/frostedglass/blob/pre-release/doc/images/example_2.gif?raw=true)

[![Github Build Status](https://github.com/kivy-garden/frostedglass/workflows/Garden%20flower/badge.svg)](https://github.com/kivy-garden/frostedglass/actions)
[![PyPI](https://img.shields.io/pypi/v/kivy_garden.frostedglass?)](https://pypi.org/project/kivy-garden.frostedglass/)

## Install
    pip install kivy_garden.frostedglass

## Import
    from kivy_garden.frostedglass import FrostedGlass

## Usage

*FrostedGlass* will apply the effect to the background passed to it. Make sure you assign the correct id of the widget/layout that is behind *FrostedGlass* to the `background` property.

## Example:

<img src="https://github.com/DexerBR/frostedglass/blob/pre-release/doc/images/kivy_example.png?raw=true">

```kvlang
Image:
    id: bg_image
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    source: 'kivy_logo.png'

FrostedGlass:
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    size_hint: (None, None)
    size: (180, 130)
    background: bg_image
    blur_size: 20
    saturation: 1.0
    luminosity: 1.5
    overlay_color: "#FFB9008C"
    noise_opacity: 0.15
    border_radius:  dp(0), dp(100), dp(0), dp(100)
    outline_color: "#000000"
    outline_width: 1.2
    Label:
        text: 'FrostedGlass'
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        bold: True
        color: 'black'
        font_size: dp(25)
```
### You can find more usage examples in the 🔷[examples folder](https://github.com/DexerBR/frostedglass/tree/pre-release/examples)🔷

---

## Overview of *FrostedGlass* creation process

To reach the final result of the FrostedGlass widget, the steps described in the image below are followed:

![](https://github.com/DexerBR/frostedglass/blob/pre-release/doc/images/FrostedgGlass_overview.png?raw=true)

---

## Guidelines
The FrostedGlass widget will attempt to update the effect whenever there is a change to its properties or background properties that require an effect update to keep the effect in sync. But if it doesn't, you can call the `update_effect()` method manually to update the effect.

If calling the `update_effect()` method did not update the effect, you may need to call the `refresh_effect()` method. But beware, calling this effect continuously in a small interval of time can reduce the widget's performance.

---

## **API**

    background

> Target widget/layout that will be used as a background to FrostedGlass.
> The recomended way to pass the widget is through the widget/layout **id**.
> 
> `background` is defaults to `None`.

<br/>

    blur_size

> Size of the gaussian blur aplied to the background.

❗️*Note: Do not pass relative values such as **dp** or **sp**. FrostedGlass already
    manages this automatically, according to the device's screen density.*

> `blur_size` is defaults to `25`.

<br/>

    saturation

> Saturation boost that will be aplied to the background.
> 
> `saturation` is defaults to `1.2`.

<br/>

    luminosity

> Luminosity boost that will be aplied to the background.
> 
> `luminosity` is defaults to `1.3`.


<br/>

    overlay_color

> Color/tint overlay that will be aplied over the background.
> 
> `overlay_color` is defaults to `[0.5, 0.5, 0.5, 0.35]`.

<br/>

    noise_opacity

> Opacity of the noise texture layer.
> 
> `noise_opacity` is a defaults to `0.08`.

<br/>

    border_radius

> Specifies the radius used for the rounded corners clockwise:
> top-left, top-right, bottom-right, bottom-left.
> 
> `border_radius` is defaults to `[0, 0, 0, 0]`.

<br/>

    outline_color

> Outline color.
> 
> `outline_color` is defaults to `[1, 1, 1, 1]`.

<br/>

    outline_width

> Outline width.
> 
> `outline_width` is defaults to `1`.

<br/>



    update_effect()

> Updates the effect only once with each method call.

❗️*Note: Use this method to update the effect only if it doesn't update automatically.*

<br/>

    refresh_effect()

> Updates the effect only once with each method call. Sould be used as an alternative, when `update_effect()` doesn't update the effect totally.

❗️*Note: Use this method to update the effect only if it doesn't update automatically and `update_effect()` doesn't update the effect.*

❗️*Note: Unlike `update_effect()` method, `refresh_effect()` will refresh the FBO on each call, wich can lead to a performance drop if called continuously on a small interval of time.*

---

<br>

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

