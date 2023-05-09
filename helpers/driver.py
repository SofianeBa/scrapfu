import sys
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import zipfile,os

base_url = "https://www.wakfu.com"

def create_driver(options):
    #if sys.platform == 'win32':
        #driver = webdriver.Chrome('.\webdriver\chromedriver.exe', options=options)  
    #if sys.platform == 'linux' or sys.platform == 'linux2':
        #driver = webdriver.Chrome('./webdriver/chromedriver', options=options)
    return proxy_chrome('10.234.168.99',8080,'sbabouri','ySbtpQ7$GDhh')

def create_full_url(addition):
    return base_url + addition


def proxy_chrome(PROXY_HOST,PROXY_PORT,PROXY_USER,PROXY_PASS):
    manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%(host)s",
                port: parseInt(%(port)d)
              },
              bypassList: ["foobar.com"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%(user)s",
                password: "%(pass)s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
        """ % {
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "user": PROXY_USER,
            "pass": PROXY_PASS,
        }


    pluginfile = 'helpers/extension/proxy_auth_plugin.zip'

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    co = Options()
    #extension support is not possible in incognito mode for now
    #co.add_argument('--incognito')
    co.add_argument('--disable-gpu')
    #disable infobars
    co.add_argument('--disable-infobars')
    co.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    co.add_experimental_option('excludeSwitches', ['enable-logging'])
    #location of chromedriver, please change it according to your project.
    chromedriver = '.\webdriver\chromedriver.exe'
    co.add_extension(pluginfile)
    driver = webdriver.Chrome(chromedriver,chrome_options=co)
    #return the driver with added proxy configuration.
    return driver