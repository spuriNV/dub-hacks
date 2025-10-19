#!/usr/bin/env python3
"""
Generate Statsig data directly without the server
"""

import time
from statsig import statsig

def generate_statsig_events():
    """Generate test events for Statsig dashboard"""
    
    # Initialize Statsig
    try:
        statsig.initialize("secret-gfkbRyexczdpYgd52rFF6IEOB8VVTfBDVzW8SIMW0Zn")
        print("✅ Statsig initialized successfully!")
    except Exception as e:
        print(f"❌ Statsig initialization failed: {e}")
        return
    
    # Test users and models
    test_data = [
        {"user_id": "user_001", "model": "Qwen/Qwen2-0.5B"},
        {"user_id": "user_002", "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"},
        {"user_id": "user_003", "model": "Qwen/Qwen2-0.5B"},
        {"user_id": "user_004", "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"},
        {"user_id": "user_005", "model": "Qwen/Qwen2-0.5B"},
        {"user_id": "user_006", "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"},
        {"user_id": "user_007", "model": "Qwen/Qwen2-0.5B"},
        {"user_id": "user_008", "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"},
        {"user_id": "user_009", "model": "Qwen/Qwen2-0.5B"},
        {"user_id": "user_010", "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"},
    ]
    
    print("🚀 Generating Statsig events...")
    
    for i, data in enumerate(test_data):
        user_id = data["user_id"]
        model = data["model"]
        
        # Create user object
        user = {"userID": user_id}
        
        try:
            # Log new_mau_28d event (simple event name only)
            statsig.log_event("new_mau_28d")
            print(f"📊 Logged new_mau_28d for {user_id} with {model}")
            
            # Log monthly_stickiness event (simple event name only)
            statsig.log_event("monthly_stickiness")
            print(f"📊 Logged monthly_stickiness for {user_id} with {model}")
            
            # Test experiment assignment
            experiment = statsig.get_experiment("wifi_assistant_model_test", user)
            assigned_model = experiment.get("model_name", "unknown")
            print(f"🎯 Experiment assigned {assigned_model} to {user_id}")
            
        except Exception as e:
            print(f"❌ Error for {user_id}: {e}")
        
        # Wait between events
        time.sleep(1)
    
    print("\n🎉 Statsig data generation complete!")
    print("📊 Check your Statsig dashboard for:")
    print("   - Events: new_mau_28d, monthly_stickiness")
    print("   - Experiment: wifi_assistant_model_test")
    print("   - Users: user_001 through user_010")
    print("   - Models: Qwen/Qwen2-0.5B vs TinyLlama/TinyLlama-1.1B-Chat-v1.0")

if __name__ == "__main__":
    generate_statsig_events()
