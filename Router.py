#!/usr/bin/python3
import os
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (TimeoutException, UnexpectedAlertPresentException, NoSuchElementException)
from selenium.webdriver.chrome.options import Options

import ConstantName as CN
import RouterConfig as routerconfig


# =======if running on orange pi=============
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')


class RouterSetting(object):
    def __init__(self,device):
        '''
        Summary:
            Initialize arguments based on default configuration file.
            
        Description:
            1) Initialize arguments based on default configuration file.
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                from Api.at import HardwareFactory

                
                router = HardwareFactory.Network.GetHardware(hardwaretype = 'asus')
                
        Returns:
            An object of AsusRouter.
        
        Caveat:
            Communication channel through OrangePi.
        '''
        print("Configuring router...")
        if routerconfig.hardware['HARDWAREINFO']['IP'] is None:
            raise ValueError("Please configure RouterConfig ['HARDWAREINFO']['IP'] at Api\setting\hardware")
        else:
            print("Configuring completed")
        ROUTERURL = 'http://' + routerconfig.hardware['HARDWAREINFO']['IP'] + '/Main_Login.asp'
        if device.lower() == 'orangepi':
            self.browser = webdriver.Chrome(chrome_options=chrome_options)
            self.browser.get(ROUTERURL)
        elif device.lower() == 'pc':
            self.browser = webdriver.Chrome()
            self.browser.get(ROUTERURL)
        else:
            raise ValueError("Device not supported. Please check the API documentation")


    def sign_in(self, username, password):
        '''
        Summary:
            Sign in on the router webpage
            
        Description:
            1) Sign in on the router webpage
            
        Args:
            self: self
            username: (Type: string) Username to the router webpage
            password: (Type: string) Password to the router webpage
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                from Api.at import HardwareFactory

                
                router.sign_in('hello', 'hello123')
                
        Returns:
            
        
        Caveat:
            Communication channel through OrangePi.
        '''
        self.browser.find_element_by_id(CN.LOGIN_USER).send_keys(username)
        self.browser.find_element_by_name(CN.LOGIN_PASS).send_keys(password)
        self.browser.find_element_by_class_name(CN.SIGN_IN_BUTTON).click()
        self.browser.implicitly_wait(5)
        try:
            err_msg = self.browser.find_element_by_id(CN.LOGIN_ERROR)
            print("Login unsuccessfull:" + err_msg.text)
        except:
            print("Login Successfull")

    def reboot(self):
        '''
        Summary:
            To reboot router
        
        Description:
            1) To reboot router
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                router.reboot()
                
        Returns:
            None
        
        Caveat:
            Automatically wait for 5 minutes.
        '''         
        try:
            self.browser.find_element_by_xpath(CN.REBOOT_BUTTON).click()
            self.browser.switch_to.alert.accept()
            print("rebooting router...")
            self.browser.implicitly_wait(300)
            print("rebooting completed")
        except NoSuchElementException as err:
            print(str(err))

    def set_bandwidth_limit(self, target_device, download_rate, upload_rate):
        '''
        Summary:
            To set the bandwidth rate of device
        
        Description:
            1) To set the bandwidth rate of device
            
        Args:
            self: self
            download_rate: (Type: Integer) Download rate limit in Mbps
            upload_rate: (Type: Integer) Uplaod rate limit in Mbps
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                download_rate = 50
                upload_rate = 25
                router.set_bandwidth_limit(download_rate,upload_rate)
                
        Returns:
            None
        
        Caveat:
            None
        ''' 
        self.browser.find_element_by_xpath(CN.BANDWIDTH_MENU).click()
        self.browser.find_element_by_xpath(CN.QOS).click()
        self.browser.implicitly_wait(5)
        try:
            self.browser.find_element_by_id(CN.PULL_DOWN_MENU).click()
            self.browser.find_element_by_id(target_device).click()
            self.browser.find_element_by_id(CN.DOWNLOAD_RATE).send_keys(download_rate)
            self.browser.find_element_by_id(CN.UPLOAD_RATE).send_keys(upload_rate)
            self.browser.find_element_by_id(CN.ADD_DELETE_DEVICE).click()
            # self.browser.find_element_by_xpath('//*[@id="FormTitle"]/tbody/tr/td/table[5]/tbody/tr/td/div/span').click()
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # to scroll down
            self.browser.find_element_by_xpath(CN.APPLY).click()
            self.browser.implicitly_wait(15)
            print("Successfully set the bandwidth limit of {}'s device to {}".format(target_device, download_rate))
        except UnexpectedAlertPresentException as err:
            print(str(err))

    def remove_bandwidth_limit(self):
        '''
        Summary:
            To remove upload and download limit.
        
        Description:
            1) To remove upload and download limit.
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                router.remove_bandwidth_setting()
                
        Returns:
            None
        
        Caveat:
            None
        ''' 
        try:
            self.browser.find_element_by_xpath(CN.BANDWIDTH_MENU).click()
            self.browser.find_element_by_xpath(CN.QOS).click()
            self.browser.implicitly_wait(5)
            msg = self.browser.find_element_by_xpath(CN.TABLE_INFO)
            expectedmsg = msg.text
            if 'No data' in expectedmsg:
                print("Set to default bandwidth setting")
            else:
                self.browser.find_element_by_xpath(CN.REMOVE_BANDWIDTH).click()
                self.browser.implicitly_wait(1)
                print("Restoring to default bandwidth setting...")
                self.browser.find_element_by_xpath(CN.APPLY).click()
                self.browser.implicitly_wait(15)
            print("Succesful")
        except UnexpectedAlertPresentException as err:
            print(str(err))

    def set_band_and_ssid(self, band_type, ssid_name):
        '''
        Summary:
            To select band type and set ssid name
        
        Description:
            1) To select band type and set ssid name
            
        Args:
            self: self
            band_type: (Type: String) To select either 2.4 GHz or 5 GHz.
            ssid_name: (Type: String) Network SSID name
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                band = '2.4GHz'
                ssid = 'SONY!!'
                router.set_band_and_ssid(band,ssid)
                
        Returns:
            None
        
        Caveat:
            None
        ''' 
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        if band_type == CN.ROUTER_5GHZ or band_type == CN.ROUTER_2GHZ:
            band.select_by_visible_text(band_type)
            self.browser.implicitly_wait(3)
            ssidName = self.browser.find_element_by_name(CN.SSIDNAME)
            ssidName.clear()
            ssidName.send_keys(ssid_name)
            try:
                self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                self.browser.switch_to.alert.accept()
                print("Setting up new ssid...")
            except TimeoutException as err:
                print(str(err))
            print("Succesful")
        else:
            raise ValueError("Invalid band type")


        

    def set_default_channel_no(self):
        '''
        Summary:
            To set default available channel
        
        Description:
            1) To set default available channel
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                router.set_default_channel_no()
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        band.select_by_visible_text(CN.DEFAULT_BAND_TYPE_2)
        self.browser.implicitly_wait(3)
        channel = Select(self.browser.find_element_by_css_selector(CN.CHANNEL_BOX))
        channel.select_by_visible_text(CN.DEFAULT_CHANNEL)
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        try:
            self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
            WebDriverWait(self.browser, 3).until(EC.alert_is_present())
            self.browser.switch_to.alert.accept()
            print("Resetting channel number...")
        except TimeoutException as err:
            print(str(err))
        print("Succesful")
 

    def set_default_channel_no_5ghz(self):
        '''
        Summary:
            To set default available channel for 5GHz
        
        Description:
            1) To set default available channel for 5GHz
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                router.set_default_channel_no_5ghz()
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        band.select_by_visible_text(CN.DEFAULT_BAND_TYPE_5)
        self.browser.implicitly_wait(3)
        channel = Select(self.browser.find_element_by_css_selector(CN.CHANNEL_BOX))
        channel.select_by_visible_text(CN.DEFAULT_CHANNEL)
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        try:
            self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
            WebDriverWait(self.browser, 3).until(EC.alert_is_present())
            self.browser.switch_to.alert.accept()
            print("Resetting channel number...")
        except TimeoutException as err:
            print(str(err))
        print("Succesful")

    def set_channel_no(self, band_type, channel_no):
        '''
        Summary:
            To set available channel for both 2.4 GHz and 5 GHz
        
        Description:
            1) To set available channel for both 2.4 GHz and 5 GHz
            
        Args:
            self: self
            band_type: (Type: String) Network band (2.4GHz or 5 GHz)
            channel_no: (Type: Integer) Channel Number. (Supported: 2.4GHz -> Auto, 1 to 11, 5GHz -> Auto, 36, 40, 44, 48, 149, 153, 157, 161 and 165)
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                band = '5GHz'
                channel = 153
                router.set_channel_no(band,channel)
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        if band_type == CN.ROUTER_5GHZ or band_type == CN.ROUTER_2GHZ:
            band.select_by_visible_text(band_type)
            self.browser.implicitly_wait(3)
            channel = Select(self.browser.find_element_by_css_selector(CN.CHANNEL_BOX))
            channel.select_by_visible_text(channel_no)
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            try:
                self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                self.browser.switch_to.alert.accept()
                print("Setting channel number...")
            except TimeoutException as err:
                print(str(err))
            print("Succesful")
        else:
            raise ValueError("Invalid band type")

    def set_default_authentication_method(self):
        '''
        Summary:
            To set default authentication method for 2.4 GHz.
        
        Description:
            1) To set default authentication method for 2.4 GHz.
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
               
                router.set_default_authentication_method()
                
        Returns:
            None
        
        Caveat:
            None
        '''
        try:
            self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
            band = Select(self.browser.find_element_by_css_selector(CN.BAND))
            self.browser.implicitly_wait(3)
            # For band 2.4GHz:
            band.select_by_visible_text(CN.DEFAULT_BAND_TYPE_2)
            self.browser.implicitly_wait(3)
            authType = Select(self.browser.find_element_by_css_selector(CN.AUTH_BOX))
            authType.select_by_visible_text(CN.DEFAULT_AUTHMETHOD)
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            try:
                self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                self.browser.switch_to.alert.accept()
                print("Reset default 2.4GHz authentication method...")
            except TimeoutException as err:
                print(str(err))

            print("Succesful")
        except NoSuchElementException as err:
            print((str(err)))

    def set_default_authentication_method_5ghz(self):
        '''
        Summary:
            To set default authentication method for 5 GHz.
        
        Description:
            1) To set default authentication method for 5 GHz.
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
               
                router.set_default_authentication_method_5ghz()
                
        Returns:
            None
        
        Caveat:
            None
        '''
        try:
            self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
            band = Select(self.browser.find_element_by_css_selector(CN.BAND))
            self.browser.implicitly_wait(3)
            band.select_by_visible_text(CN.DEFAULT_BAND_TYPE_5)
            self.browser.implicitly_wait(3)
            authType = Select(self.browser.find_element_by_css_selector(CN.AUTH_BOX))
            authType.select_by_visible_text(CN.DEFAULT_AUTHMETHOD)
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            try:
                self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                self.browser.switch_to.alert.accept()
                print("Reset default 5GHz authentication method...")
            except TimeoutException as err:
                print(str(err))

            print("Succesful")
        except NoSuchElementException as err:
            print((str(err)))

    def set_authentication_method(self, band_type, authentication_type):
        '''
        Summary:
            To set authentication method for 2.4GHz or 5 GHz.
        
        Description:
            1) To set default authentication method for 2.4GHz or 5 GHz.
            
        Args:
            self: self
            band_type: (Type: String) Network band of 2.4GHz or 5GHz
            authentication_type: (Type: String) Authentication type. (Supported: Open System, WPA2-Personal, WPA-Auto_Personal)
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                band = '5GHz'
                authentication = 'WPA-Auto-Personal'
                router.set_authentication_method(band,authentication)
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        if band_type == CN.ROUTER_5GHZ or band_type == CN.ROUTER_2GHZ:
            band.select_by_visible_text(band_type)
            self.browser.implicitly_wait(3)
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # to scroll down
            authType = Select(self.browser.find_element_by_css_selector(CN.AUTH_BOX))
            authType.select_by_visible_text(authentication_type)
            self.browser.implicitly_wait(10)
            try:
                self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                self.browser.switch_to.alert.accept()
                print("Setting authentication method...")
            except TimeoutException as err:
                print(str(err))
            print("Succesful")
        else:
            print("Invalid band type")

    def set_default_wifi_password(self,new_password):
        '''
        Summary:
            To set default WiFi password.
        
        Description:
            1) To set default WiFi password.
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                router.set_default_wifi_password()
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        band.select_by_visible_text(CN.DEFAULT_BAND_TYPE_2)
        authType = Select(self.browser.find_element_by_css_selector(CN.AUTH_BOX))
        authType.select_by_visible_text(CN.DEFAULT_AUTHMETHOD)
        self.browser.implicitly_wait(3)
        password = self.browser.find_element_by_name(CN.WPA_PRESHARED_KEY)
        password.clear()
        password.send_keys(new_password)
        try:
            print("Reset 2.4GHz wifi password...")
            self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
            WebDriverWait(self.browser, 3).until(EC.alert_is_present())
            self.browser.switch_to.alert.accept()
        except TimeoutException as err:
            print(str(err))
        print("Succesful")
        
    def set_default_wifi_password_5ghz(self,new_password):
        '''
        Summary:
            To set default WiFi password for 5GHz.
        
        Description:
            1) To set default WiFi password for 5GHz.
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                router.set_default_wifi_password_5ghz()
                
        Returns:
            None
        
        Caveat:
            None
        '''    
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        band.select_by_visible_text(CN.DEFAULT_BAND_TYPE_5)
        authType = Select(self.browser.find_element_by_css_selector(CN.AUTH_BOX))
        authType.select_by_visible_text(CN.DEFAULT_AUTHMETHOD)
        self.browser.implicitly_wait(3)
        password = self.browser.find_element_by_name(CN.WPA_PRESHARED_KEY)
        password.clear()
        password.send_keys(new_password)
        try:
            print("Reset 5GHz wifi password...")
            self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
            WebDriverWait(self.browser, 3).until(EC.alert_is_present())
            self.browser.switch_to.alert.accept()
        except TimeoutException as err:
            print(str(err))
        print("Succesful")

    def set_wifi_password(self, band_type, authentication_type, new_password):
        '''
        Summary:
            To set WiFi password for both 2.4GHz and 5 GHz band.
        
        Description:
            1) To set WiFi password for both 2.4GHz and 5 GHz band.
            
        Args:
            self: self
            band_type: (Type: String) Network band of either 2.4 GHz or 5 GHz
            authentication_type: (Type: String): Authentication type. (Supported: Open System, WPA2-Personal, WPA-Auto_Personal)
            new_password: (Type: String) Set a new password.
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                band = '5GHz'
                authentication = 'Open System'
                pass = 'PASSWORD!?!?!?!?'
                router.set_wifi_password(band,authentication,pass)
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        if band_type == CN.ROUTER_5GHZ or band_type == CN.ROUTER_2GHZ:
            band.select_by_visible_text(band_type)
            self.browser.implicitly_wait(3)
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # to scroll down
            if authentication_type == CN.ROUTER_WPA2PERSONAL or authentication_type == CN.ROUTER_WPAAUTOPERSONAL:
                authType = Select(self.browser.find_element_by_css_selector(CN.AUTH_BOX))
                authType.select_by_visible_text(authentication_type)
                self.browser.implicitly_wait(2)
                password = self.browser.find_element_by_name(CN.WPA_PRESHARED_KEY)
                password.clear()
                password.send_keys(new_password)
                try:
                    print("Setting up new password...")
                    self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                    WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                    self.browser.switch_to.alert.accept()
                except TimeoutException as err:
                    print(str(err))
            else:
                print("Invalid authentication type. Please check")
        else:
            raise ValueError("Invalid band type")
        print("Succesful")


    def set_wpa_encryption(self, band_type, authentication_type, encryption_type):
        '''
        Summary:
            To set WPA encryption type.
        
        Description:
            1) To set WPA encryption type
            
        Args:
            self: self
            authentication_type: (Type: String): Authentication type. (Supported: Open System, WPA2-Personal, WPA-Auto_Personal)
            encryption_type: (Type: String) Encryption selection. (Supported: AES and TKIP+AES)
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                authentication = 'WPA-Auto-Personal'
                encryption = 'AES'
                router.set_wpa_encryption(authentication,encryption)
                
        Returns:
            None
        
        Caveat:
            None
        '''
        try:
            self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
            band = Select(self.browser.find_element_by_css_selector(CN.BAND))
            band.select_by_visible_text(band_type)
            self.browser.implicitly_wait(3)
            if authentication_type == CN.ROUTER_WPAAUTOPERSONAL:
                encryptionType = Select(self.browser.find_element_by_css_selector(CN.ENCRYPTION_BOX))
                encryptionType.select_by_visible_text(encryption_type)
                self.browser.implicitly_wait(10)
                try:
                    self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                    WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                    self.browser.switch_to.alert.accept()
                    print("Setting wpa encryption...")
                except TimeoutException as err:
                    print(str(err))
            elif authentication_type == CN.ROUTER_WPA2PERSONAL:
                encryptionType = Select(self.browser.find_element_by_css_selector(CN.ENCRYPTION_BOX))
                if encryption_type == CN.ROUTER_AES:
                    encryptionType.select_by_visible_text(encryption_type)
                else:
                    print("Error: Encryption type not supported.")
                self.browser.implicitly_wait(10)
                try:
                    self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                    WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                    self.browser.switch_to.alert.accept()
                    print("Setting wpa encryption...")
                except TimeoutException as err:
                    print(str(err))
            else:
                print("Only WPA-Auto-Personal & WPA2-Personal ")
                print("have the option to use different WPA encryption method")
        except NoSuchElementException as err:
            print(str(err))

    def dhcp_control(self, dhcp_server_status, starting_address, ending_address):
        '''
        Summary:
            To configure DHCP features.
        
        Description:
            1) To configure DHCP features.
            
        Args:
            self: self
            dhcp_server_status: (Type: Boolean) : Only two options supported which are True (enable) and False (disable)
            starting_address: (Type: String) Only change value of X from '192.168.1.X'. X cannot be lower than 1.
            ending_address:  (Type: String) Only change value of X from '192.168.1.X'. X cannot be higher than 254.
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                dhcp_server_status: True
                starting_address: '192.168.1.20'
                ending_address: '192.168.1.100'

                router.dhcp_control(True, '192.168.1.25', '192.168.1.150')

                
        Returns:
            None
        
        Caveat:
            None
        '''
        try:
            self.browser.find_element_by_id(CN.LAN_MENU).click()
            self.browser.find_element_by_id(CN.DHCP_SERVER).click()
            if dhcp_server_status == True:
                self.browser.find_element_by_xpath(CN.ENABLE_DHCP_SERVER).click()
            else:
                self.browser.find_element_by_xpath(CN.UNABLE_DHCP_SERVER).click()
            # To set starting addresses
            dhcpStart = self.browser.find_element_by_xpath(CN.DHCP_STARTING)
            dhcpStart.clear()
            dhcpStart.send_keys(starting_address)

            # To set ending addresses
            dhcpEnd = self.browser.find_element_by_xpath(CN.DHCP_ENDING)
            dhcpEnd.clear()
            dhcpEnd.send_keys(ending_address)

            print("IP Pool Starting Address: %s" % (starting_address))
            print("IP Pool Ending Address: %s" % (ending_address))

            # Click apply button
            try:
                self.browser.find_element_by_xpath(CN.DHCP_APPLY).click() # to click apply, should be clicked lastly
                WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                self.browser.switch_to.alert.accept()
                print("Configuring DHCP control...")
            except TimeoutException as err:
                print(str(err))

        except NoSuchElementException as err:
            print(str(err))

    def set_default_dhcp_address(self):
        '''
        Summary:
            To configure default DHCP features.
        
        Description:
            1) To configure default DHCP features.
            
        Args:
            self: self
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                router.set_default_dhcp_address()
                
        Returns:
            None
        
        Caveat:
            None
        '''
        try:
            self.browser.find_element_by_id(CN.LAN_MENU).click()
            self.browser.find_element_by_id(CN.DHCP_SERVER).click()
            self.browser.find_element_by_xpath(CN.ENABLE_DHCP_SERVER).click()
            # To set starting addresses
            dhcpStart = self.browser.find_element_by_xpath(CN.DHCP_STARTING)
            dhcpStart.clear()
            dhcpStart.send_keys(CN.DEFAULT_STARTING_ADDRESS)
            # To set ending addresses
            dhcpEnd = self.browser.find_element_by_xpath(CN.DHCP_ENDING)
            dhcpEnd.clear()
            dhcpEnd.send_keys(CN.DEFAULT_ENDING_ADDRESS)
            # Click apply button
            try:
                print("Reset DHCP address")
                self.browser.find_element_by_xpath(CN.DHCP_APPLY).click() # to click apply, should be clicked lastly
                WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                self.browser.switch_to.alert.accept()
                print("Succesful")
            except TimeoutException as err:
                print(str(err))
        except UnexpectedAlertPresentException as err:
            print(str(err))

    def set_vpn_connection(self, vpn_type, country_name, username, password):
        '''
        Summary:
            To establish a VPN connection.
        
        Description:
            1) To establish a VPN connection.
            
        Args:
            self: self
            vpn_type: (Type: String) VPN method. (Supported: PPTP, L2TP and OpenVPN)
            country_name: (Type: String) Country VPN. (Must refer to ListCountriesVPN.csv and OpenVPN.csv for available country name. Country name must be the same as stated in .csv file)
            vpn_username: (Type: String) VPN account name
            vpn_password: (Type: String) VPN account password
            
        Raises:
            None
        
        Example:
            Below code block shows how to use::
                
                vpn = 'OpenVPN'
                country = 'FRANCE'
                vpn_id = 'admin'
                vpn_pass = 'admin123'
                router.set_vpn_connection(vpn,country,vpn_id,vpn_pass)
                
        Returns:
            None
        
        Caveat:
            None
        '''
        # Nav to VPN Tab
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # to scroll down
        self.browser.find_element_by_id(CN.VPN_TAB).click()
        # Go to VPN client tab
        self.browser.find_element_by_xpath(CN.VPN_CLIENT).click()
        # Select add profile button to add new VPN configuration
        self.browser.find_element_by_xpath(CN.ADD_PROFILE).click()
        self.browser.implicitly_wait(3)
        try:
            if vpn_type == CN.ROUTER_PPTP:
                self.browser.find_element_by_id(CN.PPTP).click()
                # description box
                desc = self.browser.find_element_by_xpath(CN.DESC_BOX)
                desc.click()

                VpnData = pd.read_csv(CN.LISTCOUNTRYVPN, header=0, usecols=["Country", "VpnServer"], engine='python')
                # creating a dataframe from a dictionary
                df = pd.DataFrame(VpnData)
                df = df[df.Country == country_name.upper()]
                if df.empty == True: #A condition to check whether the country exist or not in the list
                    print("Country not found")
                    print("Exiting application...")
                    self.browser.quit()
                else:
                    desc.send_keys(country_name)
                    vpn_server = df['VpnServer'].values[0]
                    # VPN Server box
                    server = self.browser.find_element_by_xpath(CN.SERVER_BOX)
                    server.click()
                    server.send_keys(vpn_server)
                    # VPN Username box
                    uId = self.browser.find_element_by_xpath(CN.USERNAME_BOX)
                    uId.click()
                    uId.send_keys(username)
                    # VPN password box
                    uPass = self.browser.find_element_by_xpath(CN.PASSWORD_BOX)
                    uPass.click()
                    uPass.send_keys(password)
                    # Click OK and Activate
                    self.browser.find_element_by_css_selector(CN.VPN_OK_BUTTON).click()
                    print("VPN to: %s" % country_name)
                    print("Activating VPN...")
                    self.browser.find_element_by_css_selector(CN.ACTIVATE_VPN).click()
                    self.browser.implicitly_wait(30)
                    print("VPN to: {} using {} method".format(country_name, vpn_type))

            elif vpn_type == CN.ROUTER_L2TP:
                self.browser.find_element_by_id(CN.L2TP).click()
                # description box
                desc = self.browser.find_element_by_xpath(CN.DESC_BOX)
                desc.click()
                VpnData = pd.read_csv(CN.LISTCOUNTRYVPN, header=0,usecols=["Country", "VpnServer"], engine='python')
                # creating a dataframe from a dictionary
                df = pd.DataFrame(VpnData)
                df = df[df.Country == country_name.upper()]
                if df.empty == True:
                    print("Country not found")
                    print("Exiting application...")
                    self.browser.quit()
                else:
                    desc.send_keys(country_name)
                    vpn_server = df['VpnServer'].values[0]
                    # VPN Server box
                    server = self.browser.find_element_by_xpath(CN.SERVER_BOX)
                    server.click()
                    server.send_keys(vpn_server)
                    # VPN Username box
                    uId = self.browser.find_element_by_xpath(CN.USERNAME_BOX)
                    uId.click()
                    uId.send_keys(username)
                    # VPN password box
                    uPass = self.browser.find_element_by_xpath(CN.PASSWORD_BOX)
                    uPass.click()
                    uPass.send_keys(password)
                    # Click OK and Activate
                    self.browser.find_element_by_css_selector(CN.VPN_OK_BUTTON).click()
                    print("Activating VPN...")
                    self.browser.find_element_by_css_selector(CN.ACTIVATE_VPN).click()
                    self.browser.implicitly_wait(30)
                    print("VPN to: {} using {} method".format(country_name, vpn_type))

            elif vpn_type == CN.ROUTER_OPENVPN:
                self.browser.find_element_by_id(CN.OPENVPN).click()
                # description box
                desc = self.browser.find_element_by_xpath(CN.OPENVPN_DESC_BOX)
                desc.click()
                VpnData = pd.read_csv(r'/root/Downloads/RouterAPI/OpenVPN.txt',
                                      header=0, usecols=["Country", "VpnServer"])
                # creating a dataframe from a dictionary
                df = pd.DataFrame(VpnData)
                df = df[df.Country == country_name.upper()]
                if df.empty == True:
                    print("Country not found")
                    print("Exiting application...")
                    self.browser.quit()
                else:
                    desc.send_keys(country_name)
                    vpn_filename = df['VpnServer'].values[0]
                    print(vpn_filename)
                    # Username box
                    uId = self.browser.find_element_by_xpath(CN.OPENVPN_USERNAME_BOX)
                    uId.click()
                    uId.send_keys(username)
                    # Password box
                    uPass = self.browser.find_element_by_xpath(CN.OPENVPN_PASSWORD_BOX)
                    uPass.click()
                    uPass.send_keys(password)
                    # Choose file box
                    chooseFile = self.browser.find_element_by_xpath(CN.CHOOSE_FILE)
                    vpn_dir = CN.DIROPENVPN
                    vpn_full_path = os.path.join(vpn_dir, vpn_filename)
                    chooseFile.send_keys(vpn_full_path)
                    # Upload file box
                    upload = self.browser.find_element_by_xpath(CN.UPLOAD_FILE)
                    upload.click()
                    self.browser.implicitly_wait(5)

                    # Click OK and Activate
                    element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='openvpnc_setting_openvpn']/div/input[2]")))
                    # self.browser.execute_script("arguments[0].click();", element)
                    element.click()
                    print("Activating VPN...")
                    # self.browser.implicitly_wait(120)
                    self.browser.find_element_by_css_selector(CN.ACTIVATE_VPN).click()
                    self.browser.implicitly_wait(30)
                    print("VPN to: {} using {} method".format(country_name.upper(), vpn_type))
            else:
                print("VPN type is not valid. Please choose 1 of these options: 1. PPTP 2. L2TP 3. OpenVPN")
        except UnexpectedAlertPresentException as err:
            print(str(err))


    def toggle_ssid_visibility(self, band_type, visibility):
        '''
        Summary:
            To toggle SSID visibility 
        
        Description:
            1) To toggle SSID visibility 
            
        Args:
            self: self
            band_type: (Type: String) Network band of either 2.4 GHz or 5 GHz
            visibility: (Type: String) Only support visible or hide
            None
        
        Example:
            Below code block shows how to use::
                
                band_type: '2.4GHz'
                visibility: 'hide'

                router.toggle_ssid_visibility('2.4GHz', 'hide')
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_id(CN.WIRELESS_MENU).click()
        band = Select(self.browser.find_element_by_css_selector(CN.BAND))
        self.browser.implicitly_wait(3)
        if band_type == CN.ROUTER_5GHZ or band_type == CN.ROUTER_2GHZ:
            band.select_by_visible_text(band_type)
            self.browser.implicitly_wait(3)
            if visibility == 'hide':
                self.browser.find_element_by_xpath(CN.SSID_HIDE).click()
                self.browser.implicitly_wait(3)
                try:
                    print("SSID visibility = hide")
                    self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                    WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                    self.browser.switch_to.alert.accept()
                    print("Succesful")
                except TimeoutException as err:
                    print(str(err))
            elif visibility == 'visible':
                self.browser.find_element_by_xpath(CN.SSID_VISIBLE).click()
                try:
                    print("SSID visibility = visible")
                    self.browser.find_element_by_id(CN.APPLY_BUTTON).click() # to click apply, should be clicked lastly
                    WebDriverWait(self.browser, 3).until(EC.alert_is_present())
                    self.browser.switch_to.alert.accept()
                    print("Succesful")
                except TimeoutException as err:
                   print(str(err))
            print("Succesful")
        else:
            print("Invalid band type")

    def toggle_wan_connection(self,status):
        '''
        Summary:
            To toggle WAN connection.
        
        Description:
            1) To toggle WAN connection.
            
        Args:
            self: self
            status: (Type: String) Only support on (connect) and off (disconnect).
        Example:
            Below code block shows how to use::

                router.toggle_wan_connection(status = 'off')
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_xpath(CN.WAN_MENU).click()
        if status == 'on':
            self.browser.find_element_by_xpath(CN.WAN_ON).click()
        elif status == 'off':
            self.browser.find_element_by_xpath(CN.WAN_OFF).click()
        try:
            self.browser.find_element_by_xpath(CN.WAN_APPLY).click()
            WebDriverWait(self.browser, 3).until(EC.alert_is_present())
            self.browser.switch_to.alert.accept()
            print("WAN connection = ", status)
        except TimeoutException as err:
            print(str(err))
        print("Succesful")

    def reset_router(self,ssid,ssid_5,wifi_password,wifi_password_5,username,password):
        '''
        Summary:
            To reset the router
        
        Description:
            1) To reset the router.
            
        Args:
            self: self
            
        Example:
            Below code block shows how to use::

                router.reset_router()
                
        Returns:
            None
        
        Caveat:
            None
        '''
        self.browser.find_element_by_xpath('//*[@id="Advanced_OperationMode_Content_menu"]/table/tbody/tr/td[2]').click()
        self.browser.find_element_by_xpath('//*[@id="Advanced_SettingBackup_Content_tab"]').click()
        self.browser.find_element_by_xpath('//*[@id="restoreInit"]').click()
        self.browser.find_element_by_xpath('//*[@id="FormTitle"]/tbody/tr/td/table/tbody/tr[1]/td/div[1]/input').click()
        self.browser.switch_to.alert.accept()
        time.sleep(240)
        self.browser.find_element_by_xpath('//*[@id="welcome_button"]').click()
        self.browser.find_element_by_xpath('//*[@id="wireless_ssid_0"]').send_keys(ssid) # 2.4GHz SSID
        self.browser.find_element_by_xpath('//*[@id="wireless_key_0"]').send_keys(wifi_password) # 2.4GHz Password
        self.browser.find_element_by_xpath('//*[@id="wireless_ssid_1"]').clear() 
        self.browser.find_element_by_xpath('//*[@id="wireless_ssid_1"]').send_keys(ssid_5) # 5GHz SSID
        self.browser.find_element_by_xpath('//*[@id="wireless_key_1"]').clear()
        self.browser.find_element_by_xpath('//*[@id="wireless_key_1"]').send_keys(wifi_password_5) # 5GHz Password
        self.browser.find_element_by_xpath('//*[@id="wireless_setting"]/div[2]/div[2]/div[5]/div[2]').click()
        self.browser.find_element_by_xpath('//*[@id="http_username"]').send_keys(username) # Router username
        self.browser.find_element_by_xpath('//*[@id="http_passwd"]').send_keys(password) # Router password
        self.browser.find_element_by_xpath('//*[@id="http_passwd_confirm"]').send_keys(password) # Retype router password
        self.browser.find_element_by_xpath('//*[@id="login_field"]/div[4]/div[2]').click()
        time.sleep(10)
        self.browser.find_element_by_xpath('//*[@id="amasbundle_page"]/div[2]/div[2]/div[2]/div[1]').click()
        time.sleep(20)
        self.browser.find_element_by_xpath('//*[@id="AdaptiveQoS_Bandwidth_Monitor_menu"]').click()
        time.sleep(20)
        self.browser.find_element_by_xpath('//*[@id="QoS_EZQoS_tab"]').click()
        self.browser.find_element_by_xpath('//*[@id="iphone_switch"]').click()
        time.sleep(5)
        self.browser.find_element_by_xpath('//*[@id="bw_limit_type"]').click()
        try:
            self.browser.find_element_by_xpath('//*[@id="FormTitle"]/tbody/tr/td/table[4]/tbody/tr/td/div').click() # to click apply, should be clicked lastly
            time.sleep(60)
            WebDriverWait(self.browser, 3).until(EC.alert_is_present())
            self.browser.switch_to.alert.accept()
        except TimeoutException as err:
            print(str(err))
        print("Succesful")









