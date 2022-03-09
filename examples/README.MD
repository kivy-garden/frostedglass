# Guide:

When you run the `main.py` file you will see three common types of FrostedGlass implementations: static, static with a moving background, and moving with a static background.
In terms of performance, there is no significant difference between the first and second implementations (which have high performance). However, the third implementation may have a slight drop in FPS on some devices, as it needs to update the FBO every time the *FrostedGlass* is moved. *What can be targeted for improvement by contributors!*

The main intention is to give a basic idea of how to combine FrostedGlass with the rest of the UI. These are just some of the many possible combinations you can make. *The creativity is yours!*

An FPS meter (`fps_monitor.py`) will also be imported and used to display the current performance of the UI. But attention, its use is indicated only for development purposes and contribution to the FrostedGlass project widget. For final product uses, perform conventional import and use as described on the project homepage: [*Import and Usage*](https://github.com/kivy-garden/frostedglass/blob/main/README.md#import)

### For contributors:

The contents of this folder are ready to be used on any operating system supported by Kivy. The FPS indicator will be imported and used automatically as mentioned above and will help you to track the performance of the UI while improving the performance, quality and usability of the FrostedGlass widget. The contents of this folder will help you improve FrostedGlass, but you don't have to limit yourself to it, of course!


# Examples overview:

https://user-images.githubusercontent.com/73297572/157085704-6fa4c48b-ba9a-4fb3-9ef1-a59088a89622.mp4
