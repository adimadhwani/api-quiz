from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Stranger Things: Escape the Upside Down", 
              description="Multi-dimensional coordination puzzle")

# ADD THESE LINES ↓↓↓
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- In-Memory Storage ---
teams: Dict[str, dict] = {}
hint_requests: Dict[str, List[dict]] = {}

# Stranger Things themed items
DEFAULT_ITEMS = {
    "Eleven": ["radio", "note: 'need demogorgon frequency'"],
    "Mike": ["demogorgon tooth", "broken walkie-talkie"]
}

# --- Data Models ---
class TeamCreate(BaseModel):
    team_name: str

class SendItem(BaseModel):
    from_friend: str
    item: str

class UseItem(BaseModel):
    friend: str
    action: str

class FixAction(BaseModel):
    friend: str
    action: str

class RemoveAction(BaseModel):
    friend: str
    code: str

class EscapeAttempt(BaseModel):
    friend: str

class HintRequest(BaseModel):
    friend: str
    problem: str

# --- API Endpoints ---

@app.post("/create_team")
async def create_new_team(team: TeamCreate):
    """Create a new team - Stranger Things Edition"""
    
    # Normalize the incoming name (lowercase and remove spaces)
    incoming_name_clean = team.team_name.lower().strip()

    # --- CHANGE START: Check if team name already exists (Case Insensitive) ---
    for existing_id, existing_data in teams.items():
        # Compare the lowercase version of the stored name vs incoming name
        if existing_data['team_name'].lower().strip() == incoming_name_clean:
            return {
                "team_id": existing_id,
                "team_name": existing_data['team_name'], # Return original name
                "message": f"Team '{team.team_name}' found (matches '{existing_data['team_name']}'). Returning existing ID.",
                "instructions": f"Share this team_id with both friends: {existing_id}",
                "story": "Welcome back. The gate is still waiting...",
                "hint_system": "Use GET /{team_id}/hint when stuck. But use wisely!"
            }
    # --- CHANGE END ---

    team_id = str(uuid.uuid4())[:8]
    current_time = time.time()
    
    teams[team_id] = {
        'team_id': team_id,
        'team_name': team.team_name, # Store the name exactly as they typed it the first time
        'escaped': False,
        'escape_key': None,
        'start_time': current_time,
        'end_time': None,
        'eleven': {
            'location': 'Hawkins Lab (Real World)',
            'items': DEFAULT_ITEMS["Eleven"].copy(),
            'gate_locked': True,
            'has_frequency': False,
            'has_eggs': False,
            'last_action': None,
            'hints_used': 0
        },
        'mike': {
            'location': 'Upside Down Hawkins Lab',
            'items': DEFAULT_ITEMS["Mike"].copy(),
            'gate_locked': True,
            'has_frequency': False,
            'has_eggs': False,
            'last_action': None,
            'hints_used': 0
        },
        'steps_completed': [],
        'escape_attempts': [],
        'last_hint_time': None
    }
    
    hint_requests[team_id] = []
    
    return {
        "team_id": team_id,
        "team_name": team.team_name,
        "message": f"Team '{team.team_name}' created!",
        "instructions": f"Share this team_id with both friends: {team_id}",
        "story": "You are Eleven (Real World) and Mike (Upside Down). Work together to escape!",
        "hint_system": "Use GET /{team_id}/hint when stuck. But use wisely!"
    }

