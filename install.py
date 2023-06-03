import launch

if not launch.is_installed("requests"):
    launch.run_pip("install requests", "requirements for sd-webui-save-images-to-webui-plus")
