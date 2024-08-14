import base64
import datetime
import time
from io import BytesIO
import os
import re
import math
import modules.scripts as scripts
import gradio as gr
import json
import hashlib
import grequests
import requests


URL_UPLOAD = "http://u2.webui.plus/upload"

WEBUI_PLUS_USER = os.environ.get('WEBUI_PLUS_USER', '')
WEBUI_PLUS_KEY = os.environ.get('WEBUI_PLUS_KEY', '')

def err_handler(request, exception):
    print("Request failed.", request.headers)

class Scripts(scripts.Script):
    def title(self):
        return "https://webui.plus"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        if WEBUI_PLUS_USER == "" or WEBUI_PLUS_KEY == "":
            checkbox_save_to_db = gr.inputs.Checkbox(label="Save images to https://webui.plus, [please set env vars (WEBUI_PLUS_USER, WEBUI_PLUS_KEY) first].", default=True)
        else:
            checkbox_save_to_db = gr.inputs.Checkbox(label="Save images to https://webui.plus, Author: " + WEBUI_PLUS_USER, default=True)
        
        checkbox_is_private = gr.inputs.Checkbox(label="Do NOT share my images", default=False)

        return [checkbox_save_to_db, checkbox_is_private]

    def postprocess(self, p, processed,checkbox_save_to_db,checkbox_is_private):
        if not checkbox_save_to_db:
            return True
        
        post_list = []
        post_size = 0
        post_count = 0

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

            if checkbox_save_to_db:
                post_list.append(grequests.post(URL_UPLOAD, data=meta))
                post_size += meta["filesize"]
                post_count += 1
        
        upload_start = time.time()
        for res in grequests.imap(post_list, size=10,exception_handler=err_handler):
            print(res.status_code," - ", res.content.decode('utf-8'))
        
        upload_duration = math.ceil(time.time() - upload_start)
        post_size = math.ceil(post_size / 1024)
        print(f"\033[1;32m*** uploaded: {post_count} files, size: {post_size} KB, duration: {upload_duration} s ***\033[0m")
        post_list.clear()

        return True
