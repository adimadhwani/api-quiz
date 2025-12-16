import requests
import time
import sys
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(number, description):
    """Print a formatted step"""
    print(f"\n{number}. {description}")
    print("-"*40)

def print_result(success, message, data=None):
    """Print test result"""
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    
    if data:
        # Clean up data for display
        if isinstance(data, dict):
            clean_data = {}
            for key, value in data.items():
                if isinstance(value, list):
                    clean_data[key] = value[:5]  # Show only first 5 items in lists
                elif isinstance(value, dict):
                    clean_data[key] = {k: v for k, v in list(value.items())[:3]}  # Show first 3 items
                else:
                    clean_data[key] = value
            print(f"   Data: {json.dumps(clean_data, indent=2)}")

def test_all_endpoints():
    """Test all endpoints in the specified sequence"""
    
    team_id = None
    team_name = "TestTeam"
    
    print_section("STRANGER THINGS API COMPREHENSIVE TEST")
    print("Testing all endpoints in sequence...")
    
    # ========== Step 1: Create Team ==========
    print_step("1", "POST /create_team - Create a new team")
    try:
        response = requests.post(
            f"{BASE_URL}/create_team",
            json={"team_name": team_name}
        )
        
        if response.status_code == 200:
            data = response.json()
            team_id = data.get("team_id")
            print_result(True, f"Team created successfully: {team_id}")
            print(f"   Team Name: {data.get('team_name')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Instructions: {data.get('instructions')}")
        else:
            print_result(False, f"Failed to create team: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception creating team: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 2: Eleven Looks Around ==========
    print_step("2", f"GET /{team_id}/eleven - Eleven looks around Hawkins Lab")
    try:
        response = requests.get(f"{BASE_URL}/{team_id}/eleven")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Eleven looked around successfully")
            print(f"   Location: {data.get('location')}")
            print(f"   Gate Status: {data.get('gate_status')}")
            print(f"   Items: {', '.join(data.get('items', []))}")
            print(f"   Note: {data.get('notes', [''])[0]}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 3: Mike Looks Around ==========
    print_step("3", f"GET /{team_id}/mike - Mike looks around Upside Down")
    try:
        response = requests.get(f"{BASE_URL}/{team_id}/mike")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Mike looked around successfully")
            print(f"   Location: {data.get('location')}")
            print(f"   Gate Status: {data.get('gate_status')}")
            print(f"   Items: {', '.join(data.get('items', []))}")
            print(f"   Note: {data.get('notes', [''])[0]}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 4: Send Demogorgon Tooth ==========
    print_step("4", f"POST /{team_id}/send_item - Mike sends demogorgon tooth to Eleven")
    try:
        response = requests.post(
            f"{BASE_URL}/{team_id}/send_item",
            json={"from_friend": "Mike", "item": "demogorgon tooth"}
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if success:
                print_result(True, data.get("message", "Item sent"))
                print(f"   Eleven's Items: {data.get('eleven_items', [])}")
                print(f"   Mike's Items: {data.get('mike_items', [])}")
                print(f"   Next Action: {data.get('next_action')}")
            else:
                print_result(False, data.get("message", "Failed to send item"))
                return False
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 5: Combine Radio and Tooth ==========
    print_step("5", f"PUT /{team_id}/use_item - Eleven combines radio and tooth")
    try:
        response = requests.put(
            f"{BASE_URL}/{team_id}/use_item",
            json={"friend": "Eleven", "action": "combine_radio_tooth"}
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if success:
                print_result(True, data.get("message", "Items combined"))
                print(f"   Sound Effect: {data.get('sound_effect')}")
                print(f"   Next Action: {data.get('next_action')}")
            else:
                print_result(False, data.get("message", "Failed to combine items"))
                return False
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 6: Scan for Frequency ==========
    print_step("6", f"PATCH /{team_id}/fix - Eleven scans for gate frequency")
    try:
        response = requests.patch(
            f"{BASE_URL}/{team_id}/fix",
            json={"friend": "Eleven", "action": "scan_frequency"}
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if success:
                print_result(True, data.get("message", "Frequency scanned"))
                print(f"   Code Revealed: {data.get('code_revealed')}")
                print(f"   Instructions: {data.get('instructions')}")
            else:
                print_result(False, data.get("message", "Failed to scan frequency"))
                return False
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 7: Activate Gate Panel ==========
    print_step("7", f"DELETE /{team_id}/remove - Mike activates gate control panel")
    try:
        response = requests.delete(
            f"{BASE_URL}/{team_id}/remove",
            json={"friend": "Mike", "code": "0110"}
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if success:
                print_result(True, data.get("message", "Gate panel activated"))
                print(f"   Instructions: {data.get('instructions')}")
            else:
                print_result(False, data.get("message", "Failed to activate gate panel"))
                return False
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 8: Check Dimension Sync ==========
    print_step("8", f"HEAD /{team_id}/status - Check dimension sync status")
    try:
        response = requests.head(f"{BASE_URL}/{team_id}/status")
        
        if response.status_code == 200:
            headers = response.headers
            print_result(True, "Status check successful")
            print(f"   Team Status: {headers.get('X-Team-Status', 'N/A')}")
            print(f"   Escaped: {headers.get('X-Escaped', 'N/A')}")
            print(f"   Eleven Ready: {headers.get('X-Eleven-Ready', 'N/A')}")
            print(f"   Mike Ready: {headers.get('X-Mike-Ready', 'N/A')}")
            print(f"   Dimension Sync: {headers.get('X-Dimension-Sync', 'N/A')}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 9: Check Escape Options ==========
    print_step("9", f"OPTIONS /{team_id}/escape - See escape requirements")
    try:
        response = requests.options(f"{BASE_URL}/{team_id}/escape")
        
        if response.status_code == 200:
            headers = response.headers
            print_result(True, "Escape options retrieved")
            print(f"   Allowed Methods: {headers.get('Allow', 'N/A')}")
            print(f"   Requirements: {headers.get('X-Escape-Requires', 'N/A')}")
            print(f"   Preconditions: {headers.get('X-Preconditions', 'N/A')}")
            print(f"   Warning: {headers.get('X-Warning', 'N/A')}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 10: Eleven Attempts Escape ==========
    print_step("10", f"POST /{team_id}/escape - Eleven attempts to escape")
    try:
        response = requests.post(
            f"{BASE_URL}/{team_id}/escape",
            json={"friend": "Eleven"}
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if success:
                print_result(True, data.get("message", "Eleven escaped"))
                print(f"   Escape Key: {data.get('escape_key')}")
            else:
                print_result(True, data.get("message", "Waiting for Mike"))
                print(f"   Attempts: {data.get('escape_attempts', 'N/A')}")
                print(f"   Time Window: {data.get('time_window', 'N/A')}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(2)  # Wait less than 10 seconds for coordination
    
    # ========== Step 11: Mike Attempts Escape ==========
    print_step("11", f"POST /{team_id}/escape - Mike attempts to escape (within 10s!)")
    try:
        response = requests.post(
            f"{BASE_URL}/{team_id}/escape",
            json={"friend": "Mike"}
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if success:
                print_result(True, "🎉 ESCAPE SUCCESSFUL! 🎉")
                print(f"   Message: {data.get('message')}")
                print(f"   Escape Key: {data.get('escape_key')}")
                print(f"   Time Taken: {data.get('time_taken')}")
                print(f"   Steps Used: {len(data.get('steps_used', []))} HTTP methods")
            else:
                print_result(False, data.get("message", "Escape failed"))
                return False
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Step 12: Get Escape Key ==========
    print_step("12", f"GET /{team_id}/key - Get escape key")
    try:
        response = requests.get(f"{BASE_URL}/{team_id}/key")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Escape key retrieved")
            print(f"   Team Name: {data.get('team_name')}")
            print(f"   Escape Key: {data.get('escape_key')}")
            print(f"   Time Taken: {data.get('time_taken')}")
            print(f"   Steps Completed: {data.get('steps_completed')}")
            print(f"   Story Ending: {data.get('story_ending', 'N/A')}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False
    
    time.sleep(0.5)
    
    # ========== Bonus: Test Hint System ==========
    print_step("Bonus", f"GET /{team_id}/hint - Get help when stuck")
    try:
        # Test hint for Eleven
        print("\n   Testing hint for Eleven...")
        response = requests.get(f"{BASE_URL}/{team_id}/hint?friend=Eleven")
        
        if response.status_code == 200:
            data = response.json()
            if "hint" in data:
                print_result(True, "Hint retrieved successfully")
                print(f"   Hint: {data.get('hint', 'N/A')[:100]}...")
                print(f"   Hints Used: {data.get('hints_used_total', 0)}")
            elif "warning" in data:
                print_result(True, "Hint system working (cooldown active)")
                print(f"   Warning: {data.get('warning')}")
                print(f"   Time Remaining: {data.get('time_remaining')}")
            else:
                print_result(True, "Hint endpoint responded")
                print(f"   Response: {data}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
    
    time.sleep(1)
    
    # Test hint for Mike (might be on cooldown)
    try:
        print("\n   Testing hint for Mike...")
        response = requests.get(f"{BASE_URL}/{team_id}/hint?friend=Mike")
        
        if response.status_code == 200:
            data = response.json()
            if "hint" in data:
                print_result(True, "Hint retrieved successfully")
                print(f"   Hint: {data.get('hint', 'N/A')[:100]}...")
            elif "warning" in data:
                print_result(True, "Hint system working (cooldown active)")
                print(f"   Warning: {data.get('warning')}")
            else:
                print_result(True, "Hint endpoint responded")
        else:
            print_result(False, f"Failed: {response.status_code}")
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
    
    time.sleep(1)
    
    # Test hint without friend parameter
    try:
        print("\n   Testing general hint...")
        response = requests.get(f"{BASE_URL}/{team_id}/hint")
        
        if response.status_code == 200:
            data = response.json()
            if "hint" in data:
                print_result(True, "General hint retrieved")
                print(f"   Hint: {data.get('hint', 'N/A')[:100]}...")
            elif "warning" in data:
                print_result(True, "Hint system working (cooldown active)")
                print(f"   Warning: {data.get('warning')}")
            else:
                print_result(True, "Hint endpoint responded")
        else:
            print_result(False, f"Failed: {response.status_code}")
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
    
    # ========== Bonus: Test Team Status ==========
    print_step("Bonus", f"GET /team_status/{team_id} - Check team status")
    try:
        response = requests.get(f"{BASE_URL}/team_status/{team_id}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Team status retrieved")
            print(f"   Team Name: {data.get('team_name')}")
            print(f"   Escaped: {data.get('escaped')}")
            print(f"   Time Elapsed: {data.get('time_elapsed')}")
            print(f"   Steps Completed: {len(data.get('steps_completed', []))}")
            print(f"   Escape Attempts: {data.get('escape_attempts', 0)}")
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
    
    # ========== Summary ==========
    print_section("TEST SUMMARY")
    print("✅ All 12 main endpoints tested successfully!")
    print(f"📋 Team ID: {team_id}")
    print(f"🏷️ Team Name: {team_name}")
    print("\n📊 HTTP Methods Tested:")
    print("   1. POST - Create team and send items")
    print("   2. GET - Look around and retrieve keys")
    print("   3. PUT - Combine items")
    print("   4. PATCH - Fix/scan for frequency")
    print("   5. DELETE - Remove obstacles")
    print("   6. HEAD - Quick status check")
    print("   7. OPTIONS - Discover methods")
    print("\n🎮 Game Flow Verified:")
    print("   ✓ Team creation")
    print("   ✓ Character coordination")
    print("   ✓ Item transfer")
    print("   ✓ Item combination")
    print("   ✓ Code discovery")
    print("   ✓ Gate activation")
    print("   ✓ Synchronized escape")
    print("   ✓ Key retrieval")
    
    return True

def main():
    """Main function"""
    try:
        # First, check if server is running
        print("🔍 Checking server connection...")
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Server is running!")
            else:
                print(f"❌ Server responded with status: {response.status_code}")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server!")
            print("   Make sure the FastAPI server is running with:")
            print("   uvicorn main:app --reload --port 8000")
            sys.exit(1)
        
        # Run the tests
        success = test_all_endpoints()
        
        if success:
            print_section("🎉 ALL TESTS PASSED! 🎉")
            print("The Stranger Things API is fully functional!")
            print("\n🔑 Key Learning Points:")
            print("   • Each HTTP method has a specific purpose")
            print("   • Coordination between characters is essential")
            print("   • Timing matters for synchronized actions")
            print("   • State is maintained server-side with team ID")
        else:
            print_section("❌ SOME TESTS FAILED")
            print("Check the error messages above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()