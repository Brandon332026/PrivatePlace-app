import streamlit as st
from datetime import datetime
import hashlib
import uuid
from PIL import Image
import io
from firebase_config import get_db, get_storage

# PayPal donation link
PAYPAL_DONATE_URL = "https://www.paypal.com/ncp/payment/JBDVRK4T8GLPJ"

# Initialize Firestore
db = get_db()
bucket = get_storage()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check if user is admin
def is_admin(username):
    return username == "admin"

# Upload image to Firebase Storage
def upload_image(image_file, ad_id):
    """Upload image to Firebase Storage and return public URL"""
    try:
        # Generate unique filename
        ext = image_file.name.split('.')[-1]
        filename = f"ads/{ad_id}/{uuid.uuid4()}.{ext}"
        
        # Resize image if too large
        img = Image.open(image_file)
        max_size = (1200, 1200)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format if img.format else 'JPEG')
        img_byte_arr.seek(0)
        
        # Upload to Firebase Storage
        blob = bucket.blob(filename)
        blob.upload_from_file(img_byte_arr, content_type=f'image/{ext}')
        blob.make_public()
        
        return blob.public_url
    except Exception as e:
        st.error(f"Error uploading image: {str(e)}")
        return None

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'view' not in st.session_state:
        st.session_state.view = 'browse'

