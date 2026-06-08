import pandas as pd

names = ['Ultimate Perks 12', 'Secure Savings 12', 'Free & Clear Nights 12', 'Summer Break 12', 'Texas Classic 12', 'Budget Relief 12', 'Texas Basics 12']
base_cost = [9.95, 0.0, 9.95, 9.95, 9.95, 9.95, 0.0] # dollars

usage500 = [22.2, 23.3, 22.0, 22.6, 22.5, 24.1, 22.3] # cents
usage1000 = [20.8, 19.9, 20.6, 21.2, 20.8, 17.7, 18.1] # cents
usage2000 = [20.1, 19.7, 19.9, 20.5, 20.1, 19.5, 19.8] # cents

raw_under_500 = [13.3, 16.4, 25.0, 16.4, 13.3, 15.2, 15.4] # cents
raw_under_1000 = [13.3, 16.4, 25.0, 16.4, 13.3, 15.2, 7.7] # cents
raw_over_1000 =  [13.3, 13.4, 25.0, 16.4, 13.3, 15.2, 15.4] # cents

df = pd.DataFrame({
    "Plan Name": names, 
    "Base Cost": base_cost, 
    "Avg 500kWh (¢)": usage500, 
    "Avg 1000kWh (¢)": usage1000, 
    "Avg 2000kWh (¢)": usage2000,
    "Raw Rate <=500kWh (¢)": raw_under_500,
    "Raw Rate <=1000kWh (¢)": raw_under_1000,
    "Raw Rate >1000kWh (¢)": raw_over_1000
})

usages = [919, 1138, 1260, 889, 622, 928, 673, 1282, 575, 484, 552, 919] # kWh, starting in July

def average_rates(row):
    total_annual_cost = 0
    for month_usage in usages:
        if month_usage <= 750:
            rate_cents = row["Avg 500kWh (¢)"]
        elif month_usage <= 1500:
            rate_cents = row["Avg 1000kWh (¢)"]
        else:
            rate_cents = row["Avg 2000kWh (¢)"]
            
        monthly_cost = (rate_cents / 100) * month_usage
        total_annual_cost += monthly_cost
        
    return total_annual_cost

def raw_estimate(row):
    total_annual_cost = 0
    for month_usage in usages:
        monthly_cost = row["Base Cost"]
        
        # Proper tier logic based on actual usage
        if month_usage <= 500:
            energy_cost = (row["Raw Rate <=500kWh (¢)"] / 100) * month_usage
            
        elif month_usage <= 1000:
            tier_1_cost = (row["Raw Rate <=500kWh (¢)"] / 100) * 500
            tier_2_cost = (row["Raw Rate <=1000kWh (¢)"] / 100) * (month_usage - 500)
            energy_cost = tier_1_cost + tier_2_cost
            
        else:
            tier_1_cost = (row["Raw Rate <=500kWh (¢)"] / 100) * 500
            tier_2_cost = (row["Raw Rate <=1000kWh (¢)"] / 100) * 500  # The next 500 kWh block
            tier_3_cost = (row["Raw Rate >1000kWh (¢)"] / 100) * (month_usage - 1000)
            energy_cost = tier_1_cost + tier_2_cost + tier_3_cost
                
        monthly_cost += energy_cost
        total_annual_cost += monthly_cost
        
    return total_annual_cost

df["Average Advertized Cost ($)"] = df.apply(average_rates, axis=1).round(2)
df["Raw Rates Estimate Cost ($)"] = df.apply(raw_estimate, axis=1).round(2)
df = df.sort_values(by="Raw Rates Estimate Cost ($)").reset_index(drop=True)

print(df)
