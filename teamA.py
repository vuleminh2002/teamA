from flask import Flask, jsonify
import subprocess
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('test-teaminfo-firebase-adminsdk-xmys2-4031fad5e2.json')  # Path to your Firebase Admin SDK JSON file
firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()
@app.route('/')
def home():
    return 'Welcome to the Flask App! Visit /pull_and_transfer to start pulling and transferring repositories.'

# Favicon Route
@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/pull_and_transfer', methods=['GET'])
def pull_and_transfer():
    # Fetch all team documents from Firestore
    teams_ref = db.collection('teams')
    teams = teams_ref.stream()

    results = []

    for team_doc in teams:
        team = team_doc.to_dict()
        team_name = team['team_name']
        repo_url = team['repo_url']
        local_path = team['local_path']
        #cluster_user = "cluster_user"            # Replace with your cluster username
        #cluster_address = "gpu.cluster.address"  # Replace with your cluster address
        #cluster_path = team['cluster_path']

        try:
            # Clone the repo if it doesn't exist, otherwise pull latest changes
            if not os.path.exists(local_path):
                print(f"Cloning repository for {team_name}...")
                subprocess.run(["git", "clone", repo_url, local_path], check=True)
            else:
                print(f"Pulling latest code for {team_name}...")
                subprocess.run(["git", "-C", local_path, "pull", "origin", "main"], check=True)

            # Transfer code to GPU cluster using SCP
            

            results.append({team_name: "Success"})
        except subprocess.CalledProcessError as e:
            print(f"Error processing {team_name}: {e}")
            results.append({team_name: f"Error: {e}"})

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
