import launch

if not launch.is_installed("requests"):
    launch.run_pip("install requests", "requirements for sd-webui-save-images-to-webui-plus")
if not launch.is_installed("gevent"):
    launch.run_pip("install gevent", "requirements for sd-webui-save-images-to-webui-plus")
if not launch.is_installed("grequests"):
    launch.run_pip("install grequests", "requirements for sd-webui-save-images-to-webui-plus")