@app.get("/team_status/{team_id}")
async def get_team_status(team_id: str):
    """Check team progress"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    elapsed = int(time.time() - team['start_time'])
    
    return {
        "team_name": team['team_name'],
        "escaped": team['escaped'],
        "time_elapsed": f"{elapsed}s",
        "eleven_items": team['eleven']['items'],
        "mike_items": team['mike']['items'],
        "eleven_has_frequency": team['eleven']['has_frequency'],
        "mike_has_eggs": team['mike']['has_eggs'],
        "steps_completed": team['steps_completed'],
        "escape_attempts": len(team['escape_attempts']),
        "hints_used": team['eleven']['hints_used'] + team['mike']['hints_used']
    }

# GET - Look around
@app.get("/{team_id}/eleven")
async def eleven_look(team_id: str):
    """Eleven: Look around Hawkins Lab (Real World)"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "GET_ELEVEN" not in team['steps_completed']:
        team['steps_completed'].append("GET_ELEVEN")
    
    return {
        "location": team['eleven']['location'],
        "gate_status": "🔒 LOCKED" if team['eleven']['gate_locked'] else "🔓 UNLOCKED",
        "items": team['eleven']['items'],
        "notes": [
            "Demogorgon tooth from Mike needed to tune radio",
            "Radio needs to scan for gate frequency",
            "The gate is flickering... we don't have much time"
        ],
        "friend_location": "Upside Down Hawkins Lab (Mike)",
        "atmosphere": "Lights are flickering. You hear static from the radio."
    }

@app.get("/{team_id}/mike")
async def mike_look(team_id: str):
    """Mike: Look around Upside Down Hawkins Lab"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "GET_MIKE" not in team['steps_completed']:
        team['steps_completed'].append("GET_MIKE")
    
    return {
        "location": team['mike']['location'],
        "gate_status": "🔒 LOCKED" if team['mike']['gate_locked'] else "🔓 UNLOCKED",
        "items": team['mike']['items'],
        "notes": [
            "Eleven needs the demogorgon tooth to tune her radio",
            "Gate control panel needs activation code",
            "You hear Demogorgon screeches in the distance..."
        ],
        "friend_location": "Hawkins Lab - Real World (Eleven)",
        "atmosphere": "Dark, spores floating. Everything is mirrored and decaying."
    }

# POST - Send items
@app.post("/{team_id}/send_item")
async def send_item(team_id: str, data: SendItem):
    """Send an item to your friend across dimensions"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "POST" not in team['steps_completed']:
        team['steps_completed'].append("POST")
    
    # Mike sending demogorgon tooth to Eleven
    if data.from_friend == "Mike" and data.item == "demogorgon tooth":
        if "demogorgon tooth" in team['mike']['items']:
            # Move tooth from Mike to Eleven
            team['mike']['items'].remove("demogorgon tooth")
            team['eleven']['items'].append("demogorgon tooth")
            team['mike']['last_action'] = time.time()
            
            return {
                "success": True,
                "message": "Demogorgon tooth sent to Eleven!",
                "eleven_items": team['eleven']['items'],
                "mike_items": team['mike']['items'],
                "next_action": "Eleven: Combine radio and tooth (PUT /use_item)",
                "story_update": "The tooth vibrates with interdimensional energy"
            }
        else:
            return {
                "success": False,
                "message": "Mike doesn't have the demogorgon tooth",
                "mike_items": team['mike']['items']
            }
    
    return {
        "success": False,
        "message": "Cannot send that item. Only Mike can send 'demogorgon tooth'"
    }

