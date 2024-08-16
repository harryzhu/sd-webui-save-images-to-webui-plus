# SD-WebUI-Save-Images-To-WebUI-Plus : 
a Stable Diffusion extension for saving the generated images into cloud automatically.

## Getting Started
1. Clone this repo into the `extensions` directory via git commandline launched within in the `stable-diffusion-webui` folder
```sh
git clone https://github.com/harryzhu/sd-webui-save-images-to-webui-plus extensions/sd-webui-save-images-to-webui-plus
```
   Or download this repository, locate the `extensions` folder within your WebUI installation, create a folder named `save-images-to-webui-plus` and put the contents of the downloaded directory inside of it. 

2. register an username and get an apikey via http://webui.plus,

3. In your webui machine, setup two env vars: WEBUI_PLUS_USER and WEBUI_PLUS_KEY, WEBUI_PLUS_USER value is your username and WEBUI_PLUS_KEY is your apikey(not the password),

2. Then restart your WebUI,

3. Open webui in browser, find the [Save images to https://webui.plus] checkbox at the bottom of Seed,

4. generate your images,

5. visit http://list.webui.plus, you can see your images, default username is `__testman__` and __testman__'s images will be removed after 15 minutes, this username is just for testing, you should register your unique username.