#========== In Development ========================================================

    # def RemoveVPNConnection(self):
    #     '''
    #     This function is to remove existing VPN connection.
    #     '''
    #     # Nav to VPN Tab
    #     self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # to scroll down
    #     self.browser.find_element_by_id(routerconfig.VPN_TAB).click()
    #     # Go to VPN client tab
    #     self.browser.find_element_by_xpath(routerconfig.VPN_CLIENT).click()
    #     self.browser.implicitly_wait(5)
    #     # self.browser.find_element_by_xpath(routerconfig.DELETE_VPN).click()
    #     element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='vpnc_clientlist_Block']/table/tbody/tr/td[5]/div")))
    #     # self.browser.execute_script("arguments[0].click();", element)
    #     element.click()
    #     print("Removing existing VPN connection")
    #     self.browser.implicitly_wait(5)

        # msg = self.browser.find_element_by_xpath(routerconfig.TABLE_INFO)
        # expectedmsg = msg.text
        # if 'No data' in expectedmsg:
        #     print("Set to default bandwidth setting")
        # else:
        #     self.browser.find_element_by_xpath(routerconfig.REMOVE_BANDWIDTH).click()
        #     self.browser.implicitly_wait(1)
        #     print("Restoring to default bandwidth setting...")
        #     self.browser.find_element_by_xpath(routerconfig.APPLY).click()
        #     self.browser.implicitly_wait(15)
        #TODO

