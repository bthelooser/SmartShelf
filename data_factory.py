import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_dummy_data():
    os.makedirs('data', exist_ok=True)
    skus = [f"SKU_{i:03d}" for i in range(1, 21)]
    categories = ['Beverages', 'Snacks', 'Dairy', 'Frozen', 'Produce']
    
    # 1. Product Velocity & Restock Efficiency Data
    velocity_rows = []
    for _ in range(200):
        sku = np.random.choice(skus)
        alert_time = datetime.now() - timedelta(days=np.random.randint(0, 7), hours=np.random.randint(0, 24))
        # Wait time between 5 mins and 120 mins
        wait_time = np.random.randint(5, 120)
        refill_time = alert_time + timedelta(minutes=wait_time)
        velocity_rows.append({
            'sku': sku,
            'category': np.random.choice(categories),
            'alert_timestamp': alert_time,
            'refill_timestamp': refill_time,
            'wait_time_mins': wait_time,
            'units_refilled': np.random.randint(10, 50)
        })
    pd.DataFrame(velocity_rows).to_csv('data/product_velocity.csv', index=False)

    # 2. Lost Revenue Data
    revenue_rows = []
    for sku in skus:
        oos_duration = np.random.uniform(1.0, 8.0) # hours
        avg_velocity = np.random.uniform(5.0, 15.0) # units/hour
        unit_price = np.random.uniform(2.5, 25.0)
        revenue_rows.append({
            'sku': sku,
            'oos_duration_hours': round(oos_duration, 2),
            'potential_revenue_lost': round(oos_duration * avg_velocity * unit_price, 2)
        })
    pd.DataFrame(revenue_rows).to_csv('data/lost_revenue.csv', index=False)

    # 3. Planogram Compliance Data (Shelf Coordinates)
    compliance_rows = []
    for shelf in ['A1-B1', 'A1-B2', 'A2-B1', 'A2-B2']:
        for slot in range(1, 11):
            is_compliant = np.random.choice([True, False], p=[0.85, 0.15])
            compliance_rows.append({
                'shelf_id': shelf,
                'slot_id': slot,
                'is_compliant': int(is_compliant),
                'error_type': 'None' if is_compliant else np.random.choice(['Misplaced', 'Empty', 'Wrong Label']),
                'x_coord': slot, # Simple grid
                'y_coord': int(shelf[-1])
            })
    pd.DataFrame(compliance_rows).to_csv('data/planogram_compliance.csv', index=False)
    print("Dummy data generated successfully in /data folder.")

if __name__ == "__main__":
    generate_dummy_data()