# PUT - Use/Combine items
@app.put("/{team_id}/use_item")
async def use_item(team_id: str, data: UseItem):
    """Use or combine items"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "PUT" not in team['steps_completed']:
        team['steps_completed'].append("PUT")
    
    # Eleven combining radio and demogorgon tooth
    if data.friend == "Eleven" and data.action == "combine_radio_tooth":
        # Check if Eleven has both items
        has_radio = any("radio" in item for item in team['eleven']['items'])
        has_tooth = "demogorgon tooth" in team['eleven']['items']
        
        if has_radio and has_tooth:
            # Remove old items
            team['eleven']['items'] = [item for item in team['eleven']['items'] 
                                      if not item.startswith('radio') and item != "demogorgon tooth"]
            
            # Add tuned radio
            team['eleven']['items'].append("tuned radio")
            team['eleven']['last_action'] = time.time()
            
            return {
                "success": True,
                "message": "Tuned radio created! The radio now picks up interdimensional signals",
                "next_action": "Scan for gate frequency: PATCH /fix with action='scan_frequency'",
                "sound_effect": "📻 Radio static turns into clear frequency patterns"
            }
    
    return {
        "success": False,
        "message": "Cannot combine. Eleven needs both 'radio' and 'demogorgon tooth'",
        "eleven_items": team['eleven']['items']
    }

# PATCH - Fix/Adjust
@app.patch("/{team_id}/fix")
async def fix_something(team_id: str, data: FixAction):
    """Fix something or adjust state"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "PATCH" not in team['steps_completed']:
        team['steps_completed'].append("PATCH")
    
    # Eleven scanning for gate frequency
    if data.friend == "Eleven" and data.action == "scan_frequency":
        if "tuned radio" in team['eleven']['items']:
            team['eleven']['has_frequency'] = True
            team['eleven']['items'].append("frequency reading")
            team['eleven']['last_action'] = time.time()
            
            return {
                "success": True,
                "message": "Frequency found! The radio reveals the gate code",
                "code_revealed": "0110",
                "instructions": "Tell Mike to use code '0110' on the gate control panel (DELETE /remove)",
                "story": "The radio crackles: '0110... 0110... Will's birthday...'"
            }
    
    return {
        "success": False,
        "message": "Cannot scan frequency. Eleven needs 'tuned radio' first",
        "eleven_items": team['eleven']['items']
    }

# DELETE - Remove obstacle
@app.delete("/{team_id}/remove")
async def remove_obstacle(team_id: str, data: RemoveAction):
    """Remove an obstacle or activate device"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "DELETE" not in team['steps_completed']:
        team['steps_completed'].append("DELETE")
    
    # Mike activating gate control panel
    if data.friend == "Mike" and data.code == "0110":
        if "broken walkie-talkie" in team['mike']['items']:
            team['mike']['items'].remove("broken walkie-talkie")
            team['mike']['items'].append("activated gate panel")
            team['mike']['has_eggs'] = True
            team['mike']['last_action'] = time.time()
            
            return {
                "success": True,
                "message": "Gate control panel activated! The gate starts to stabilize",
                "instructions": "Both friends ready for escape! Coordinate final POST /escape within 10 seconds",
                "story": "The gate flickers and stabilizes. A clear portal forms. You have 10 seconds!"
            }
    
    return {
        "success": False,
        "message": "Cannot activate panel. Mike needs 'broken walkie-talkie' and correct code '0110'",
        "mike_items": team['mike']['items']
    }

# HEAD - Quick status check
@app.head("/{team_id}/status")
async def quick_status(team_id: str):
    """Quick status check (headers only)"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "HEAD" not in team['steps_completed']:
        team['steps_completed'].append("HEAD")
    
    from fastapi.responses import Response
    
    elapsed = int(time.time() - team['start_time'])
    
    headers = {
        "X-Team-Status": "ACTIVE",
        "X-Escaped": "YES" if team['escaped'] else "NO",
        "X-Eleven-Ready": "YES" if team['eleven']['has_frequency'] else "NO",
        "X-Mike-Ready": "YES" if team['mike']['has_eggs'] else "NO",
        "X-Time-Elapsed": str(elapsed),
        "X-Dimension-Sync": "STABLE" if team['eleven']['has_frequency'] and team['mike']['has_eggs'] else "UNSTABLE"
    }
    return Response(headers=headers)

