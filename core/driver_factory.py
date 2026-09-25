"""
Creación del driver. Por defecto se usa Appium conectado a Google Chrome.

Requisitos (una sola vez):
    appium driver install chromium        # Chrome de escritorio
    appium driver install uiautomator2    # Chrome en Android (ya instalado)
    appium --relaxed-security             # levantar el server
"""
import platform

from appium import webdriver as appium_webdriver
from appium.options.common import AppiumOptions
from selenium import webdriver as selenium_webdriver

from config import settings


def _plataforma_escritorio():
    return {"Darwin": "mac", "Windows": "windows"}.get(platform.system(), "linux")


def _argumentos_chrome():
    args = [f"--window-size={settings.VENTANA[0]},{settings.VENTANA[1]}", "--lang=es-MX"]
    if settings.HEADLESS:
        args.append("--headless=new")
    return args


def crear_driver(modo=None):
    modo = modo or settings.MODO_DRIVER

    if modo == "appium_desktop":
        opciones = AppiumOptions()
        opciones.load_capabilities({
            "platformName": _plataforma_escritorio(),
            "browserName": "chrome",
            "appium:automationName": "Chromium",
            "acceptInsecureCerts": True,
            "goog:chromeOptions": {"args": _argumentos_chrome()},
        })
        driver = appium_webdriver.Remote(settings.APPIUM_URL, options=opciones)

    elif modo == "appium_android":
        opciones = AppiumOptions()
        opciones.load_capabilities({
            "platformName": "Android",
            "browserName": "Chrome",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": settings.ANDROID_DEVICE,
            "appium:chromedriverAutodownload": True,  # requiere --allow-insecure chromedriver_autodownload
            "acceptInsecureCerts": True,
        })
        driver = appium_webdriver.Remote(settings.APPIUM_URL, options=opciones)

    elif modo == "selenium":
        opciones = selenium_webdriver.ChromeOptions()
        opciones.accept_insecure_certs = True
        for arg in _argumentos_chrome():
            opciones.add_argument(arg)
        driver = selenium_webdriver.Chrome(options=opciones)

    else:
        raise ValueError(f"MODO_DRIVER no soportado: {modo}")

    driver.implicitly_wait(0)
    return driver


def simular_sin_conexion(driver, sin_conexion=True):
    """Corta/restablece la red del navegador (TC-BP-041 y TC-BP-042)."""
    condiciones = {"offline": sin_conexion, "latency": 0,
                   "download_throughput": -1, "upload_throughput": -1}
    if hasattr(driver, "set_network_conditions"):          # Selenium Chrome
        driver.set_network_conditions(**condiciones)
    elif hasattr(driver, "set_network_connection"):        # Appium Android
        driver.set_network_connection(0 if sin_conexion else 6)
    else:
        raise NotImplementedError("El driver actual no permite simular pérdida de conexión")
