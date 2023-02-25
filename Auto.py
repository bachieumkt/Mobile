import threading
import time
from appium import webdriver

# Đọc danh sách thiết bị từ file
def read_device_list(file_path):
    with open(file_path, "r") as f:
        devices = [line.strip() for line in f if line.strip()]
    return devices

# Đọc danh sách proxy từ file
def read_proxy_list(file_path):
    with open(file_path, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies

# Thiết lập proxy cho thiết bị
def set_proxy(device_id, proxy):
    desired_caps = {
        "platformName": "Android",
        "platformVersion": "9.0",
        "deviceName": device_id,
        "appPackage": "com.android.chrome",
        "appActivity": "com.google.android.apps.chrome.Main",
        "noReset": True,
        "newCommandTimeout": 300,
        "chromeOptions": {
            "androidPackage": "com.android.chrome",
            "androidUseRunningApp": True,
            "androidDeviceSerial": device_id,
            "args": [
                f"--proxy-server=http://{proxy}",
                "--ignore-certificate-errors",
                "--disable-extensions",
                "--disable-gpu",
                "--disable-popup-blocking",
                "--no-first-run",
                "--no-default-browser-check",
                "--start-maximized",
                "--disable-infobars",
                "--disable-notifications",
            ],
        },
    }
    driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
    return driver

# Tìm kiếm trên google và chuyển đến trang có chứa 'cryptocloud9'
def open_google_search(driver):
    search_box = driver.find_element_by_xpath("//input[@name='q']")
    search_box.clear()
    search_box.send_keys("cryptocloud9")
    search_box.submit()
    time.sleep(5)
    try:
        link = driver.find_element_by_xpath("//a[contains(@href,'cryptocloud9')]")
        link.click()
        print(f"Clicked link on {driver.desired_capabilities['deviceName']}")
        return True
    except:
        return False

# Thực thi trên mỗi thread
def execute(device_id, proxy):
    # Thiết lập proxy
    driver = set_proxy(device_id, proxy)
    
    # Tìm kiếm và click vào link chứa 'cryptocloud9'
    found_link = False
    while not found_link:
        found_link = open_google_search(driver)
        if not found_link:
            try:
                driver.swipe(500, 1500, 500, 500, 1000)
            except:
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
    time.sleep(5)
    driver.quit()

# Đọc danh sách thiết bị
devices = read_device_list("devices.txt")
# Đọc danh sách proxy
proxies = read_proxy_list("workProxy.txt")

# Tạo và thực thi thread trên mỗi thiết bị
threads = []
for i, device_id in enumerate(devices):
    proxy = proxies[i % len(proxies)]
    t = threading.Thread(target=execute, args=(device_id, proxy))
    threads.append(t)
    t.start()

# Đợi tất cả các thread hoàn thành
for t in threads:
    t.join()



