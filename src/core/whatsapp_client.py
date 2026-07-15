"""
====================================================================
WHATSAPP CLIENT - WhatsApp Web Automation
====================================================================

Uses selenium with webdriver-manager for automatic browser setup.
Supports both WhatsApp Web (free) and WhatsApp Business Cloud API.

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import selenium
SELENIUM_AVAILABLE = False
SeleniumWebDriver = None

try:
    from selenium import webdriver as SeleniumWebDriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    pass  # Selenium not available, will use mock mode


class WhatsAppClient:
    """
    WhatsApp Web Client using Selenium
    
    Features:
    - QR code scanning authentication
    - Session persistence (save/load)
    - Message sending and receiving
    - Auto-reply support
    - Chat monitoring
    """
    
    BASE_URL = "https://web.whatsapp.com"
    
    def __init__(
        self,
        session_dir: str = "data/session",
        headless: bool = False,
        verbose: bool = True
    ):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.verbose = verbose
        
        self.driver = None
        self.is_connected = False
        self._message_callback: Optional[Callable] = None
        self._running = False
        
        logger.info(f"WhatsApp Client initialized (session_dir: {session_dir})")
    
    def _log(self, message: str):
        """Print log message if verbose mode is enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📱 {message}")
    
    def _setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError(
                "Selenium not installed!\n"
                "Run: pip install selenium webdriver-manager"
            )
        
        from selenium import webdriver as SeleniumWebDriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Chrome options for WhatsApp
        options = Options()
        options.add_argument("--user-data-dir=./data/chrome-profile")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        
        # Speech recognition and notifications
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--use-fake-device-for-media-stream")
        
        if self.headless:
            options.add_argument("--headless=new")
        
        # Try to use webdriver-manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = SeleniumWebDriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.warning(f"webdriver-manager failed: {e}, trying direct chromedriver")
            driver = SeleniumWebDriver.Chrome(options=options)
        
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)
        
        return driver
    
    def connect(self) -> bool:
        """
        Connect to WhatsApp Web
        
        Returns:
            bool: True if connected successfully
        """
        self._log("Connecting to WhatsApp Web...")
        
        try:
            # Setup driver
            self.driver = self._setup_driver()
            
            # Try to load existing session
            if not self._load_session():
                # Need to scan QR code
                self._log("No session found. Please scan QR code!")
                self._scan_qr()
            
            # Wait for WhatsApp to load
            self._wait_for_load()
            
            self.is_connected = True
            self._log("✅ Connected to WhatsApp!")
            
            # Save session for next time
            self._save_session()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.is_connected = False
            return False
    
    def _scan_qr(self):
        """Scan QR code for authentication"""
        self._log("Opening WhatsApp Web...")
        self.driver.get(self.BASE_URL)
        
        # Wait for QR code to appear
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Look for QR code image
                qr_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        '//div[@data-ref][@role="img"]'
                    ))
                )
                
                if qr_container:
                    self._log("QR Code displayed! Scan within 20 seconds...")
                    
                    # Wait for QR to be scanned
                    time.sleep(25)
                    
                    # Check if logged in
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((
                                By.XPATH,
                                '//div[@data-testid="chat-list-search"]'
                            ))
                        )
                        self._log("QR Code scanned successfully!")
                        break
                    except TimeoutException:
                        self._log("QR expired. Waiting for new QR...")
                        continue
                        
            except TimeoutException:
                # Check if already logged in
                try:
                    search_box = self.driver.find_element(
                        By.XPATH,
                        '//div[@data-testid="chat-list-search"]'
                    )
                    self._log("Already logged in!")
                    break
                except NoSuchElementException:
                    self._log("Waiting for QR code...")
                    time.sleep(2)
    
    def _wait_for_load(self):
        """Wait for WhatsApp to fully load"""
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[@data-testid="chat-list-search"] | //div[@data-testid="side"]'
                ))
            )
            time.sleep(2)  # Extra wait for full render
        except TimeoutException:
            raise RuntimeError("WhatsApp failed to load")
    
    def _save_session(self):
        """Save browser cookies for session persistence"""
        try:
            if self.driver:
                cookies = self.driver.get_cookies()
                session_file = self.session_dir / "session.json"
                with open(session_file, 'w') as f:
                    json.dump(cookies, f)
                logger.info("Session saved")
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")
    
    def _load_session(self) -> bool:
        """Load saved session cookies"""
        session_file = self.session_dir / "session.json"
        
        if not session_file.exists():
            return False
        
        try:
            # Open WhatsApp first
            self.driver.get(self.BASE_URL)
            time.sleep(3)
            
            # Load cookies
            with open(session_file, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    pass
            
            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(3)
            
            # Check if session is valid
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '//div[@data-testid="chat-list-search"]'
                    ))
                )
                logger.info("Session loaded successfully")
                return True
            except TimeoutException:
                logger.warning("Session expired")
                return False
                
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            return False
    
    def send_message(self, phone: str, message: str) -> bool:
        """
        Send message to a phone number
        
        Args:
            phone: Phone number with country code (e.g., 919876543210)
            message: Message text
            
        Returns:
            bool: True if sent successfully
        """
        if not self.is_connected or not self.driver:
            logger.error("Not connected to WhatsApp")
            return False
        
        try:
            # Format phone number
            phone = phone.replace("+", "").replace(" ", "").replace("-", "")
            if not phone.endswith("@c.us"):
                phone = f"{phone}@c.us"
            
            # Open chat
            url = f"{self.BASE_URL}/send?phone={phone.replace('@c.us', '')}"
            self.driver.get(url)
            time.sleep(4)
            
            # Wait for message input
            message_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[@data-testid="conversation-compose-box-input"] | '
                    '//footer//div[@contenteditable="true"][@data-tab="10"]'
                ))
            )
            
            # Type message
            message_box.click()
            message_box.clear()
            message_box.send_keys(message)
            time.sleep(0.5)
            
            # Find and click send button
            send_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[@data-testid="send"] | '
                    '//span[@data-testid="send"] | '
                    '//div[@data-testid="send"]/..'
                ))
            )
            send_button.click()
            
            self._log(f"Message sent to {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def get_unread_messages(self) -> List[Dict[str, Any]]:
        """
        Get all unread messages
        
        Returns:
            List of dicts with 'sender', 'message', 'time'
        """
        messages = []
        
        if not self.is_connected or not self.driver:
            return messages
        
        try:
            # Find all chat panels
            chats = self.driver.find_elements(
                By.XPATH,
                '//div[@data-testid="chat-list-item"]'
            )
            
            for chat in chats[:10]:  # Check first 10 chats
                try:
                    # Check if unread
                    unread = chat.find_elements(
                        By.XPATH,
                        './/span[@data-testid="icon-unread-count"]'
                    )
                    
                    if unread:
                        # Get sender name
                        sender_elem = chat.find_element(
                            By.XPATH,
                            './/span[@data-testid="contact-name"] | .//div[@data-testid="conversation-info-header"]//span'
                        )
                        sender = sender_elem.text if sender_elem else "Unknown"
                        
                        # Click to open chat
                        chat.click()
                        time.sleep(2)
                        
                        # Get messages
                        msg_elems = self.driver.find_elements(
                            By.XPATH,
                            '//div[@class="message-in"]//span[@data-testid="quoted-message-bubble"] | '
                            '//div[@class="message-in"]//div[@data-testid="message-bubble"]'
                        )
                        
                        for msg_elem in msg_elems[-3:]:  # Last 3 messages
                            msg_text = msg_elem.text.strip()
                            if msg_text:
                                messages.append({
                                    "sender": sender,
                                    "message": msg_text,
                                    "time": datetime.now().isoformat()
                                })
                        
                        # Go back
                        self.driver.back()
                        time.sleep(1)
                        
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
        
        return messages
    
    def start_monitoring(self, callback: Callable[[str, str], str]):
        """
        Start monitoring for new messages
        
        Args:
            callback: Function that takes (sender, message) and returns response
        """
        if not self.is_connected:
            logger.error("Not connected to WhatsApp")
            return
        
        self._message_callback = callback
        self._running = True
        self._log("Started monitoring for messages...")
        
        last_message = ""
        
        while self._running:
            try:
                # Find the search/input area
                # Get the last message
                try:
                    messages = self.driver.find_elements(
                        By.XPATH,
                        '//div[@class="message-in"]//div[@data-testid="message-bubble"]'
                    )
                    
                    if messages:
                        latest = messages[-1].text.strip()
                        
                        if latest and latest != last_message:
                            last_message = latest
                            
                            # Get sender
                            try:
                                header = self.driver.find_element(
                                    By.XPATH,
                                    '//div[@data-testid="conversation-info-header"]//span[@title]'
                                )
                                sender = header.get_attribute("title") or "Unknown"
                            except:
                                sender = "Unknown"
                            
                            self._log(f"New message from {sender}: {latest[:50]}...")
                            
                            # Get response from callback
                            if self._message_callback:
                                response = self._message_callback(sender, latest)
                                if response:
                                    # Find and click reply
                                    try:
                                        menu = self.driver.find_element(
                                            By.XPATH,
                                            '//div[@data-testid=" JPMcc"]'
                                        )
                                        menu.click()
                                        time.sleep(0.5)
                                        
                                        reply_option = self.driver.find_element(
                                            By.XPATH,
                                            '//div[@data-testid="reply"]'
                                        )
                                        reply_option.click()
                                        time.sleep(0.5)
                                    except:
                                        pass
                                    
                                    # Type and send response
                                    try:
                                        input_box = self.driver.find_element(
                                            By.XPATH,
                                            '//div[@data-testid="conversation-compose-box-input"]'
                                        )
                                        input_box.send_keys(response)
                                        time.sleep(0.5)
                                        
                                        send_btn = self.driver.find_element(
                                            By.XPATH,
                                            '//button[@data-testid="send"]'
                                        )
                                        send_btn.click()
                                        
                                        self._log(f"Sent auto-reply: {response[:50]}...")
                                    except Exception as e:
                                        logger.error(f"Failed to send auto-reply: {e}")
                            
                except NoSuchElementException:
                    pass
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(5)
    
    def stop_monitoring(self):
        """Stop monitoring for messages"""
        self._running = False
        self._log("Stopped monitoring")
    
    def disconnect(self):
        """Disconnect from WhatsApp"""
        self._running = False
        self._save_session()
        
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        
        self.is_connected = False
        self._log("Disconnected from WhatsApp")
    
    def get_qr_code(self) -> Optional[str]:
        """Get current QR code as base64 (for display in web UI)"""
        if not self.driver:
            return None
        
        try:
            qr = self.driver.find_element(By.XPATH, '//div[@data-ref][@role="img"]')
            return qr.screenshot_as_base64
        except Exception:
            return None


# ========================
# SIMPLE WhatsApp API Client (No Selenium)
# ========================

class WhatsAppCloudAPI:
    """
    WhatsApp Business Cloud API Client
    
    This is a simpler alternative that uses WhatsApp's official API.
    Requires a Meta Business App setup.
    
    Get started: https://developers.facebook.com/docs/whatsapp
    """
    
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.api_url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    
    def send_message(self, to: str, message: str) -> bool:
        """Send message via Cloud API"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Message sent via Cloud API to {to}")
                return True
            else:
                logger.error(f"Cloud API error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False


# ========================
# MOCK Client for Testing
# ========================

class MockWhatsAppClient:
    """
    Mock WhatsApp client for testing without browser
    
    Simulates receiving and sending messages for testing purposes.
    """
    
    def __init__(self):
        self.is_connected = True
        self.messages_sent = []
        self._log("Mock WhatsApp Client initialized")
    
    def _log(self, msg):
        print(f"[MOCK] {msg}")
    
    def connect(self) -> bool:
        self._log("Connected (mock)")
        return True
    
    def send_message(self, phone: str, message: str) -> bool:
        self.messages_sent.append({"to": phone, "message": message})
        self._log(f"Sent to {phone}: {message[:30]}...")
        return True
    
    def disconnect(self):
        self._log("Disconnected (mock)")
