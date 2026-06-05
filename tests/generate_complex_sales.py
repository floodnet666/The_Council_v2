import os
import random
from datetime import datetime, timedelta
import csv

def generate_complex_sales(num_rows=100000, output_path="datasets/vendas_complexas_100k.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    start_date = datetime(2023, 1, 1)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "id_pedido", "status_pedido", "order_date", "ship_date", "delivery_date", 
            "valor_bruto", "valor_desconto", "valor_frete"
        ])
        
        for i in range(1, num_rows + 1):
            # Order Date
            days_offset = random.randint(0, 730)
            order_date = start_date + timedelta(days=days_offset)
            
            # Status
            # 80% Delivered, 10% Shipped (in transit), 5% Processing, 5% Cancelled
            rand_val = random.random()
            if rand_val < 0.8:
                status = "Delivered"
            elif rand_val < 0.9:
                status = "Shipped"
            elif rand_val < 0.95:
                status = "Processing"
            else:
                status = "Cancelled"
                
            # Ship Date & Delivery Date logic
            ship_date = ""
            delivery_date = ""
            
            if status in ["Shipped", "Delivered"]:
                ship_delay = random.randint(1, 5)
                ship_dt = order_date + timedelta(days=ship_delay)
                ship_date = ship_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                if status == "Delivered":
                    delivery_delay = random.randint(2, 10)
                    delivery_dt = ship_dt + timedelta(days=delivery_delay)
                    delivery_date = delivery_dt.strftime("%Y-%m-%d %H:%M:%S")
                    
            if status == "Cancelled":
                # Maybe cancelled before shipping, maybe after. Assume before.
                ship_date = ""
                delivery_date = ""
                
            order_date_str = order_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Financials
            bruto = round(random.uniform(50.0, 5000.0), 2)
            desconto = round(bruto * random.uniform(0.0, 0.3), 2) # up to 30% discount
            frete = round(random.uniform(10.0, 150.0), 2)
            
            writer.writerow([
                f"ORD-{i:07d}", status, order_date_str, ship_date, delivery_date, 
                bruto, desconto, frete
            ])
            
    print(f"Generated {num_rows} complex rows at {output_path}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "datasets/vendas_complexas_100k.csv")
    generate_complex_sales(output_path=out_path)