# OPTIONS - See available methods
@app.options("/{team_id}/escape")
async def escape_options(team_id: str):
    """See available escape methods"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Record step
    if "OPTIONS" not in team['steps_completed']:
        team['steps_completed'].append("OPTIONS")
    
    from fastapi.responses import Response
    headers = {
        "Allow": "POST",
        "X-Escape-Requires": "Both friends POST within 10 seconds",
        "X-Preconditions": "Eleven needs frequency, Mike needs activated gate",
        "X-Warning": "Gate unstable - must synchronize perfectly"
    }
    return Response(headers=headers)

# GET - Hint system
@app.get("/{team_id}/hint")
async def get_hint(team_id: str, friend: Optional[str] = None):
    """Get a hint when stuck - analyzes team progress"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    current_time = time.time()
    
    # Prevent hint spamming (1 hint per 30 seconds)
    if team.get('last_hint_time') and (current_time - team['last_hint_time']) < 30:
        return {
            "warning": "Hints are limited! Please wait 30 seconds between hints.",
            "time_remaining": f"{30 - int(current_time - team['last_hint_time'])} seconds"
        }
    
    team['last_hint_time'] = current_time
    
    # Track hint usage
    if friend == "Eleven":
        team['eleven']['hints_used'] += 1
    elif friend == "Mike":
        team['mike']['hints_used'] += 1
    
    # Analyze team progress and provide context-aware hint
    hint = generate_contextual_hint(team, friend)
    
    # Record hint request
    hint_requests[team_id].append({
        "time": current_time,
        "friend": friend,
        "hint_given": hint
    })
    
    return {
        "hint": hint,
        "friend": friend or "Both",
        "hints_used_total": team['eleven']['hints_used'] + team['mike']['hints_used'],
        "note": "Hints are limited. Try to solve on your own first!"
    }

def generate_contextual_hint(team: dict, friend: Optional[str]) -> str:
    """Generate a hint based on team progress"""
    
    # Check if team has escaped
    if team['escaped']:
        return "You've already escaped! Get your escape key at GET /{team_id}/key"
    
    # Analyze based on completed steps
    steps = team['steps_completed']
    
    # Check basic progress
    if "GET_ELEVEN" not in steps or "GET_MIKE" not in steps:
        return "🔍 Start by having both Eleven and Mike look around their locations using GET endpoints"
    
    # Check if tooth was sent
    if "POST" not in steps:
        if friend == "Mike":
            return "📦 Mike should send the demogorgon tooth to Eleven using POST /send_item"
        elif friend == "Eleven":
            return "📻 Eleven needs the demogorgon tooth from Mike. Ask Mike to send it!"
        else:
            return "Mike needs to send his demogorgon tooth to Eleven using POST /send_item"
    
    # Check if radio was tuned
    if "PUT" not in steps:
        if friend == "Eleven":
            return "🔧 Eleven should combine the radio and demogorgon tooth using PUT /use_item with action='combine_radio_tooth'"
        else:
            return "Eleven needs to combine the radio and tooth. Tell her to use PUT /use_item"
    
    # Check if frequency was found
    if "PATCH" not in steps:
        if friend == "Eleven":
            return "📡 Eleven should scan for the gate frequency using PATCH /fix with action='scan_frequency'"
        else:
            return "Eleven needs to scan for the gate frequency with her tuned radio"
    
    # Check if gate panel was activated
    if "DELETE" not in steps:
        if friend == "Mike":
            return "🔢 Mike needs to use the code '0110' on the gate control panel using DELETE /remove"
        else:
            return "Mike needs the code '0110' to activate the gate panel. It was revealed by Eleven's radio!"
    
    # Check if ready for escape
    if "HEAD" not in steps:
        return "📊 Check dimension synchronization with HEAD /{team_id}/status"
    
    if "OPTIONS" not in steps:
        return "ℹ️ Check escape requirements with OPTIONS /{team_id}/escape"
    
    # Check escape attempts
    if len(team['escape_attempts']) < 2:
        if friend == "Eleven" and not team['eleven']['has_frequency']:
            return "Eleven isn't ready! She needs to find the frequency first"
        if friend == "Mike" and not team['mike']['has_eggs']:
            return "Mike isn't ready! He needs to activate the gate panel first"
        
        if team['escape_attempts']:
            last_attempt = team['escape_attempts'][-1]
            time_since = current_time - last_attempt['time']
            if time_since > 10:
                return "⏰ Last escape attempt expired! Both must POST /escape within 10 seconds. Try again!"
            else:
                return f"⏱️ Hurry! {10 - int(time_since)} seconds left for other friend to escape!"
        
        if friend == "Eleven":
            return "🚪 Eleven should attempt escape first using POST /escape. Mike must follow within 10 seconds!"
        elif friend == "Mike":
            return "🚪 Wait for Eleven to attempt escape first, then Mike must follow within 10 seconds!"
        else:
            return "Both friends must POST /escape within 10 seconds of each other! Eleven should go first"
    
    return "Check your items and make sure both friends are ready. Then coordinate escape attempts!"