# Main app
def main():
    st.set_page_config(page_title="PrivatePlace", page_icon=":material/search:", layout="wide")
    
    init_session_state()
    
    # Age verification warning
    if 'age_verified' not in st.session_state:
        st.session_state.age_verified = False
    
    if not st.session_state.age_verified:
        # Add some spacing at the top
        st.write("")
        st.write("")
        st.write("")
        
        # App branding
        st.markdown("<h1 style='text-align: center;'>PrivatePlace</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #888;'>Adult Personal Ad's 100% Free</h3>", unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        
        # Age verification
        st.markdown("<h2 style='text-align: center;'>Age Verification Required</h2>", unsafe_allow_html=True)
        st.warning("This site contains adult content. You must be 18 years or older to continue.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("I am 18 or older", type="primary", use_container_width=True):
                st.session_state.age_verified = True
                st.rerun()
        return
    
    # Header
    st.title("PrivatePlace")
    st.caption("Adult Personal Ad's 100% Free")
    
    # Navigation and auth in sidebar
    with st.sidebar:
        if not st.session_state.logged_in:
            st.header("Account")
        else:
            st.header("Navigation")
        
        if st.session_state.logged_in:
            st.success(f"Welcome, {st.session_state.username}")
            
            if is_admin(st.session_state.username):
                if st.button("Browse Ads", icon=":material/search:", use_container_width=True):
                    st.session_state.view = 'browse'
                    st.rerun()
                if st.button("Post New Ad", icon=":material/add:", use_container_width=True):
                    st.session_state.view = 'post'
                    st.rerun()
                if st.button("Pending Approvals", icon=":material/pending_actions:", use_container_width=True):
                    st.session_state.view = 'admin'
                    st.rerun()
            else:
                if st.button("Browse Ads", icon=":material/search:", use_container_width=True):
                    st.session_state.view = 'browse'
                    st.rerun()
                if st.button("Post New Ad", icon=":material/add:", use_container_width=True):
                    st.session_state.view = 'post'
                    st.rerun()
                if st.button("My Ads", icon=":material/person:", use_container_width=True):
                    st.session_state.view = 'my_ads'
                    st.rerun()
            
            st.divider()
            if st.button("Logout", icon=":material/logout:", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.view = 'browse'
                st.rerun()
        else:
            login_or_register()
        
        # Donation section
        st.divider()
        st.markdown("### HELP US KEEP THIS APP FREE BY DONATING")
        
        # PayPal Donate Button
        st.markdown(f'''
            <a href="{PAYPAL_DONATE_URL}" target="_blank">
                <button style="
                    background-color: #0070ba;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;
                    text-align: center;
                ">
                    💝 Donate via PayPal
                </button>
            </a>
        ''', unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.logged_in:
        if st.session_state.view == 'browse':
            browse_ads()
        elif st.session_state.view == 'post':
            post_ad()
        elif st.session_state.view == 'admin':
            admin_panel()
        elif st.session_state.view == 'my_ads':
            my_ads()
    else:
        browse_ads()

def login_or_register():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            # Get user from Firestore
            user_ref = db.collection('users').document(username).get()
            if user_ref.exists:
                user_data = user_ref.to_dict()
                if user_data['password'] == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Register")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_age = st.number_input("Age", min_value=18, max_value=120, key="reg_age")
        reg_location = st.text_input("Location", key="reg_location")
        reg_looking_for = st.text_area("What are you looking for?", key="reg_looking_for")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", type="primary", use_container_width=True):
            if not all([reg_name, reg_age, reg_location, reg_looking_for, reg_username, reg_password]):
                st.error("Please fill in all fields")
            elif reg_age < 18:
                st.error("You must be 18 or older to register")
            elif reg_password != reg_confirm_password:
                st.error("Passwords do not match")
            else:
                # Check if username exists
                user_ref = db.collection('users').document(reg_username).get()
                if user_ref.exists:
                    st.error("Username already exists")
                else:
                    # Create new user
                    db.collection('users').document(reg_username).set({
                        'name': reg_name,
                        'age': reg_age,
                        'location': reg_location,
                        'looking_for': reg_looking_for,
                        'password': hash_password(reg_password),
                        'created_at': datetime.now()
                    })
                    st.success("Registration successful! Please login.")

def browse_ads():
    st.header("Browse Ads")
    
    # Get approved ads from Firestore
    ads_ref = db.collection('ads').where('status', '==', 'approved').stream()
    approved_ads = [{'id': doc.id, **doc.to_dict()} for doc in ads_ref]
    
    if not approved_ads:
        st.info("No ads available yet. Be the first to post!")
        return
    
    # Filters
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("Search ads", placeholder="Search by title or description...")
    with col2:
        location_filter = st.text_input("Filter by location", placeholder="Enter location...")
    
    # Apply filters
    filtered_ads = approved_ads
    if search:
        filtered_ads = [ad for ad in filtered_ads if 
                       search.lower() in ad['title'].lower() or 
                       search.lower() in ad['description'].lower()]
    if location_filter:
        filtered_ads = [ad for ad in filtered_ads if 
                       location_filter.lower() in ad['location'].lower()]
    
    # Display ads
    if not filtered_ads:
        st.info("No ads match your search criteria")
    else:
        for ad in sorted(filtered_ads, key=lambda x: x['created_at'], reverse=True):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(ad['title'])
                    
                    # Display image if exists
                    if 'photo_url' in ad and ad['photo_url']:
                        st.image(ad['photo_url'], use_container_width=True)
                    
                    st.write(ad['description'])
                    if 'contact' in ad:
                        st.caption(f":material/contact_mail: {ad['contact']}")
                with col2:
                    st.caption(f":material/location_on: {ad['location']}")
                    st.caption(f":material/person: {ad['age']} years old")
                    created_at = ad['created_at']
                    if hasattr(created_at, 'strftime'):
                        st.caption(f":material/calendar_today: {created_at.strftime('%Y-%m-%d')}")
                st.divider()

def post_ad():
    st.header("Post New Ad")
    
    # Get user data
    user_ref = db.collection('users').document(st.session_state.username).get()
    user_data = user_ref.to_dict() if user_ref.exists else {}
    
    st.info("Your ad will be reviewed by our moderators before it goes live")
    
    title = st.text_input("Ad Title", placeholder="Enter a catchy title...")
    description = st.text_area("Description", placeholder="Describe what you're looking for...", height=200)
    
    # Photo upload
    photo = st.file_uploader("Upload Photo (optional)", type=['jpg', 'jpeg', 'png'], help="Upload a photo for your ad")
    
    # Pre-fill location and age from user profile
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("Location", value=user_data.get('location', ''))
    with col2:
        age = st.number_input("Age", min_value=18, max_value=120, value=user_data.get('age', 18))
    
    contact = st.text_input("Contact Information", placeholder="Email, phone, or preferred contact method...")
    
    if st.button("Submit Ad for Approval", type="primary", icon=":material/send:"):
        if not all([title, description, location, contact]):
            st.error("Please fill in all fields including contact information")
        elif age < 18:
            st.error("You must be 18 or older")
        else:
            # Create ad document
            ad_id = str(uuid.uuid4())
            ad_data = {
                'username': st.session_state.username,
                'title': title,
                'description': description,
                'location': location,
                'age': age,
                'contact': contact,
                'status': 'pending',
                'created_at': datetime.now()
            }
            
            # Upload photo if provided
            if photo:
                with st.spinner("Uploading photo..."):
                    photo_url = upload_image(photo, ad_id)
                    if photo_url:
                        ad_data['photo_url'] = photo_url
            
            # Save ad to Firestore
            db.collection('ads').document(ad_id).set(ad_data)
            st.success("Ad submitted! It will be visible once approved by a moderator.")
            st.session_state.view = 'my_ads'
            st.rerun()

def my_ads():
    st.header("My Ads")
    
    # Get user's ads from Firestore
    ads_ref = db.collection('ads').where('username', '==', st.session_state.username).stream()
    my_ads_list = [{'id': doc.id, **doc.to_dict()} for doc in ads_ref]
    
    if not my_ads_list:
        st.info("You haven't posted any ads yet")
        return
    
    # Group by status
    pending = [ad for ad in my_ads_list if ad['status'] == 'pending']
    approved = [ad for ad in my_ads_list if ad['status'] == 'approved']
    rejected = [ad for ad in my_ads_list if ad['status'] == 'rejected']
    
    tab1, tab2, tab3 = st.tabs([f"Approved ({len(approved)})", f"Pending ({len(pending)})", f"Rejected ({len(rejected)})"])
    
    with tab1:
        if approved:
            for ad in sorted(approved, key=lambda x: x['created_at'], reverse=True):
                display_my_ad(ad)
        else:
            st.info("No approved ads")
    
    with tab2:
        if pending:
            for ad in sorted(pending, key=lambda x: x['created_at'], reverse=True):
                display_my_ad(ad)
        else:
            st.info("No pending ads")
    
    with tab3:
        if rejected:
            for ad in sorted(rejected, key=lambda x: x['created_at'], reverse=True):
                display_my_ad(ad)
        else:
            st.info("No rejected ads")

def display_my_ad(ad):
    with st.container():
        st.subheader(ad['title'])
        
        # Display image if exists
        if 'photo_url' in ad and ad['photo_url']:
            st.image(ad['photo_url'], width=300)
        
        st.write(ad['description'])
        if 'contact' in ad:
            st.caption(f":material/contact_mail: {ad['contact']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f":material/location_on: {ad['location']}")
        with col2:
            st.caption(f":material/person: {ad['age']} years old")
        with col3:
            created_at = ad['created_at']
            if hasattr(created_at, 'strftime'):
                st.caption(f":material/calendar_today: {created_at.strftime('%Y-%m-%d')}")
        
        if ad['status'] == 'pending':
            st.warning("Awaiting approval")
        elif ad['status'] == 'approved':
            st.success("Approved and live")
        elif ad['status'] == 'rejected':
            st.error("Rejected")
        
        st.divider()

def admin_panel():
    st.header("Pending Ad Approvals")
    
    # Get pending ads from Firestore
    ads_ref = db.collection('ads').where('status', '==', 'pending').stream()
    pending_ads = [{'id': doc.id, **doc.to_dict()} for doc in ads_ref]
    
    if not pending_ads:
        st.info("No pending ads to review")
        return
    
    for ad in pending_ads:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.subheader(ad['title'])
                
                # Display image if exists
                if 'photo_url' in ad and ad['photo_url']:
                    st.image(ad['photo_url'], width=300)
                
                st.write(ad['description'])
                if 'contact' in ad:
                    st.caption(f":material/contact_mail: {ad['contact']}")
                st.caption(f"Posted by: {ad['username']} | Location: {ad['location']} | Age: {ad['age']}")
                created_at = ad['created_at']
                if hasattr(created_at, 'strftime'):
                    st.caption(f"Submitted: {created_at.strftime('%Y-%m-%d')}")
            
            with col2:
                if st.button("Approve", key=f"approve_{ad['id']}", type="primary", icon=":material/check_circle:"):
                    db.collection('ads').document(ad['id']).update({'status': 'approved'})
                    st.success("Ad approved!")
                    st.rerun()
                
                if st.button("Reject", key=f"reject_{ad['id']}", icon=":material/cancel:"):
                    db.collection('ads').document(ad['id']).update({'status': 'rejected'})
                    st.warning("Ad rejected")
                    st.rerun()
            
            st.divider()

if __name__ == "__main__":
    main()
