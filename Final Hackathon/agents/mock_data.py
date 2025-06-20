import json
import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_mock_budget_excel():
    """Generate mock budget Excel file"""
    budget_data = {
        'Department': ['IT', 'IT', 'IT', 'Marketing', 'Marketing', 'Operations', 'Operations', 'HR', 'HR'],
        'Category': ['Software', 'Hardware', 'Cloud Services', 'Advertising', 'Events', 'Supplies', 'Equipment', 'Training', 'Recruitment'],
        'Monthly_Limit': [20000, 15000, 12000, 25000, 10000, 8000, 20000, 5000, 8000],
        'Annual_Limit': [240000, 180000, 144000, 300000, 120000, 96000, 240000, 60000, 96000],
        'Primary_Vendors': ['Microsoft,AWS,Adobe', 'Dell,HP,Lenovo', 'AWS,Google Cloud,Azure', 'Google Ads,Facebook', 'Event Corp,Catering Plus', 'Office Depot,Staples', 'Industrial Supply Co', 'Training Corp', 'Recruitment Agency']
    }
    
    df = pd.DataFrame(budget_data)
    os.makedirs('data/uploads', exist_ok=True)
    df.to_excel('data/uploads/sample_budget.xlsx', index=False)
    print("✅ Generated sample_budget.xlsx")
    return df

def generate_mock_budget_json():
    """Generate structured budget JSON"""
    budget_structure = {
        "departments": {
            "IT": {
                "total_budget": 50000,
                "categories": {
                    "Software": {"limit": 20000, "period": "monthly"},
                    "Hardware": {"limit": 15000, "period": "monthly"},
                    "Cloud Services": {"limit": 12000, "period": "monthly"},
                    "vendors": ["Microsoft", "AWS", "Adobe", "Dell", "HP"]
                }
            },
            "Marketing": {
                "total_budget": 35000,
                "categories": {
                    "Advertising": {"limit": 25000, "period": "monthly"},
                    "Events": {"limit": 10000, "period": "monthly"},
                    "vendors": ["Google Ads", "Facebook", "Event Corp"]
                }
            },
            "Operations": {
                "total_budget": 28000,
                "categories": {
                    "Supplies": {"limit": 8000, "period": "monthly"},
                    "Equipment": {"limit": 20000, "period": "monthly"},
                    "vendors": ["Office Depot", "Industrial Supply Co"]
                }
            },
            "HR": {
                "total_budget": 13000,
                "categories": {
                    "Training": {"limit": 5000, "period": "monthly"},
                    "Recruitment": {"limit": 8000, "period": "monthly"},
                    "vendors": ["Training Corp", "Recruitment Agency"]
                }
            }
        }
    }
    
    os.makedirs('data/uploads', exist_ok=True)
    with open('data/uploads/structured_budget.json', 'w') as f:
        json.dump(budget_structure, f, indent=2)
    
    print("✅ Generated structured_budget.json")
    return budget_structure

def generate_mock_transactions():
    """Generate mock transaction data that will trigger breaches"""
    departments = ["IT", "Marketing", "Operations", "HR"]
    categories = {
        "IT": ["Software", "Hardware", "Cloud Services"],
        "Marketing": ["Advertising", "Events"],
        "Operations": ["Supplies", "Equipment"],
        "HR": ["Training", "Recruitment"]
    }
    
    vendors = {
        "IT": ["Microsoft", "AWS", "Adobe", "Dell", "HP", "Google Cloud"],
        "Marketing": ["Google Ads", "Facebook", "Event Corp", "LinkedIn Ads"],
        "Operations": ["Office Depot", "Industrial Supply Co", "Staples"],
        "HR": ["Training Corp", "Recruitment Agency", "Learning Platform"]
    }
    
    transactions = []
    
    # Generate normal transactions
    for i in range(50):
        dept = random.choice(departments)
        category = random.choice(categories[dept])
        vendor = random.choice(vendors[dept])
        
        # Base amounts that should be safe
        base_amounts = {
            "Software": random.uniform(500, 2000),
            "Hardware": random.uniform(300, 1500),
            "Cloud Services": random.uniform(200, 1000),
            "Advertising": random.uniform(1000, 3000),
            "Events": random.uniform(800, 2000),
            "Supplies": random.uniform(100, 500),
            "Equipment": random.uniform(1000, 3000),
            "Training": random.uniform(200, 800),
            "Recruitment": random.uniform(500, 1500)
        }
        
        transaction = {
            "amount": round(base_amounts[category], 2),
            "department": dept,
            "category": category,
            "vendor": vendor,
            "description": f"{category} purchase from {vendor}",
            "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }
        
        transactions.append(transaction)
    
    # Generate transactions that will cause breaches
    breach_transactions = [
        {
            "amount": 15000,  # This will push IT Software over limit
            "department": "IT",
            "category": "Software",
            "vendor": "Microsoft",
            "description": "Enterprise software license renewal",
            "timestamp": datetime.now().isoformat()
        },
        {
            "amount": 12000,  # This will push Marketing Advertising over limit
            "department": "Marketing", 
            "category": "Advertising",
            "vendor": "Google Ads",
            "description": "Q4 advertising campaign",
            "timestamp": datetime.now().isoformat()
        },
        {
            "amount": 8000,  # This will push Operations Equipment close to limit
            "department": "Operations",
            "category": "Equipment", 
            "vendor": "Industrial Supply Co",
            "description": "Heavy equipment purchase",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    transactions.extend(breach_transactions)
    
    # Save to file
    os.makedirs('data/uploads', exist_ok=True)
    with open('data/uploads/mock_transactions.json', 'w') as f:
        json.dump(transactions, f, indent=2)
    
    print(f"✅ Generated {len(transactions)} mock transactions (including {len(breach_transactions)} breach triggers)")
    return transactions

def generate_all_mock_data():
    """Generate all mock data files"""
    print("🎲 Generating mock data for Smart Budget Enforcer...")
    
    budget_excel = generate_mock_budget_excel()
    budget_json = generate_mock_budget_json()
    transactions = generate_mock_transactions()
    
    print("\n📁 Generated files:")
    print("   - data/uploads/sample_budget.xlsx")
    print("   - data/uploads/structured_budget.json") 
    print("   - data/uploads/mock_transactions.json")
    
    print("\n💡 Usage instructions:")
    print("   1. Upload sample_budget.xlsx via /upload-budget endpoint")
    print("   2. Send transactions from mock_transactions.json via /track-expense")
    print("   3. The system will automatically detect breaches and generate recommendations")
    
    return {
        "budget_excel": budget_excel,
        "budget_json": budget_json,
        "transactions": transactions
    }

if __name__ == "__main__":
    generate_all_mock_data()