# POST - Escape attempt
@app.post("/{team_id}/escape")
async def attempt_escape(team_id: str, data: EscapeAttempt):
    """Attempt to escape - both must call within 10 seconds"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    # Check preconditions
    if data.friend == "Eleven" and not team['eleven']['has_frequency']:
        raise HTTPException(400, "Eleven needs to find the frequency first!")
    if data.friend == "Mike" and not team['mike']['has_eggs']:
        raise HTTPException(400, "Mike needs to activate the gate panel first!")
    
    # Record escape attempt
    current_time = time.time()
    team['escape_attempts'].append({
        "friend": data.friend,
        "time": current_time
    })
    
    # Check if both escaped within 10 seconds
    if len(team['escape_attempts']) >= 2:
        # Get the last two attempts
        last_two = team['escape_attempts'][-2:]
        
        # Calculate time difference
        time_diff = abs(last_two[1]['time'] - last_two[0]['time'])
        
        if time_diff <= 10:  # Within 10 seconds
            # Mark team as escaped
            team['escaped'] = True
            team['end_time'] = current_time
            team['escape_key'] = f"ESCAPE_{team['team_name']}_{int(current_time)}"
            
            return {
                "success": True,
                "message": "ESCAPE SUCCESSFUL! The gate closes behind you.",
                "escape_key": team['escape_key'],
                "time_taken": f"{int(current_time - team['start_time'])} seconds",
                "steps_used": team['steps_completed'],
                "hints_used": team['eleven']['hints_used'] + team['mike']['hints_used'],
                "story": "You both jump through the gate as it collapses. Safe in the Real World!",
                "congratulations": "You used all HTTP methods to escape the Upside Down!"
            }
    
    return {
        "success": False,
        "message": f"Waiting for friend... {len(team['escape_attempts'])}/2 attempts",
        "time_window": "Both must POST within 10 seconds - Gate is unstable!",
        "warning": "Demogorgon screeches grow louder..."
    }

# GET - Final key
@app.get("/{team_id}/key")
async def get_escape_key(team_id: str):
    """Get the escape key after successful escape"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team = teams[team_id]
    
    if not team['escaped']:
        raise HTTPException(400, "Team hasn't escaped the Upside Down yet!")
    
    return {
        "team_name": team['team_name'],
        "escape_key": team['escape_key'],
        "time_taken": f"{int(team['end_time'] - team['start_time'])} seconds",
        "steps_completed": len(team['steps_completed']),
        "hints_used": team['eleven']['hints_used'] + team['mike']['hints_used'],
        "escaped": team['escaped'],
        "story_ending": "The gate is closed. Hawkins is safe... for now.",
        "certificate": f"Team {team['team_name']} successfully escaped the Upside Down!"
    }

