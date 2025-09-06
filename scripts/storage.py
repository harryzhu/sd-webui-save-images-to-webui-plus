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



URL_UPLOAD = "https://upload.webui.plus/stablediffusion"

WEBUI_PLUS_USER = os.environ.get('WEBUI_PLUS_USER', '')
WEBUI_PLUS_KEY = os.environ.get('WEBUI_PLUS_KEY', '')

def get_webui_plus_status():
    status_text = "[ERROR:OFFLINE]"
    try:
        res = requests.head(URL_UPLOAD, timeout=5.0)
        if res.status_code > 0 and res.status_code < 400:
            status_text = ""
    except requests.exceptions as e:
        status_text = "[ERROR:OFFLINE]"
        print(e)
    finally:
        return status_text

    

class Scripts(scripts.Script):
    def title(self):
        return "https://webui.plus"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        if WEBUI_PLUS_USER == "" or WEBUI_PLUS_KEY == "":
            checkbox_save_to_db = gr.inputs.Checkbox(label=get_webui_plus_status() + " Save images to https://webui.plus, [please set env vars (WEBUI_PLUS_USER, WEBUI_PLUS_KEY) first.]", default=False)
        else:
            checkbox_save_to_db = gr.inputs.Checkbox(label=get_webui_plus_status() + " Save images to https://webui.plus, Author: " + WEBUI_PLUS_USER.lower(), default=True)
        
        checkbox_is_private = gr.inputs.Checkbox(label="Public Images", default=False)

        return [checkbox_save_to_db, checkbox_is_private]

    def postprocess(self, p, processed,checkbox_save_to_db,checkbox_is_private):
        if not checkbox_save_to_db:
            return True
        
        is_public = 0
        if checkbox_is_private:
            is_public = 1

        global WEBUI_PLUS_USER
        global WEBUI_PLUS_KEY

        sess = requests.session()
        sess.keep_alive = False
             
        for i in range(len(processed.images)):

            try:
                # Extract image information
                regex = r"Steps:.*$"
                seed = processed.seed
                prompt = processed.prompt
                neg_prompt = processed.negative_prompt
                info = re.findall(regex, processed.info, re.M)[0]
                input_dict = {}
                kvs = str(info).split(", ")
                for kv in kvs:
                    keyval = kv.split(": ")
                    if len(keyval) == 2:
                        if len(keyval[0]) > 0:
                            input_dict[keyval[0]] = keyval[1]
                #input_dict = dict(item.split(": ") for item in str(info).split(", "))
                steps = int(input_dict["Steps"])
                seed = int(input_dict["Seed"])
                sampler = input_dict["Sampler"]
                cfg_scale = float(input_dict["CFG scale"])
                size = tuple(map(int, input_dict["Size"].split("x")))
                model_hash = input_dict["Model hash"]
                model = input_dict["Model"]
                schedule_type = input_dict["Schedule type"]
                version = input_dict["Version"]
                #print(input_dict)

                image = processed.images[i]               
                buffer = BytesIO()
                image.save(buffer, "png")
                image_bytes = buffer.getvalue()

                image_size = image.size
                filesize = len(image_bytes)
                if image_size[0] > size[0] or image_size[1] > size[1]:
                    continue
                #
                meta = {}
                #
                meta["username"] = WEBUI_PLUS_USER
                meta["userkey"] = WEBUI_PLUS_KEY
                meta["model"] = model
                meta["prompt"] = processed.prompt
                meta["file_mime"] = "image/png"
                meta["file_md5"] = hashlib.md5(image_bytes).hexdigest()
                #
                meta["raw_info"] = processed.info
                meta["steps"] = steps
                meta["sampler"] = sampler
                meta["cfg_scale"] = cfg_scale
                meta["model_hash"] = model_hash
                meta["version"] = input_dict["Version"]
                meta["schedule_type"] = schedule_type
                meta["seed"] = processed.seed
                meta["neg_prompt"] = processed.negative_prompt
                meta["filesize"] = filesize
                meta["image_width"] = int(size[0]),
                meta["image_height"] = int(size[1])
                meta["is_private"] = 0
                meta["is_public"] = is_public
                #
                files = {'file': ("sd-up-tmp.png",image_bytes,'image/png')}

            except Exception as e:
                print(e)
                print("error while preparing the meta")
                continue

            if checkbox_save_to_db and filesize > 0:
                print("\nuploading filesize: %d" % (filesize,))
                try:
                    res = sess.post(url=URL_UPLOAD,files=files, data=meta, stream=True)
                    print(res.status_code, ": ", res.content.decode('utf-8'))
                except Exception as e:
                    print(f"ERROR: {e}")
                    sess.close()
                    sess = requests.session()
                    sess.keep_alive = False


        return True