#==============================================================================================================



username = input('Enter router username: ')
password = input('Enter router password: ')
device = input('Enter device use: ')
function = input('Choose your function: ')

AsusRouter = RouterSetting(device)
AsusRouter.sign_in(username, password)

if function == CN.ROUTER_REBOOT:
    print('reboot Function')
    AsusRouter.reboot()
elif function == CN.ROUTER_ADDBANDWIDTH:
    print('Bandwidth setting')
    macAddress = input('Enter device MAC Address: ')
    download = input('Enter download rate: ')
    upload = input('Enter upload rate: ')
    AsusRouter.set_bandwidth_limit(macAddress, download, upload)
elif function == CN.ROUTER_REMOVEBANDWIDTH:
    print("Remove bandwidth setting")
    macAddress = input('Enter device MAC Address: ')
    AsusRouter.remove_bandwidth_limit()
elif function == CN.ROUTER_SSID:
    print("Set band and SSID")
    band = input('Enter band type: ')
    ssid = input('Enter SSID: ')
    AsusRouter.set_band_and_ssid(band, ssid)
elif function == CN.ROUTER_DEFAULTCHANNEL:
    print("Set default channel no setting")
    AsusRouter.set_default_channel_no()
elif function == CN.ROUTER_DEFAULTCHANNEL5GHZ:
    print("Set default channel no setting 5GHz")
    AsusRouter.set_default_channel_no_5ghz()
