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


def ejecutar_cdp(driver, comando, parametros=None):
    """Envía un comando del protocolo de depuración de Chrome (CDP).
    El driver Chromium de Appium reenvía el endpoint de chromedriver /goog/cdp/execute."""
    if "cdp_execute" not in driver.command_executor._commands:
        driver.command_executor.add_command("cdp_execute", "POST", "/session/$sessionId/goog/cdp/execute")
    return driver.execute("cdp_execute", {"cmd": comando, "params": parametros or {}})["value"]


def simular_sin_conexion(driver, sin_conexion=True):
    """Corta/restablece la red del navegador (TC-BP-041 y TC-BP-042)."""
    if settings.MODO_DRIVER == "appium_android":
        driver.set_network_connection(0 if sin_conexion else 6)
        return
    ejecutar_cdp(driver, "Network.enable")
    ejecutar_cdp(driver, "Network.emulateNetworkConditions", {
        "offline": sin_conexion, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})
