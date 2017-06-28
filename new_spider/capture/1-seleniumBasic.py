from selenium import webdriver
import time
# E:\python\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs.exe

path = u"E:\python\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs.exe"
driver = webdriver.PhantomJS(executable_path=path)
driver.get("http://pythonscraping.com/pages/javascript/ajaxDemo.html")
time.sleep(3)
print(driver.find_element_by_id("content").text)
driver.close()