# ADMIN - Get all teams
@app.get("/admin/all_teams")
async def get_all_teams():
    """Get all teams (for monitoring)"""
    all_teams = []
    current_time = time.time()
    
    for team_id, team in teams.items():
        elapsed = int(current_time - team['start_time'])
        
        all_teams.append({
            "team_id": team_id,
            "team_name": team['team_name'],
            "escaped": team['escaped'],
            "time_elapsed": f"{elapsed}s",
            "eleven_ready": team['eleven']['has_frequency'],
            "mike_ready": team['mike']['has_eggs'],
            "steps_count": len(team['steps_completed']),
            "hints_used": team['eleven']['hints_used'] + team['mike']['hints_used'],
            "escape_attempts": len(team['escape_attempts']),
            "status": "ESCAPED" if team['escaped'] else "TRAPPED"
        })
    
    return {
        "total_teams": len(all_teams),
        "escaped_teams": sum(1 for team in all_teams if team['escaped']),
        "trapped_teams": sum(1 for team in all_teams if not team['escaped']),
        "teams": all_teams
    }

# ADMIN - Reset team
@app.post("/admin/reset_team/{team_id}")
async def reset_team(team_id: str):
    """Reset a team to initial state"""
    if team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team_name = teams[team_id]['team_name']
    
    # Reset to initial state
    teams[team_id] = {
        'team_id': team_id,
        'team_name': team_name,
        'escaped': False,
        'escape_key': None,
        'start_time': time.time(),
        'end_time': None,
        'eleven': {
            'location': 'Hawkins Lab (Real World)',
            'items': DEFAULT_ITEMS["Eleven"].copy(),
            'gate_locked': True,
            'has_frequency': False,
            'has_eggs': False,
            'last_action': None,
            'hints_used': 0
        },
        'mike': {
            'location': 'Upside Down Hawkins Lab',
            'items': DEFAULT_ITEMS["Mike"].copy(),
            'gate_locked': True,
            'has_frequency': False,
            'has_eggs': False,
            'last_action': None,
            'hints_used': 0
        },
        'steps_completed': [],
        'escape_attempts': [],
        'last_hint_time': None
    }
    
    hint_requests[team_id] = []
    
    return {"message": f"Team '{team_name}' reset. The gate has reopened..."}

# Root endpoint
@app.get("/")
async def root():
    return {
        "game": "Stranger Things: Escape the Upside Down",
        "status": "Running - Season 4 Special",
        "total_teams": len(teams),
        "escaped_teams": sum(1 for team in teams.values() if team['escaped']),
        "story": "Two friends, two dimensions. One escape.",
        "characters": {
            "Eleven": "In the Real World. Has radio. Needs demogorgon frequency.",
            "Mike": "In the Upside Down. Has demogorgon tooth. Needs gate code."
        },
        "hint_system": "GET /{team_id}/hint?friend=Eleven (or Mike) - Get context-aware help",
        "instructions": {
            "1": "POST /create_team with {\"team_name\": \"YourTeam\"}",
            "2": "GET /{team_id}/eleven - Eleven looks around Hawkins Lab",
            "3": "GET /{team_id}/mike - Mike looks around Upside Down",
            "4": "POST /{team_id}/send_item with {\"from_friend\": \"Mike\", \"item\": \"demogorgon tooth\"}",
            "5": "PUT /{team_id}/use_item with {\"friend\": \"Eleven\", \"action\": \"combine_radio_tooth\"}",
            "6": "PATCH /{team_id}/fix with {\"friend\": \"Eleven\", \"action\": \"scan_frequency\"}",
            "7": "DELETE /{team_id}/remove with {\"friend\": \"Mike\", \"code\": \"0110\"}",
            "8": "HEAD /{team_id}/status - Check dimension sync",
            "9": "OPTIONS /{team_id}/escape - See escape requirements",
            "10": "POST /{team_id}/escape with {\"friend\": \"Eleven\"}",
            "11": "POST /{team_id}/escape with {\"friend\": \"Mike\"} (within 10s!)",
            "12": "GET /{team_id}/key - Get escape key",
            "help": "GET /{team_id}/hint - Get help when stuck"
        },
        "api_docs": "Visit /docs for interactive API documentation",
        "theme_music": "🎵 Should I Stay or Should I Go - The Clash 🎵",
        "note": "Multiple teams can play simultaneously. Each team has isolated state."
    }