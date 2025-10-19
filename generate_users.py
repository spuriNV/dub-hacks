#!/usr/bin/env python3
"""
Generate users and events for Statsig dashboard
"""

import time
from statsig_python_core import Statsig, StatsigUser, StatsigOptions

def generate_users():
    """Generate users and events for Statsig dashboard"""
    
    print("🚀 Generating users and events for Statsig...")
    
    try:
        # Initialize Statsig
        options = StatsigOptions()
        options.environment = "development"
        
        statsig = Statsig("secret-gfkbRyexczdpYgd52rFF6IEOB8VVTfBDVzW8SIMW0Zn", options)
        statsig.initialize().wait()
        print("✅ Statsig initialized!")
        
        # Generate users
        users = [
            "user_001", "user_002", "user_003", "user_004", "user_005",
            "user_006", "user_007", "user_008", "user_009", "user_010",
            "user_011", "user_012", "user_013", "user_014", "user_015",
            "user_016", "user_017", "user_018", "user_019", "user_020"
        ]
        
        print(f"📊 Generating data for {len(users)} users...")
        
        for i, user_id in enumerate(users):
            print(f"👤 Processing user {i+1}/{len(users)}: {user_id}")
            
            # Create user object
            user = StatsigUser(user_id=user_id)
            
            # Test experiment
            try:
                experiment = statsig.get_experiment(user, "wifi_assistant_model_test")
                model_name = experiment.get_string("model_name", "unknown")
                print(f"  🎯 Experiment: {model_name}")
            except Exception as e:
                print(f"  ❌ Experiment failed: {e}")
            
            # Log events
            try:
                statsig.log_event(user, "new_mau_28d")
                statsig.log_event(user, "monthly_stickiness")
                print(f"  📊 Logged events")
            except Exception as e:
                print(f"  ❌ Event logging failed: {e}")
            
            # Small delay
            time.sleep(0.3)
        
        # Shutdown to flush events
        statsig.shutdown().wait()
        print("🔄 All events flushed to Statsig!")
        
        print("\n🎉 User generation complete!")
        print("📊 Your Statsig dashboard should now show:")
        print(f"   - {len(users)} users")
        print("   - Events: new_mau_28d, monthly_stickiness")
        print("   - Experiment: wifi_assistant_model_test")
        
        print("\n🔍 Check your Statsig dashboard for:")
        print("   1. Events → new_mau_28d and monthly_stickiness")
        print("   2. Users → user_001 through user_020")
        print("   3. Analytics → Event counts and user activity")
        
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    generate_users()
