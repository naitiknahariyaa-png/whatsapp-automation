"""
WhatsApp Web Client Module
Handles connection to WhatsApp Web and message operations
"""

import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType
except ImportError:
    ChromeDriverManager = None


class WhatsAppClient:
    """WhatsApp Web client using Selenium"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.driver = None
        self.wait = None
        self.is_connected = False
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # Run in headless mode for server deployments
        if self.config.get('headless', False):
            options.add_argument("--headless")
        
        try:
            if ChromeDriverManager:
                service = webdriver.chrome.service.Service(
                    ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
                )
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"Error setting up driver: {e}")
            self.driver = webdriver.Chrome(options=options)
        
        self.wait = WebDriverWait(self.driver, 30)
        
    def connect(self):
        """Connect to WhatsApp Web"""
        print("Setting up WhatsApp Web connection...")
        self.setup_driver()
        
        # Open WhatsApp Web
        self.driver.get("https://web.whatsapp.com")
        
        print("Please scan the QR code within 30 seconds...")
        print("(Or wait for automatic session restore)")
        
        try:
            # Wait for either QR code or chat interface
            # Check if already logged in
            self.wait.until(
                lambda d: d.find_elements(By.XPATH, '//div[@data-tab="6"]') or
                         d.find_elements(By.XPATH, '//div[@data-testid="chat-list"]')
            )
            
            # Try to find main chat list (indicates logged in)
            try:
                chat_list = self.driver.find_element(By.XPATH, '//div[@data-testid="chat-list"]')
                print("✅ Already logged in! Restoring session...")
                self.is_connected = True
            except:
                # QR code present - need to scan
                print("⏳ Waiting for QR scan...")
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]'))
                )
                self.is_connected = True
                
        except TimeoutException:
            print("⚠️ Timeout waiting for WhatsApp Web")
            return False
        
        print("✅ Connected to WhatsApp!")
        return True
    
    def get_new_messages(self):
        """Get new messages from all chats"""
        messages = []
        
        if not self.is_connected:
            return messages
        
        try:
            # Get all open chats
            chat_panels = self.driver.find_elements(By.XPATH, '//div[@data-testid="chat-list"]//div[@data-testid="chat-list-item"]')
            
            for chat in chat_panels[:5]:  # Check last 5 chats
                try:
                    # Click on chat to open it
                    chat.click()
                    time.sleep(1)
                    
                    # Get chat name
                    try:
                        name_elem = self.driver.find_element(By.XPATH, '//div[@data-testid="conversation-info-header"]//span[@data-testid="conversation-info-back-button"]/following-sibling::span')
                        sender = name_elem.text
                    except:
                        sender = "Unknown"
                    
                    # Get messages
                    msg_elements = self.driver.find_elements(
                        By.XPATH, 
                        '//div[@data-testid="msg-list"]//div[contains(@class, "message")]'
                    )
                    
                    if msg_elements:
                        last_msg = msg_elements[-1]
                        msg_text = last_msg.text
                        
                        if msg_text.strip():
                            messages.append({
                                'sender': sender,
                                'content': msg_text,
                                'timestamp': time.time()
                            })
                            
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error getting messages: {e}")
        
        return messages
    
    def get_unread_messages(self):
        """Get unread messages specifically"""
        messages = []
        
        try:
            # Find unread chats
            unread = self.driver.find_elements(By.XPATH, '//span[@data-testid="icon-unread-count"]')
            
            for _ in unread[:3]:  # Check first 3 unread
                try:
                    # Click on unread chat
                    unread[0].click()
                    time.sleep(1)
                    
                    # Get last message
                    msg_elements = self.driver.find_elements(
                        By.XPATH,
                        '//div[contains(@class, "message-in")]'
                    )
                    
                    if msg_elements:
                        last = msg_elements[-1]
                        messages.append({
                            'sender': 'Unknown',
                            'content': last.text,
                            'timestamp': time.time()
                        })
                        
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return messages
    
    def send_message(self, message, contact_name=None):
        """Send a message to a specific contact or current chat"""
        try:
            if contact_name:
                self.search_contact(contact_name)
            
            # Find message input box
            msg_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@data-testid="conversation-compose-box-input"]')
                )
            )
            
            # Clear and type message
            msg_box.clear()
            msg_box.send_keys(message)
            
            # Find and click send button
            send_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@data-testid="send"]')
                )
            )
            send_btn.click()
            
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error sending message: {e}")
            return False
    
    def search_contact(self, name):
        """Search for a contact by name"""
        try:
            # Click search icon or search box
            search_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@data-testid="chat-list-search"]//input')
                )
            )
            search_box.clear()
            search_box.send_keys(name)
            
            time.sleep(1)
            
            # Click on first result
            contact = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f'//span[@title="{name}"]')
                )
            )
            contact.click()
            
            return True
            
        except Exception as e:
            print(f"Error searching contact: {e}")
            return False
    
    def get_chat_messages(self, contact_name, limit=50):
        """Get messages from a specific chat"""
        messages = []
        
        try:
            # Search and open chat
            self.search_contact(contact_name)
            time.sleep(1)
            
            # Get all messages
            msg_elements = self.driver.find_elements(
                By.XPATH,
                '//div[contains(@class, "message-in")] | //div[contains(@class, "message-out")]'
            )
            
            for msg in msg_elements[-limit:]:
                messages.append(msg.text)
                
        except Exception as e:
            print(f"Error getting chat messages: {e}")
        
        return messages
    
    def reply_to_message(self, reply_text):
        """Reply to the currently selected message"""
        return self.send_message(reply_text)
    
    def close(self):
        """Close the WhatsApp session"""
        if self.driver:
            self.driver.quit()
            print("WhatsApp session closed")


# ──────────────────────────────────────────────
# Simple WhatsApp API (Alternative - via requests)
# ──────────────────────────────────────────────

class WhatsAppAPI:
    """
    Alternative WhatsApp API using unofficial endpoints
    WARNING: This uses unofficial methods and may violate WhatsApp ToS
    """
    
    def __init__(self, session_path=None):
        self.session_path = session_path or "data/whatsapp_session"
        self.session = None
        
    def connect(self):
        """Initialize session"""
        Path(self.session_path).parent.mkdir(parents=True, exist_ok=True)
        print(f"Session will be saved to: {self.session_path}")
        
    def send_message(self, phone, message):
        """Send message to phone number"""
        # This would require additional implementation
        # Using WhatsApp Business API or third-party services
        print(f"Sending to {phone}: {message}")
        
    def get_messages(self):
        """Get new messages"""
        return []
