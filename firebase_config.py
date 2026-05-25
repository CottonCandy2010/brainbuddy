import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    """
    Initialize Firebase Admin SDK using service account key from Replit Secrets
    """
    if not firebase_admin._apps:
        try:
            # Get Firebase service account key from environment
            firebase_key = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
            
            if not firebase_key:
                raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY not found in environment variables")
            
            # Clean up the key - remove any potential whitespace
            firebase_key = firebase_key.strip()
            
            # Check if the key looks like valid JSON
            if not firebase_key.startswith('{'):
                print(f"Firebase key format issue - doesn't start with '{{'. First 50 chars: {firebase_key[:50]}")
                return False
            
            # Parse the JSON key
            service_account_info = json.loads(firebase_key)
            
            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            for field in required_fields:
                if field not in service_account_info:
                    print(f"Missing required field in Firebase key: {field}")
                    return False
            
            # Initialize Firebase with service account
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            
            print("Firebase initialized successfully!")
            return True
            
        except json.JSONDecodeError as e:
            print(f"Firebase JSON parsing error: {e}")
            print(f"Key preview (first 100 chars): {firebase_key[:100] if firebase_key else 'None'}")
            return False
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            return False
    else:
        print("Firebase already initialized")
        return True

def get_firestore_client():
    """
    Get Firestore client instance
    """
    if initialize_firebase():
        return firestore.client()
    else:
        return None