elif function == CN.ROUTER_CHANNELSETTING:
    print("Set channel no setting")
    band = input('Enter band type: ')
    channel = input('Enter channel no: ')
    AsusRouter.set_channel_no(band, channel)
elif function == CN.ROUTER_DEFAULTAUTH:
    print("Set default authentication method")
    AsusRouter.set_default_authentication_method()
elif function == CN.ROUTER_DEFAULTAUTH5GHZ:
    print("Set default authentication method 5GHz")
    AsusRouter.set_default_authentication_method_5ghz()
elif function == CN.ROUTER_AUTHMETHOD:
    print("Set authentication method")
    band = input('Enter band type: ')
    authenticationType = input('Enter authentication type: ')
    AsusRouter.set_authentication_method(band, authenticationType)
elif function == CN.ROUTER_DEFAULTWIFIPASSWORD:
    print("Set default Wi-Fi password")
    newPassword = input('Enter new password: ')
    AsusRouter.set_default_wifi_password(newPassword)
elif function == CN.ROUTER_DEFAULTWIFIPASSWORD5GHZ:
    print("Set default Wi-Fi password 5GHz")
    newPassword = input('Enter new password: ')
    AsusRouter.set_default_wifi_password_5ghz(newPassword)
elif function == CN.ROUTER_WIFIPASSWORD:
    print("Set Wi-Fi password")   
    band = input('Enter band type')
    authenticationType = input('Enter authentication type: ')
    newPassword = input('Enter new password: ')
    AsusRouter.set_wifi_password(band, authenticationType, newPassword)
