# 🏪 CAFE QUICK SETUP GUIDE

## How to Set Up Auto-Reply for Your Cafe (5 Minutes!)

---

## Step 1: Get the Files

```bash
git clone https://github.com/naitiknahariyaa-png/whatsapp-automation.git
cd whatsapp-automation
pip install -r requirements.txt
pip install pandas openpyxl
```

---

## Step 2: Edit Your Menu

Open `cafe_menu_template.csv` in Excel or Google Sheets:

```
Category,Item,Price,Keywords
Coffee,Espresso,99,espresso coffee shot
Coffee,Cappuccino,129,cappuccino coffee capp
...
```

**Fill in your:**
- ✅ Your cafe items
- ✅ Your prices
- ✅ Search keywords people might use

**Example:**
```
Category: Pizza
Item: Margherita Pizza
Price: 199
Keywords: pizza, margherita, veg pizza, cheese pizza
```

---

## Step 3: Setup Bot

```bash
# Run setup
python create_cafe_menu.py

# Select option 2 to convert your Excel/CSV menu

# Then select option 5 to import to bot database
```

---

## Step 4: Start Bot

```bash
python main.py
```

---

## How Auto-Reply Works:

```
Customer: "Hi"
Bot: "Hello! 👋 Welcome to [Your Cafe]!"

Customer: "What pizzas do you have?"
Bot: "🍕 Our Pizzas:
• Margherita - ₹199
• Farmhouse - ₹249
..."

Customer: "Price?"
Bot: "💰 Our prices are very affordable!
☕ Coffee: ₹99-179
🍕 Pizza: ₹199-499
..."
```

---

## Pre-Made Keywords (Just Work!)

These keywords work automatically:

| Keyword | Response |
|---------|----------|
| hi, hello | Welcome message |
| menu | Full menu summary |
| price, cost | Price list |
| pizza | Pizza menu |
| coffee | Coffee menu |
| burger | Burger menu |
| delivery | Delivery info |
| order | How to order |
| hours | Opening hours |
| address | Location |

---

## Custom Keywords

Add your own in the bot:
- Type [4] to add keywords
- Type [7] to see all keywords

---

## Tips for Success:

1. **Be specific:** "chicken burger" not just "burger"
2. **Add variations:** People type differently
   - "price", "cost", "how much", "₹"
3. **Keep responses short:** 1-2 lines max
4. **Add your info:** Address, phone, hours

---

## Support

Need help? Ask me! 😊
