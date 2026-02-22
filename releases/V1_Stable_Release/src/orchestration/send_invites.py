import pandas as pd
import os

EMAIL_TEMPLATE = """Subject: Expert Review Invitation - Maternity User Research Protocol

Dear [Expert Name],

We are conducting a study on an AI-augmented qualitative interview protocol designed to uncover structural insights in the maternity healthcare journey. 

Given your highly relevant expertise in [insert specific field], we would be incredibly grateful if you could participate in our Expert Evaluation panel. The review requires evaluating 5 Likert-scale criteria via a brief Google Form.

Please let us know if you have availability in the coming weeks.

Best regards,
Synthetic Maternity Research Team"""

def main():
    csv_path = "data/raw/dummy_experts.csv"
    
    # Check if file exists relative to execution path
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw", "dummy_experts.csv")
        
    df = pd.read_csv(csv_path)
    
    print("-" * 60)
    for index, row in df.iterrows():
        name = str(row['Name'])
        field = str(row['Field'])
        
        # Replace the placeholders
        custom_email = EMAIL_TEMPLATE.replace("[Expert Name]", name).replace("[insert specific field]", field)
        
        print(custom_email)
        print("-" * 60)

if __name__ == "__main__":
    main()
