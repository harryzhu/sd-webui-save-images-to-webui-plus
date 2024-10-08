import base64
import datetime
import time
from io import BytesIO
import os
import re
import modules.scripts as scripts
import gradio as gr
import json
import hashlib
import requests


URL_UPLOAD = "https://u2.webui.plus/upload"

WEBUI_PLUS_USER = os.environ.get('WEBUI_PLUS_USER', '')
WEBUI_PLUS_KEY = os.environ.get('WEBUI_PLUS_KEY', '')

def get_webui_plus_status():
    status_text = "[ERROR:OFFLINE]"
    try:
        res = requests.head(URL_UPLOAD, timeout=3.0)
        if res.status_code > 0 and res.status_code < 400:
            status_text = ""
    except requests.exceptions as e:
        status_text = "[ERROR:OFFLINE]"
    finally:
        return status_text

    

class Scripts(scripts.Script):
    def title(self):
        return "https://webui.plus"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        if WEBUI_PLUS_USER == "" or WEBUI_PLUS_KEY == "":
            checkbox_save_to_db = gr.inputs.Checkbox(label=get_webui_plus_status() + " Save images to https://webui.plus, [please set env vars (WEBUI_PLUS_USER, WEBUI_PLUS_KEY) first.]", default=True)
        else:
            checkbox_save_to_db = gr.inputs.Checkbox(label=get_webui_plus_status() + " Save images to https://webui.plus, Author: " + WEBUI_PLUS_USER.lower(), default=True)
        
        checkbox_is_private = gr.inputs.Checkbox(label="Do NOT share my images", default=False)

        return [checkbox_save_to_db, checkbox_is_private]

    def postprocess(self, p, processed,checkbox_save_to_db,checkbox_is_private):
        if not checkbox_save_to_db:
            return True
        
        is_private = 0
        if checkbox_is_private:
            is_private = 1

        global WEBUI_PLUS_USER
        global WEBUI_PLUS_KEY
             
        for i in range(len(processed.images)):

            try:
                # Extract image information
                regex = r"Steps:.*$"
                seed = processed.seed
                prompt = processed.prompt
                neg_prompt = processed.negative_prompt
                info = re.findall(regex, processed.info, re.M)[0]
                input_dict = dict(item.split(": ") for item in str(info).split(", "))
                steps = int(input_dict["Steps"])
                seed = int(input_dict["Seed"])
                sampler = input_dict["Sampler"]
                cfg_scale = float(input_dict["CFG scale"])
                size = tuple(map(int, input_dict["Size"].split("x")))
                model_hash = input_dict["Model hash"]
                model = input_dict["Model"]
                #print(input_dict)

                image = processed.images[i]
                buffer = BytesIO()
                image.save(buffer, "png")
                image_bytes = buffer.getvalue()
                image_size = image.size
                if image_size[0] > size[0] or image_size[1] > size[1]:
                    continue

                meta = {
                        "model_hash": model_hash,
                        "sampler": sampler,
                        "prompt": prompt,
                        "negative_prompt": neg_prompt, 
                        "steps": int(steps), 
                        "cfg_scale": float(cfg_scale),
                        "width": int(size[0]),
                        "height": int(size[1])
                }

                meta_str = json.dumps(meta).lower()
                meta_md5 = hashlib.md5(meta_str.encode('utf-8')).hexdigest()

                #
                meta["model"] = model
                meta["seed"] = int(seed)
                
                # 
                meta["username"] = WEBUI_PLUS_USER
                meta["userkey"] = WEBUI_PLUS_KEY
                meta["md5_meta"] = meta_md5
                #
                meta["is_private"] = is_private
                #
                meta["image_bin"] = image_bytes
                meta["filesize"] = len(image_bytes)
                meta["md5_file"] = hashlib.md5(image_bytes).hexdigest()
                
                meta["content_type"] = "image/png"
                meta["ts_upload"] = int(time.time())
            except:
                print("error while preparing the meta")
                continue

            if checkbox_save_to_db and meta["filesize"] > 0:
                print("\nuploading filesize: %d" % (meta["filesize"],))
                res = requests.post(url=URL_UPLOAD,data=meta)
                print(res.status_code,": ",res.content.decode('utf-8'))

        return True
