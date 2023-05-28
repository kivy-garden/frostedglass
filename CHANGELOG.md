# Changelog
<br>

# 0.5.0 → 2023-05-28

Fixed
----------

- Fix effect update for animated backgrounds (gif, videos, etc);
- Require `kivy==2.2.0` (which includes kivy `Smoothline` `rounded_rectangle` fix);
- Ask update for horizontal blur fbo.

# 0.4.0 → 2023-04-30

Fixed
----------

- Fix related to state of UI not updating when needed.
- Fix that allows changing the background dynamically (with binding and unbinding properties).
- Fixed issue that caused the app to crash if an instance of FrostedGlass was removed.
- Improved binding/unbinding of properties.

# 0.3.0 → 2023-01-23

Highlights
----------

- Performance improvement with new rules for widget update. Only widgets inside the window, or on the current screen (when using `ScreenManager`) will be updated, avoiding unnecessary computation of widgets that are not being viewed.
- Improved integration with `ModalView`.
- Significant performance improvement when using multiple moving `FrostedGlass` widgets (like inside a `ScrollView`).
- Added support for auto-update when using videos as background.
- Improved performance when animating the `blur_size` property.
- Minor bug fixes.

Docs
----------
- Added usage example with `ModalView`.
- Updated overview video with new example using `ModalView`.

Internal
----------

- Removed final effect widget from child widget tree. Now the effect is drawn directly on the canvas.
- General refactoring.

<br>

# 0.2.0 → 2022-03-08

Highlights
----------

- Significant improvements in overall performance.
- Improved blur quality.
- Automatic effect update to keep it in sync with the background.
- Improved noise texture quality and consistency of its appearance on different devices.

Added
----------

- Added `saturation` property.
- Added `outline_color` property.
- Added `outline_width` property.
- Added `refresh_effect()` method.
- Added feature to add widgets to the container FrostedGlass #1.

Changed
----------

- Default `luminosity` value changed from `1.25` to `1.3`.
- Default `overlay_color` value changed from `[1, 1, 1, 0.75]` to `[0.5, 0.5, 0.5, 0.5]`.
- Default `luminosity` value changed from `1.25` to `1.3`.
- Default `blur_size` value changed from `60` to `25`.
- `update_effect()` does not need to be called manually to update the effect. This is already managed by the widget.

Removed
----------

- Removed `downscale_factor` property.
- Removed `start_auto_update_effect()` method.
- Removed `stop_auto_update_effect()` method.

Fixed
----------

- Temporary FPS drop when there was a touch on the screen (even using static FrostedGlass widgets).

<br>

# 0.1.1rc1 → 2021-10-02
 - Initial pre-release.