elif function == CN.ROUTER_WPATYPE:
    print('Set WPA encryption type')
    band = input('Enter band type: ')
    authenticationType = input('Enter authentication type: ')
    encryptionType = input('Enter encryption type: ')
    AsusRouter.set_wpa_encryption(band,authenticationType, encryptionType)
elif function == CN.ROUTER_DHCP:
    print("DHCP control setting")
    dhcpServerStatus = input("Enter DHCP server status: ")
    startingAddress = input("Enter the starting address: ")
    endingAddress = input("Enter the ending address: ")
    AsusRouter.dhcp_control(dhcpServerStatus, startingAddress, endingAddress)
elif function == CN.ROUTER_DEFAULTDHCP:
    print("Set default DHCP address")
    AsusRouter.set_default_dhcp_address()
elif function == CN.ROUTER_VPN:
    print("VPN connection setting")
    vpnType = input("Enter VPN type: ")
    countryName = input("Enter country name: ")
    vpnUsername = input("Enter vpn username: ")
    vpnPassword = input("Enter vpn password: ")
    AsusRouter.set_vpn_connection(vpnType, countryName, vpnUsername, vpnPassword)
elif function == CN.ROUTER_TOGGLESSIDVISIBILITY:
    print("Toggle SSID visibility")
    band = input('Enter band type: ')
    visibility =  input('Choose visibility: ')
    AsusRouter.toggle_ssid_visibility(band, visibility)
elif function == CN.ROUTER_TOGGLEWANCONNECTION:
    print("Toggle WAN connection")
    status = input('Enter WAN connection status: ')
    AsusRouter.toggle_wan_connection(status)
elif function == CN.ROUTER_RESET:
    print("Resetting router")
    ssid = input('Enter SSID 2.4GHz: ')
    ssid_5 = input('Enter SSID 5GHz: ')
    wifi_password = input('Enter Wifi password 2.4GHz: ')
    wifi_password_5 = input('Enter Wifi password GHz: ')
    username = input('Enter router username: ')
    password = input('Enter router password: ')
    AsusRouter.reset_router(ssid,ssid_5,wifi_password,wifi_password_5,username,password)



#     startingAddress = ""
#     endingAddress = ""
#     ASUSRouter.dhcp_control(dhcpServerStatus, startingAddress, endingAddress)
# elif function == '9':
#     print()
# elif function == '10':
#     print()
# elif function == '11':
#     print()
#
#
