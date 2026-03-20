import json
import os
import datetime

class InterviewLogger:
    def __init__(self):
        self.interactions = []
        self.pricing_file = "data/config/model_pricing.json"
        self._check_and_update_pricing()
        
        # Load pricing from the config file
        with open(self.pricing_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.pricing = data.get("prices", {})

    def _get_most_recent_sunday_0001(self):
        now = datetime.datetime.now()
        # weekday() returns 0 for Monday, 6 for Sunday
        days_since_sunday = (now.weekday() + 1) % 7
        last_sunday = now - datetime.timedelta(days=days_since_sunday)
        most_recent_sunday_0001 = last_sunday.replace(hour=0, minute=1, second=0, microsecond=0)
        return most_recent_sunday_0001

    def _check_and_update_pricing(self):
        needs_update = True
        most_recent_sunday_0001 = self._get_most_recent_sunday_0001()
        
        if os.path.exists(self.pricing_file):
            try:
                with open(self.pricing_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                last_updated_str = data.get("last_updated")
                if last_updated_str:
                    last_updated = datetime.datetime.fromisoformat(last_updated_str)
                    if last_updated > most_recent_sunday_0001:
                        needs_update = False
            except Exception as e:
                print(f"[Logger] Error reading pricing file: {e}")
                
        if needs_update:
            print("[Logger] Pricing data is missing or outdated. Generating new pricing file...")
            self._update_pricing_data()
            
    def _update_pricing_data(self):
        os.makedirs(os.path.dirname(self.pricing_file), exist_ok=True)
        
        # Hardcoded pricing as requested, ready to be wired to an API later
        pricing_data = {
            "last_updated": datetime.datetime.now().isoformat(),
            "prices": {
                "gpt-5.2": {"input": 0.0025, "output": 0.010},
                "gpt-4o": {"input": 0.0025, "output": 0.010},
                "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},
                "gemini-3.0-pro": {"input": 0.00125, "output": 0.00375},
                "gemini-1.5-pro": {"input": 0.00125, "output": 0.00375},
                "grok-2": {"input": 0.002, "output": 0.010}
            }
        }
        
        with open(self.pricing_file, "w", encoding="utf-8") as f:
            json.dump(pricing_data, f, indent=4)
        print(f"[Logger] Saved updated pricing to {self.pricing_file}")

    def estimate_cost(self, model_name, input_tokens, output_tokens):
        # Fallback to standard OpenAI pricing if model not found
        rates = self.pricing.get(model_name, {"input": 0.0025, "output": 0.010})
        cost = (input_tokens / 1000.0) * rates["input"] + (output_tokens / 1000.0) * rates["output"]
        return round(cost, 6)

    def log_interaction(self, provider, model_name, exact_prompt, exact_reply, input_tokens, output_tokens):
        total_tokens = input_tokens + output_tokens
        cost = self.estimate_cost(model_name, input_tokens, output_tokens)
        
        self.interactions.append({
            "provider": provider,
            "model_name": model_name,
            # stringifying prompt list if necessary to ensure clean json logging
            "exact_prompt": json.dumps(exact_prompt) if not isinstance(exact_prompt, str) else exact_prompt,
            "exact_reply": exact_reply,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": cost,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def save_logs(self):
        os.makedirs("data/logs", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        json_path = os.path.join("data/logs", f"detailed_log_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.interactions, f, indent=4)
            
        total_input = sum(i["input_tokens"] for i in self.interactions)
        total_output = sum(i["output_tokens"] for i in self.interactions)
        total_tokens = sum(i["total_tokens"] for i in self.interactions)
        total_cost = sum(i["estimated_cost_usd"] for i in self.interactions)
        
        models_used = set(i["model_name"] for i in self.interactions)
        
        summary_path = os.path.join("data/logs", f"summary_report_{timestamp}.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("--- Run Summary Report ---\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Total Input Tokens: {total_input}\n")
            f.write(f"Total Output Tokens: {total_output}\n")
            f.write(f"Total Tokens: {total_tokens}\n")
            f.write(f"Total Estimated Cost: ${total_cost:.6f}\n")
            f.write(f"Models Used: {', '.join(models_used)}\n")
            f.write(f"Total Interactions Logged: {len(self.interactions)}\n")
            
        print(f"\n[Logger] Saved detailed JSON log to: {json_path}")
        print(f"[Logger] Saved summary report to: {summary_path}")
        return json_path, summary_path
