import launch

if not launch.is_installed("pymongo"):
    launch.run_pip("install pymongo", "requirements for save-to-webui-plus")

if not launch.is_installed("requests"):
    launch.run_pip("install requests", "requirements for save-to-webui-plus")
