import streamlit as st

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    st.error("Firebase not available. Please check requirements.txt")

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not FIREBASE_AVAILABLE:
        return None, None
        
    if not firebase_admin._apps:
        try:
            # Get credentials from Streamlit secrets
            cred_dict = {
                "type": st.secrets["firebase"]["type"],
                "project_id": st.secrets["firebase"]["project_id"],
                "private_key_id": st.secrets["firebase"]["private_key_id"],
                "private_key": st.secrets["firebase"]["private_key"],
                "client_email": st.secrets["firebase"]["client_email"],
                "client_id": st.secrets["firebase"]["client_id"],
                "auth_uri": st.secrets["firebase"]["auth_uri"],
                "token_uri": st.secrets["firebase"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
                "universe_domain": st.secrets["firebase"]["universe_domain"]
            }
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': st.secrets["firebase"]["storageBucket"]
            })
        except Exception as e:
            st.error(f"Firebase initialization error: {str(e)}")
            return None, None
    
    return firestore.client(), storage.bucket()

def get_db():
    """Get Firestore database instance"""
    db, _ = initialize_firebase()
    return db

def get_storage():
    """Get Firebase Storage bucket instance"""
    _, bucket = initialize_firebase()
    return bucket
