from flask import Flask, render_template, request, jsonify
import database
import os

app = Flask(__name__)

# Full Data Source
ESHOPBOX_REPS = [
    {"name": "Pratik Agarwal", "email": "pratik.agarwal@eshopbox.com", "booking_url": "https://calendar.app.google/L62uUYbY88UsDsAB7"},
    {"name": "Taufeeq Ahmad", "email": "taufeeq.ahmad@eshopbox.com", "booking_url": "https://calendar.app.google/zNYgBy3rhfWLcUnZ8"},
    {"name": "Prashant Gaurav", "email": "prashant.gaurav@eshopbox.com", "booking_url": "https://calendar.app.google/6AWcCKYc8HX451L49"},
    {"name": "Mukul Kharb", "email": "mukul.kharb@eshopbox.com", "booking_url": "https://calendar.app.google/L8FoXvB1pAZ9Toyd7"},
    {"name": "Syed Najmul Quadir", "email": "najmul.quadir@eshopbox.com", "booking_url": "https://calendar.app.google/KtPGSAbwsguBFbzN6"},
    {"name": "Sumit Gupta", "email": "sumit.gupta@eshopbox.com", "booking_url": "https://calendar.app.google/wvfB3vH85WRQ467s5"},
    {"name": "Diksha Syal", "email": "diksha.syal@eshopbox.com", "booking_url": "https://calendar.app.google/m1UEgWLRygQAu9k6A"},
    {"name": "Divya Shukla", "email": "divya.shukla@eshopbox.com", "booking_url": "https://calendar.app.google/o6CLJnxroSswBA94A"},
    {"name": "Sarthak Misra", "email": "sarthak.misra@eshopbox.com", "booking_url": "https://calendar.app.google/raaTfnYmRRb8vAJh8"},
    {"name": "Namita Tripathi", "email": "namita.tripathi@eshopbox.com", "booking_url": "https://calendar.app.google/cdUhp7bHQ6sfvWxw6"},
    {"name": "Vinayak Shukla", "email": "vinayak.shukla@eshopbox.com", "booking_url": "https://calendar.app.google/aXCfQTPi6yr9dy3q8"},
    {"name": "Raghwendra Kumar", "email": "raghwendra.kumar@eshopbox.com", "booking_url": "https://calendar.app.google/rpGfbGbsauATqUtM7"},
    {"name": "Manshi Verma", "email": "manshi.verma@eshopbox.com", "booking_url": "https://calendar.app.google/qgaivEmnhmGrkNvFA"},
    {"name": "Shubham Kumar", "email": "shubham.kumar@eshopbox.com", "booking_url": "https://calendar.app.google/kbdmKFnj34r2cwPk7"},
    {"name": "Sunil Sethi", "email": "sunil.sethi@eshopbox.com", "booking_url": "https://calendar.app.google/XNqNjvAH9fxAymDS7"},
    {"name": "Jatin Verma", "email": "jatin.verma@eshopbox.com", "booking_url": "https://calendar.app.google/827zwaVCYZUdJ8bh7"},
    {"name": "Ajeet Kumar", "email": "ajeet.kumar@eshopbox.com", "booking_url": "https://calendar.app.google/eiT1TKhYayTaxX4R6"},
    {"name": "Umang Seth", "email": "umang.seth@eshopbox.com", "booking_url": "https://calendar.app.google/8E8HfPDhvGH4rUPd6"},
    {"name": "Syed Shariq Hasan", "email": "shariq.hasan@eshopbox.com", "booking_url": "https://calendar.app.google/bQDAKaXMhwKSLACt7"},
    {"name": "Tauheed Prolta", "email": "tauheed.prolta@eshopbox.com", "booking_url": "https://calendar.app.google/Ds6YPCC7Kg9piEWx9"},
    {"name": "Abhijeet Chaudhary", "email": "abhijeet.chaudhary@eshopbox.com",
     "booking_url": "https://calendar.app.google/41oHduPC7zFBNczr6"},
    {"name": "Aditi Saini", "email": "aditi.saini@eshopbox.com", "booking_url": "https://calendar.app.google/rQTE4YaV6n7G2Tat5"},
]

# Filtering Logic for Teams
LST_TARGET_NAMES = [
    "Divya Shukla", 
    "Diksha Syal",
    "Raghwendra Kumar", 
    "Namita Tripathi", 
    "Vinayak Shukla", 
    "Shubham Kumar"
]

FST_TARGET_NAMES = [
    "Taufeeq Ahmad", 
    "Ajeet Kumar", 
    "Sunil Sethi"
]

def get_team_members(target_names):
    team = []
    target_names_lower = [n.lower() for n in target_names]
    for rep in ESHOPBOX_REPS:
        if rep['name'].lower() in target_names_lower:
            team.append(rep)
    return team

LST_TEAM = get_team_members(LST_TARGET_NAMES)
FST_TEAM = get_team_members(FST_TARGET_NAMES)

# Initialize database and team members at module level
# This ensures it runs on startup for both local and serverless
database.init_db()
database.initialize_team_members(LST_TEAM, "LST")
database.initialize_team_members(FST_TEAM, "FST")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eshopbox_create_event', methods=['POST'])
def create_event():
    data = request.json
    
    # Extract data with safe defaults
    preferred_date = data.get('date', "")
    time_slot = data.get('time_slot', "")
    volume_str = data.get('volume', "0")
    # Added .strip() to be safe against trailing whitespace
    service = data.get('service', "").strip()
    exclude_str = data.get('exclude', "")
    
    try:
        volume = int(volume_str)
    except ValueError:
        volume = 0

    # Determine eligible team
    # CRITICAL: Eshopbox Plus ALWAYS routes to FST, overriding volume
    if service == 'Eshopbox Plus':
        eligible_team = FST_TEAM
        team_name = "FST"
    elif service == 'Ship':
        eligible_team = LST_TEAM
        team_name = "LST"
    else:
        # For 'Fulfil' or 'Both', check volume
        # < 3000 -> LST
        # >= 3000 -> FST
        if volume < 3000:
            eligible_team = LST_TEAM
            team_name = "LST"
        else:
            eligible_team = FST_TEAM
            team_name = "FST"
    
    if not eligible_team:
        return jsonify({"error": "No eligible team configured"}), 500

    # Exclude logic
    excluded_names = [name.strip() for name in exclude_str.split(',') if name.strip()]
    available_team = [ae for ae in eligible_team if ae['name'] not in excluded_names]
    
    if not available_team:
        available_team = eligible_team

    # Round Robin Logic
    assignment_counts = database.get_assignment_counts(team_name)
    
    min_count = float('inf')
    selected_ae = None
    
    for ae in available_team:
        count = assignment_counts.get(ae['name'], 0)
        if count < min_count:
            min_count = count
            selected_ae = ae
    
    if not selected_ae:
        selected_ae = available_team[0]

    return jsonify({
        "name": selected_ae['name'],
        "email": selected_ae['email'],
        "calendar_link": selected_ae['booking_url'],
        "date": preferred_date,
        "time_slot": time_slot,
        "volume": volume,
        "service": service,
        "team": team_name
    })

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    data = request.json
    
    ae_name = data.get('name')
    ae_email = data.get('email')
    booking_date = data.get('date')
    time_slot = data.get('time_slot')
    volume = data.get('volume')
    service = data.get('service')
    team = data.get('team')
    
    database.record_booking(ae_name, ae_email, booking_date, time_slot, volume, service, team)
    
    return jsonify({"status": "success", "message": "Booking confirmed"})

if __name__ == '__main__':
    # Run locally
    app.run(debug=True)
