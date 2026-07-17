"""
====================================================================
WHATSAPP CLIENT v2.0 - WhatsApp Web Automation (FIXED)
====================================================================

Advanced features:
- Robust error handling
- Multiple fallback selectors
- Better session management
- Auto-recovery from crashes
- Group chat filtering
- Message deduplication

Author: Built for Indian Businesses 🇮🇳
====================================================================
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from typing import Optional, Callable, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import selenium
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
    SELENIUM_AVAILABLE = True
except ImportError:
    pass


# WhatsApp Selectors - Multiple strategies for reliability
CHAT_LIST_SELECTORS = [
    '//div[@data-testid="chat-list-item"]',
    '//div[contains(@class,"chat-list")]//div[@tabindex]',
    '//div[@id="pane-side"]//div[@role="row"]',
]

CHAT_TITLE_SELECTORS = [
    './/span[@data-testid="conversation-info-header-title"]',
    './/span[contains(@class,"chat-title")]',
    './/div[@role="button"]//span[@title]',
]

UNREAD_SELECTORS = [
    './/span[@data-testid="icon-unread-read"]',
    './/div[contains(@class,"unread")]',
]

MESSAGE_SELECTORS = [
    '//div[@data-testid="msg-list"]//div[contains(@class,"message-in")]//div[@data-testid="message-bubble"]',
    '//div[contains(@class,"message-in")]//div[@data-testid="bubble"]',
    '//div[contains(@class,"copyable-text")]',
]

INPUT_BOX_SELECTORS = [
    '//div[@data-testid="conversation-compose-box-input"]',
    '//div[@contenteditable="true"][@data-tab="10"]',
    '//footer//div[@contenteditable="true"]',
]

SEND_BTN_SELECTORS = [
    '//button[@data-testid="send"]',
    '//span[@data-testid="send"]/ancestor::button',
    '//div[@data-testid="send"]',
]

BACK_BTN_SELECTORS = [
    '//div[@data-testid="btn-back"]',
    '//div[@aria-label="Back"]',
]

GROUP_ICON_SELECTORS = [
    './/div[@data-testid="group-icon"]',
    './/div[contains(@class,"group")]',
]


class WhatsAppClient:
    """WhatsApp Web Client v2.0 - Fixed and Advanced"""
    
    BASE_URL = "https://web.whatsapp.com"
    
    def __init__(self, session_dir: str = "data/session", headless: bool = False, verbose: bool = True):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.verbose = verbose
        
        self.driver = None
        self.is_connected = False
        self._message_callback: Optional[Callable] = None
        self._running = False
        self._processed_messages: set = set()
        
        logger.info(f"WhatsApp Client v2.0 initialized")
    
    def _log(self, message: str):
        """Print log message"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📱 {message}")
    
    def _find_element(self, selectors: List[str], parent=None, timeout: int = 5):
        """Find element using multiple selectors"""
        elem = parent or self.driver
        for selector in selectors:
            try:
                found = elem.find_element(By.XPATH, selector)
                if found:
                    return found
            except:
                continue
        return None
    
    def _find_elements(self, selectors: List[str], parent=None):
        """Find elements using multiple selectors"""
        elem = parent or self.driver
        for selector in selectors:
            try:
                found = elem.find_elements(By.XPATH, selector)
                if found:
                    return found
            except:
                continue
        return []
    
    def _setup_driver(self):
        """Setup Chrome driver"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("❌ Selenium not installed! Run: pip install selenium webdriver-manager")
        
        options = Options()
        options.add_argument("--user-data-dir=./data/chrome-profile")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--use-fake-device-for-media-stream")
        
        if self.headless:
            options.add_argument("--headless=new")
        
        driver = None
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            self._log("✅ Chrome driver loaded")
        except:
            try:
                driver = webdriver.Chrome(options=options)
                self._log("✅ Chrome driver loaded directly")
            except Exception as e:
                raise RuntimeError(f"❌ Failed to load Chrome: {e}")
        
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        return driver
    
    def connect(self) -> bool:
        """Connect to WhatsApp Web"""
        self._log("🔄 Connecting to WhatsApp Web...")
        
        try:
            self.driver = self._setup_driver()
            self._log("🌐 Opening WhatsApp Web...")
            self.driver.get(self.BASE_URL)
            time.sleep(3)
            
            # Check if already logged in
            chat_list = self._find_element(CHAT_LIST_SELECTORS, timeout=3)
            
            if chat_list:
                self._log("✅ Already logged in!")
            else:
                self._log("⚠️ Please scan QR code...")
                if not self._scan_qr():
                    return False
            
            if not self._wait_for_load():
                return False
            
            self.is_connected = True
            self._log("✅ Connected to WhatsApp!")
            self._save_session()
            return True
            
        except Exception as e:
            self._log(f"❌ Connection failed: {e}")
            self.is_connected = False
            return False
    
    def _scan_qr(self) -> bool:
        """Scan QR code"""
        max_wait = 180
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                qr = self._find_element(['//div[@data-ref][@role="img"]', '//canvas', '//img[@alt="Scan me!"]'], timeout=2)
                
                if qr:
                    self._log("📱 QR Code displayed - Scan now!")
                    time.sleep(20)
                    
                    chat_list = self._find_element(CHAT_LIST_SELECTORS, timeout=2)
                    if chat_list:
                        self._log("✅ QR Scanned!")
                        return True
                else:
                    chat_list = self._find_element(CHAT_LIST_SELECTORS, timeout=2)
                    if chat_list:
                        self._log("✅ Already logged in!")
                        return True
                    
                    self._log("⏳ Waiting for QR...")
                    time.sleep(2)
            except:
                pass
        
        self._log("❌ QR scan timeout")
        return False
    
    def _wait_for_load(self) -> bool:
        """Wait for WhatsApp to load"""
        for attempt in range(10):
            chat_list = self._find_element(CHAT_LIST_SELECTORS, timeout=5)
            if chat_list:
                self._log("✅ WhatsApp loaded!")
                time.sleep(2)
                return True
            
            self._log(f"⏳ Loading... ({attempt+1}/10)")
            time.sleep(2)
        
        self._log("❌ WhatsApp failed to load")
        return False
    
    def _save_session(self):
        """Save session cookies"""
        try:
            if self.driver:
                cookies = self.driver.get_cookies()
                session_file = self.session_dir / "session.json"
                with open(session_file, 'w') as f:
                    json.dump(cookies, f)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def _load_session(self) -> bool:
        """Load session from cookies"""
        try:
            session_file = self.session_dir / "session.json"
            if not session_file.exists():
                return False
            
            self.driver.get(self.BASE_URL)
            time.sleep(2)
            
            with open(session_file, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass
            
            self.driver.refresh()
            time.sleep(3)
            return True
        except:
            return False
    
    def _is_group_chat(self, chat_elem) -> bool:
        """Check if chat is a group"""
        for selector in GROUP_ICON_SELECTORS:
            try:
                chat_elem.find_element(By.XPATH, selector)
                return True
            except:
                continue
        return False
    
    def _go_back_to_chat_list(self):
        """Navigate back to chat list"""
        try:
            back_btn = self._find_element(BACK_BTN_SELECTORS, timeout=2)
            if back_btn:
                back_btn.click()
                time.sleep(1)
                return True
        except:
            pass
        
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)
            return True
        except:
            pass
        
        try:
            self.driver.get(self.BASE_URL)
            time.sleep(2)
            return True
        except:
            pass
        
        return False
    
    def _get_last_message(self) -> Optional[str]:
        """Get last received message"""
        messages = self._find_elements(MESSAGE_SELECTORS)
        
        if not messages:
            return None
        
        for msg in reversed(messages[-10:]):
            try:
                msg_text = msg.text.strip()
                if msg_text and len(msg_text) > 0:
                    parent = msg.find_element(By.XPATH, "..")
                    parent_class = parent.get_attribute("class") or ""
                    if "outgoing" not in parent_class.lower():
                        return msg_text
            except:
                continue
        
        return None
    
    def _send_message(self, message: str) -> bool:
        """Send message"""
        try:
            input_box = self._find_element(INPUT_BOX_SELECTORS)
            
            if not input_box:
                self._log("❌ Input box not found")
                return False
            
            input_box.click()
            input_box.clear()
            time.sleep(0.3)
            input_box.send_keys(message)
            time.sleep(0.5)
            
            send_btn = self._find_element(SEND_BTN_SELECTORS)
            
            if send_btn:
                send_btn.click()
            else:
                input_box.send_keys(Keys.RETURN)
            
            time.sleep(1)
            self._log(f"✅ Sent: {message[:50]}...")
            return True
                
        except Exception as e:
            self._log(f"❌ Send failed: {e}")
            return False
    
    def _get_sender_name(self) -> str:
        """Get current chat sender name"""
        selectors = [
            '//div[@data-testid="conversation-info-header"]//span[@title]',
            '//div[@data-testid="conversation-info-header-title"]',
            '//span[@class="chat-title"]',
        ]
        
        for selector in selectors:
            try:
                elem = self.driver.find_element(By.XPATH, selector)
                if elem:
                    name = elem.get_attribute("title") or elem.text
                    if name:
                        return name.strip()
            except:
                continue
        
        return "Unknown"
    
    def start_monitoring(self, callback: Callable[[str, str], str]):
        """Start monitoring ALL chats for auto-replies"""
        if not self.is_connected:
            self._log("❌ Not connected")
            return
        
        self._message_callback = callback
        self._running = True
        self._processed_messages.clear()
        self._log("🚀 STARTED: Monitoring all chats...")
        self._log("💡 Skipping groups, monitoring personal chats")
        
        consecutive_errors = 0
        max_errors = 5
        
        while self._running:
            try:
                self._go_back_to_chat_list()
                time.sleep(1)
                
                chats = self._find_elements(CHAT_LIST_SELECTORS)
                
                if not chats:
                    time.sleep(5)
                    consecutive_errors += 1
                    continue
                
                self._log(f"📋 Scanning {len(chats)} chats...")
                consecutive_errors = 0
                processed = 0
                
                for i, chat in enumerate(chats):
                    if not self._running:
                        break
                    
                    try:
                        try:
                            _ = chat.is_displayed()
                        except StaleElementReferenceException:
                            continue
                        
                        # Get chat title
                        chat_title = None
                        for selector in CHAT_TITLE_SELECTORS:
                            try:
                                title_elem = chat.find_element(By.XPATH, selector)
                                if title_elem:
                                    chat_title = title_elem.text.strip()
                                    break
                            except:
                                continue
                        
                        if not chat_title:
                            continue
                        
                        # Skip groups
                        if self._is_group_chat(chat):
                            continue
                        
                        # Check unread
                        unread = None
                        for selector in UNREAD_SELECTORS:
                            try:
                                unread = chat.find_element(By.XPATH, selector)
                                if unread:
                                    break
                            except:
                                continue
                        
                        if not unread:
                            continue
                        
                        chat_key = f"{chat_title}_{i}"
                        if chat_key in self._processed_messages:
                            continue
                        
                        self._log(f"📩 Unread: {chat_title}")
                        
                        try:
                            chat.click()
                            time.sleep(2)
                        except:
                            continue
                        
                        sender = self._get_sender_name()
                        last_msg = self._get_last_message()
                        
                        if last_msg and last_msg not in self._processed_messages:
                            self._log(f"💬 {sender}: {last_msg[:50]}...")
                            
                            if self._message_callback:
                                response = self._message_callback(sender, last_msg)
                                if response:
                                    if self._send_message(response):
                                        processed += 1
                            
                            self._processed_messages.add(last_msg)
                        
                        self._processed_messages.add(chat_key)
                        time.sleep(0.5)
                        self._go_back_to_chat_list()
                        time.sleep(0.5)
                        
                    except StaleElementReferenceException:
                        continue
                    except Exception as e:
                        continue
                
                if processed > 0:
                    self._log(f"✅ Processed {processed} messages")
                
                if len(self._processed_messages) > 1000:
                    self._processed_messages = set(list(self._processed_messages)[-500:])
                
                time.sleep(3)
                
            except Exception as e:
                consecutive_errors += 1
                self._log(f"❌ Error: {e} ({consecutive_errors}/{max_errors})")
                
                if consecutive_errors >= max_errors:
                    self._log("🔄 Recovering...")
                    try:
                        self.driver.get(self.BASE_URL)
                        time.sleep(5)
                        consecutive_errors = 0
                    except:
                        pass
                
                time.sleep(5)
        
        self._log("🛑 Stopped monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._running = False
        self._log("🛑 Stopping...")
    
    def disconnect(self):
        """Disconnect from WhatsApp"""
        self._running = False
        self._save_session()
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.is_connected = False
        self._log("👋 Disconnected")
    
    def get_qr_code(self) -> Optional[str]:
        """Get QR code as base64"""
        if not self.driver:
            return None
        
        try:
            qr = self.driver.find_element(By.XPATH, '//div[@data-ref][@role="img"]')
            return qr.screenshot_as_base64
        except:
            return None


# WhatsApp Cloud API Client
class WhatsAppCloudAPI:
    """WhatsApp Business Cloud API"""
    
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
                "text": {"preview_url": False, "body": message}
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Failed to send: {e}")
            return False


# Mock Client for Testing
class MockWhatsAppClient:
    """Mock client for testing"""
    
    def __init__(self):
        self.is_connected = True
        self.messages_sent = []
    
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
