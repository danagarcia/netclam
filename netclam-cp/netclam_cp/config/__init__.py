class Config:
    app = {
        "title": "NetClam Control Plane (CP)",
        "description": "### Control Plane API for the NetClam OSS project.",
        "version": "0.1.0",
        "contact": {
            "name": "Dana Garcia",
            "url": "https://thedanagarcia.com/#contact-section",
            "email": "dana_sean_garcia@live.com"
        },
        "license_info": {
            "name": "GNU GPL v2",
            "url": "https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html"
        }
    }
    server = {
        "port": 8080,
        "log_level": "info"
    }
    metrics = {
        "namespace": "netclam",
        "subsystem": "controlplane",
        "enabled": True
    }