from delta_rest_client import DeltaRestClient, OrderType

# Initialize client
delta_client = DeltaRestClient(
    base_url='https://cdn-ind.testnet.deltaex.org',
    api_key='pLuQouWRUVq2Cx4DfxmgGWGfWo1pkX',
    api_secret='8f1zN8vzNTmQsrPH8KZuGqTc5vBhXTklz0VI03SADji0glzCWYe7HjgM74Yj'
)

PRODUCT_ID = 84   # Change if needed


# 🔹 Get current position
def get_position():
    try:
        positions = delta_client.get_positions()
        
        for pos in positions:
            if pos['product_id'] == PRODUCT_ID:
                size = float(pos['size'])
                
                if size > 0:
                    return "LONG"
                elif size < 0:
                    return "SHORT"
        
        return "NONE"
    
    except Exception as e:
        print("Error fetching position:", e)
        return "NONE"


# 🔹 Place order
def place_order(side):
    try:
        print(f"📤 Placing {side.upper()} order")

        order = delta_client.place_order(
            product_id=PRODUCT_ID,
            size=1,
            side=side,
            order_type=OrderType.MARKET,
        )

        print("✅ Order Response:", order)
        return order

    except Exception as e:
        print("❌ Order failed:", e)


# 🔹 Close existing position
def close_position(current_position):
    if current_position == "LONG":
        print("Closing LONG → SELL")
        place_order("sell")

    elif current_position == "SHORT":
        print("Closing SHORT → BUY")
        place_order("buy")


# 🔹 Main execution logic
def execute_trade(signal):
    """
    signal: "LONG" or "SHORT"
    """

    current_position = get_position()
    print("📊 Current Position:", current_position)

    # 🚀 LOGIC
    if signal == "LONG":
        if current_position == "LONG":
            print("Already in LONG → No action")

        elif current_position == "SHORT":
            close_position("SHORT")
            place_order("buy")

        else:
            place_order("buy")

    elif signal == "SHORT":
        if current_position == "SHORT":
            print("Already in SHORT → No action")

        elif current_position == "LONG":
            close_position("LONG")
            place_order("sell")

        else:
            place_order("sell")