import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from faker import Faker
import os
import random

# Initialize Faker
fake = Faker()

# --- Configuration Parameters ---
START_DATE = date(2020, 1, 1)
END_DATE = date(2023, 12, 31)
NUM_PROPERTIES = 600 # Slightly increased to accommodate owner types better
NUM_OWNERS = 150 # A good number to distribute across categories
NUM_PLATFORMS = 7 # e.g., Airbnb, Booking.com, Direct, Expedia, Vrbo, TripAdvisor, Agoda
AVG_ADR = 190 # Base Average Daily Rate
TARGET_OCCUPANCY_RATE_OVERALL = 0.55 # Overall target across all properties
AVG_BOOKING_DURATION_DAYS = 5 # Average length of a booking

OUTPUT_DIR = 'synthetic_booking_data_v2'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Starting V2 data generation...")

# --- Global Date Calculations ---
total_days_in_period = (END_DATE - START_DATE).days + 1
# Convert END_DATE to datetime object for consistent comparisons later
END_DATE_DATETIME = datetime.combine(END_DATE, datetime.min.time())

# --- Property Type & Amenity Configuration ---
PROPERTY_TYPES_CONFIG = {
    'Apartment': {'base_adr_factor': 0.8, 'target_occupancy': 0.70, 'amenity_luxury_prob': 0.2, 'luxury_amenities_pool_rooftop_gym': False},
    'House': {'base_adr_factor': 1.0, 'target_occupancy': 0.55, 'amenity_luxury_prob': 0.4, 'luxury_amenities_pool_rooftop_gym': True},
    'Villa': {'base_adr_factor': 1.5, 'target_occupancy': 0.40, 'amenity_luxury_prob': 0.7, 'luxury_amenities_pool_rooftop_gym': True},
    'Cabin': {'base_adr_factor': 0.9, 'target_occupancy': 0.50, 'amenity_luxury_prob': 0.3, 'luxury_amenities_pool_rooftop_gym': False},
    'Townhouse': {'base_adr_factor': 0.95, 'target_occupancy': 0.60, 'amenity_luxury_prob': 0.3, 'luxury_amenities_pool_rooftop_gym': True},
    'Resort': {'base_adr_factor': 1.8, 'target_occupancy': 0.45, 'amenity_luxury_prob': 0.8, 'luxury_amenities_pool_rooftop_gym': True} # New type
}

# Base amenities (all properties have these)
BASIC_AMENITIES = ['WiFi', 'Hot Water', 'Air Conditioning', 'Balcony', 'Kitchenette', 'Parking']

# Luxury amenities, categorized by general compatibility
LUXURY_AMENITIES_GENERAL = ['Fireplace', 'Gym', 'Hot Tub', 'Game Room', 'Home Theater']
LUXURY_AMENITIES_OUTDOOR_LARGE = ['Swimming Pool', 'Private Beach Access', 'Rooftop Terrace'] # More suited for House, Villa, Resort

# --- Owner Categorization ---
OWNER_CATEGORIES_CONFIG = {
    'Sole Proprietor': {'count': int(NUM_OWNERS * 0.40), 'properties_per_owner': 1}, # 40% are sole
    'Family (1 Property)': {'count': int(NUM_OWNERS * 0.20), 'properties_per_owner': 1}, # 20% family owning 1 property
    'Family (>1 Property)': {'count': int(NUM_OWNERS * 0.20), 'properties_per_owner': (2, 4)}, # 20% family owning 2-4
    'Family (>5 Properties)': {'count': int(NUM_OWNERS * 0.15), 'properties_per_owner': (5, 9)}, # 15% family owning 5-9
    'Family (>10 Properties)': {'count': int(NUM_OWNERS * 0.05), 'properties_per_owner': (10, 15)} # 5% family owning 10-15
}
# Adjust counts to ensure total NUM_OWNERS is met and distribution is somewhat even
total_assigned_owners = sum(cat['count'] for cat in OWNER_CATEGORIES_CONFIG.values())
if total_assigned_owners != NUM_OWNERS:
    OWNER_CATEGORIES_CONFIG['Sole Proprietor']['count'] += (NUM_OWNERS - total_assigned_owners)


# --- Tenant and Review Configuration ---
NUM_TENANTS = 1000 # Number of unique tenants
TENANT_REPEAT_PROB = 0.3 # 30% chance a booking is from a returning tenant
BOOKING_PURPOSES = ['Holiday Fun', 'Business Meeting', 'Personal Getaway', 'Family Gathering', 'Event Accommodation']

REVIEW_RATING_DISTRIBUTION = {
    5: 0.60, # 60% chance of 5-star review
    4: 0.20, # 20% chance of 4-star
    3: 0.10, # 10% chance of 3-star
    2: 0.05, # 5% chance of 2-star
    1: 0.05  # 5% chance of 1-star
}

REVIEW_COMMENTS = {
    5: ["Absolutely loved it!", "Fantastic stay, highly recommend.", "Perfect in every way.", "Will definitely be back!", "Exceeded expectations."],
    4: ["Very good, just a minor issue with X.", "Enjoyed our stay, comfortable.", "Pleasant experience overall.", "Great location and amenities.", "Would stay again."],
    3: ["Decent stay, nothing special.", "It was okay, a bit noisy.", "Could use some improvements.", "Met basic needs.", "Average experience."],
    2: ["Disappointing, amenities not as described.", "Had issues with cleanliness.", "Not worth the price.", "Poor communication.", "Wouldn't recommend."],
    1: ["Horrible experience, avoid at all costs.", "Filthy and uncomfortable.", "Completely unacceptable.", "Misleading listing.", "Worst stay ever."]
}


print("Generating dim_date...")
# --- 1. Generate dim_date ---
date_id = 0
dates_list = []
date_to_id_map = {} # New: To store date -> date_id mapping for fact tables
current_date = START_DATE
while current_date <= END_DATE:
    dates_list.append({
        'date_id': date_id,
        'date': current_date,
        'year': current_date.year,
        'quarter': (current_date.month - 1) // 3 + 1,
        'month': current_date.month,
        'day': current_date.day,
        'weekday': current_date.weekday() # Monday=0, Sunday=6
    })
    date_to_id_map[current_date] = date_id # Store mapping
    current_date += timedelta(days=1)
    date_id += 1
dim_date = pd.DataFrame(dates_list)
dim_date.to_csv(os.path.join(OUTPUT_DIR, 'dim_date.csv'), index=False)
print(f"dim_date generated with {len(dim_date)} rows.")

print("Generating dim_owner...")
# --- 2. Generate dim_owner (with categories and UNIQUE emails) ---
owners_list = []
owner_id_counter = 1
generated_emails = set() # To store and check for unique emails

for category, config in OWNER_CATEGORIES_CONFIG.items():
    for _ in range(config['count']):
        owner_email = fake.email()
        # Ensure unique email
        while owner_email in generated_emails:
            owner_email = fake.email()
        generated_emails.add(owner_email)

        owners_list.append({
            'owner_id': owner_id_counter,
            'owner_name': fake.name(),
            'owner_email': owner_email,
            'owner_phone': fake.phone_number(),
            'owner_category': category
        })
        owner_id_counter += 1
dim_owner = pd.DataFrame(owners_list)
dim_owner.to_csv(os.path.join(OUTPUT_DIR, 'dim_owner.csv'), index=False)
print(f"dim_owner generated with {len(dim_owner)} rows.")

print("Generating dim_platform...")
# --- 3. Generate dim_platform ---
platform_names = ['Airbnb', 'Booking.com', 'Direct Website', 'Expedia', 'Vrbo', 'TripAdvisor', 'Agoda']
platforms_list = []
for i, name in enumerate(platform_names[:NUM_PLATFORMS]):
    platforms_list.append({
        'platform_id': i + 1,
        'platform_name': name
    })
dim_platform = pd.DataFrame(platforms_list)
dim_platform.to_csv(os.path.join(OUTPUT_DIR, 'dim_platform.csv'), index=False)
print(f"dim_platform generated with {len(dim_platform)} rows.")

print("Generating dim_property...")
# --- 4. Generate dim_property (with amenity logic and price adjustments) ---
property_types = list(PROPERTY_TYPES_CONFIG.keys())
countries = ['USA', 'Canada']
# Generate specific major cities in USA and Canada for better realism
us_cities = [fake.city() for _ in range(NUM_PROPERTIES // 8)] # ~75 US cities
ca_cities = [fake.city() for _ in range(NUM_PROPERTIES // 12)] # ~50 CA cities
all_cities = us_cities + ca_cities

properties_list = []
property_id_counter = 1

# Assign properties to owners based on categories
owner_category_map = {cat: [] for cat in OWNER_CATEGORIES_CONFIG.keys()}
for idx, owner_row in dim_owner.iterrows():
    owner_category_map[owner_row['owner_category']].append(owner_row['owner_id'])

# Distribute properties to owners ensuring category rules are followed
assigned_properties_count = 0
for category, config in OWNER_CATEGORIES_CONFIG.items():
    owner_ids_in_category = owner_category_map[category]
    random.shuffle(owner_ids_in_category) # Shuffle owners to distribute properties
    
    current_owner_idx = 0
    while current_owner_idx < len(owner_ids_in_category) and assigned_properties_count < NUM_PROPERTIES:
        owner_id = owner_ids_in_category[current_owner_idx]
        
        props_to_assign = 1 # Default for Sole/Family(1)
        if isinstance(config['properties_per_owner'], tuple): # For ranges
            props_to_assign = random.randint(config['properties_per_owner'][0], config['properties_per_owner'][1])
        
        # Ensure we don't exceed NUM_PROPERTIES
        props_to_assign = min(props_to_assign, NUM_PROPERTIES - assigned_properties_count)

        for _ in range(props_to_assign):
            if assigned_properties_count >= NUM_PROPERTIES:
                break

            prop_type = np.random.choice(property_types)
            prop_config = PROPERTY_TYPES_CONFIG[prop_type]

            # Assign amenities based on property type and luxury probability
            amenities = BASIC_AMENITIES[:] # Start with all basic amenities
            if random.random() < prop_config['amenity_luxury_prob']: # Chance for luxury amenities
                # Add general luxury amenities
                amenities.append(random.choice(LUXURY_AMENITIES_GENERAL))
                
                # Add outdoor/large luxury amenities based on property type compatibility
                # Corrected typo here: 'luxury_amenities_pool_rooft0op_gym' -> 'luxury_amenities_pool_rooftop_gym'
                if prop_config['luxury_amenities_pool_rooftop_gym'] and random.random() < 0.5: # 50% chance for these compatible types
                     amenities.append(random.choice(LUXURY_AMENITIES_OUTDOOR_LARGE))
            
            # Calculate base price based on property's base price and amenities
            # Add a small premium for each luxury amenity
            luxury_premium = len(amenities) - len(BASIC_AMENITIES) # Count added luxury amenities
            base_price = round(AVG_ADR * prop_config['base_adr_factor'] * np.random.uniform(0.9, 1.1) + (luxury_premium * 20), 2)
            base_price = max(50, base_price) # Ensure a minimum price

            country = np.random.choice(countries)
            city_pool = us_cities if country == 'USA' else ca_cities
            city = np.random.choice(city_pool)

            properties_list.append({
                'property_id': property_id_counter,
                'owner_id': owner_id,
                'property_type': prop_type,
                'country': country,
                'city': city,
                'distance_to_city_center': round(np.random.uniform(1, 20), 2),
                'amenities': ", ".join(sorted(list(set(amenities)))), # Unique and sorted amenities
                'base_price': base_price
            })
            property_id_counter += 1
            assigned_properties_count += 1
        current_owner_idx += 1

dim_property = pd.DataFrame(properties_list)
dim_property.to_csv(os.path.join(OUTPUT_DIR, 'dim_property.csv'), index=False)
print(f"dim_property generated with {len(dim_property)} rows.")

print("Generating dim_tenant...")
# --- 5. Generate dim_tenant ---
tenants_list = []
# To also handle potential duplicate emails for tenants if NUM_TENANTS is very large
generated_tenant_emails = set()
for i in range(NUM_TENANTS):
    tenant_email = fake.email()
    while tenant_email in generated_tenant_emails:
        tenant_email = fake.email()
    generated_tenant_emails.add(tenant_email)

    tenants_list.append({
        'tenant_id': i + 1,
        'tenant_name': fake.name(),
        'tenant_email': tenant_email,
        'tenant_phone': fake.phone_number()
    })
dim_tenant = pd.DataFrame(tenants_list)
dim_tenant.to_csv(os.path.join(OUTPUT_DIR, 'dim_tenant.csv'), index=False)
print(f"dim_tenant generated with {len(dim_tenant)} rows.")


print("Generating fact_bookings...")
# --- 6. Generate fact_bookings (Revised for distribution, occupancy, platform variation) ---
bookings_data = []
booking_id_counter = 1

# --- Helper to calculate total available nights for a property type ---
def get_total_available_nights_for_type(prop_type_name, num_properties_of_type):
    return num_properties_of_type * total_days_in_period

# --- Phase 1: Guaranteed Bookings for Each Property across All Years ---
# This ensures every property has data in every year
MIN_BOOKINGS_PER_PROPERTY_PER_YEAR = 1 # Minimum 1 booking per property per year
print("Generating guaranteed bookings for all properties across all years...")
for year in range(START_DATE.year, END_DATE.year + 1):
    year_start = max(START_DATE, date(year, 1, 1))
    year_end = min(END_DATE, date(year, 12, 31))
    
    days_in_current_year = (year_end - year_start).days + 1
    
    if days_in_current_year > 0: # Ensure year has days in the range
        for prop_id in dim_property['property_id'].unique():
            num_guaranteed_bookings_this_year = np.random.randint(MIN_BOOKINGS_PER_PROPERTY_PER_YEAR, MIN_BOOKINGS_PER_PROPERTY_PER_YEAR + 1) # 1 booking
            
            for _ in range(num_guaranteed_bookings_this_year):
                # Ensure check_in and check_out are within the current year's range
                # Ensure the range for randint is valid (at least 0)
                check_in_offset_range = max(0, days_in_current_year - AVG_BOOKING_DURATION_DAYS)
                check_in_offset = np.random.randint(0, check_in_offset_range + 1) if check_in_offset_range >= 0 else 0
                
                check_in_date = year_start + timedelta(days=check_in_offset)
                
                nights = max(1, int(np.random.normal(AVG_BOOKING_DURATION_DAYS, AVG_BOOKING_DURATION_DAYS / 2)))
                check_out_date = check_in_date + timedelta(days=nights)
                
                if check_out_date > year_end:
                    check_out_date = year_end
                    nights = (check_out_date - check_in_date).days
                
                if nights >= 1: # Only add if still valid
                    platform_id = np.random.choice(dim_platform['platform_id']) # Random platform for guaranteed bookings
                    revenue = round(nights * (AVG_ADR * np.random.uniform(0.8, 1.2)), 2)
                    damage_flag = np.random.choice([0, 1], p=[0.98, 0.02]) # Lower damage chance
                    damage_cost = round(np.random.uniform(50, 500), 2) if damage_flag == 1 else 0
                    turnover_flag = np.random.choice([0, 1], p=[0.75, 0.25]) # Higher turnover chance

                    # Ensure check_in_date and check_out_date are valid keys in date_to_id_map
                    check_in_date_id = date_to_id_map.get(check_in_date, None)
                    check_out_date_id = date_to_id_map.get(check_out_date, None)

                    if check_in_date_id is not None and check_out_date_id is not None:
                        bookings_data.append({
                            'booking_id': booking_id_counter,
                            'property_id': prop_id,
                            'platform_id': platform_id,
                            'tenant_id': np.random.choice(dim_tenant['tenant_id']), # Initial tenant
                            'check_in_date_id': check_in_date_id, # NEW: Add check_in_date_id
                            'check_out_date_id': check_out_date_id, # NEW: Add check_out_date_id
                            'check_in': check_in_date.strftime('%Y-%m-%d'),
                            'check_out': check_out_date.strftime('%Y-%m-%d'),
                            'nights': nights,
                            'revenue': revenue,
                            'purpose_of_stay': np.random.choice(BOOKING_PURPOSES),
                            'damage_flag': damage_flag,
                            'damage_cost': damage_cost,
                            'turnover_flag': turnover_flag
                        })
                        booking_id_counter += 1

print(f"Generated {len(bookings_data)} guaranteed bookings.")

# --- Phase 2: Generate Remaining Bookings to hit Target Occupancy with Variances ---
# Calculate total bookings needed based on target occupancy for each property type
total_bookings_target = 0
for prop_type, config in PROPERTY_TYPES_CONFIG.items():
    num_props_of_type = dim_property[dim_property['property_type'] == prop_type].shape[0]
    total_nights_available_for_type = num_props_of_type * total_days_in_period
    target_nights_booked_for_type = int(total_nights_available_for_type * config['target_occupancy'])
    total_bookings_target += int(target_nights_booked_for_type / AVG_BOOKING_DURATION_DAYS)

# Adjust for bookings already guaranteed
num_initial_bookings = len(bookings_data)
# Add some buffer to ensure target is met after random drops
remaining_bookings_to_generate = max(0, total_bookings_target - num_initial_bookings) + int(total_bookings_target * 0.1) # 10% buffer
print(f"Targeting total {total_bookings_target} bookings. Generating {remaining_bookings_to_generate} additional random bookings.")

# Store property_ids grouped by type for weighted random selection
property_ids_by_type = {pt: dim_property[dim_property['property_type'] == pt]['property_id'].tolist() for pt in PROPERTY_TYPES_CONFIG.keys()}

# Store platform_ids and their general performance biases
# Higher weight means more likely to be picked for overall bookings
PLATFORM_BIAS = {
    'Airbnb': 1.2, # Generally strong
    'Booking.com': 1.1, # Strong
    'Direct Website': 0.8, # Needs work
    'Expedia': 0.9, # Average
    'Vrbo': 1.0, # Average
    'TripAdvisor': 0.6, # Weaker
    'Agoda': 0.5 # Weaker
}
platform_names_ordered = [p['platform_name'] for p in platforms_list] # Ensure order for indexing
platform_weights = [PLATFORM_BIAS[name] for name in platform_names_ordered]
platform_ids_weighted = random.choices(dim_platform['platform_id'].tolist(), weights=platform_weights, k=10000) # Pre-generate weighted choices

for _ in range(remaining_bookings_to_generate):
    # Weighted random selection of property type based on target occupancy
    # Then select a property from that type
    selected_prop_type = random.choices(
        list(PROPERTY_TYPES_CONFIG.keys()), 
        weights=[PROPERTY_TYPES_CONFIG[pt]['target_occupancy'] * len(property_ids_by_type[pt]) for pt in PROPERTY_TYPES_CONFIG.keys()],
        k=1
    )[0]
    
    # Pick a random property ID from the selected type
    property_id = np.random.choice(property_ids_by_type[selected_prop_type])
    
    # Platform selection with general bias
    platform_id = np.random.choice(platform_ids_weighted) # Using pre-generated weighted list

    # Tenant selection: some repeat customers
    tenant_id = np.random.choice(dim_tenant['tenant_id'])
    if random.random() < TENANT_REPEAT_PROB and booking_id_counter > 100: # Ensure some history before repeating
        # Pick from already booked tenants to increase repeat customer likelihood
        recent_tenants = [b['tenant_id'] for b in bookings_data[-500:] if 'tenant_id' in b] # Look at recent bookings
        if recent_tenants:
            tenant_id = random.choice(recent_tenants)

    # Ensure check_in and check_out are within the overall date range
    # Check if total_days_in_period is greater than AVG_BOOKING_DURATION_DAYS to avoid negative range
    if total_days_in_period - AVG_BOOKING_DURATION_DAYS > 0:
        check_in_offset = np.random.randint(0, total_days_in_period - AVG_BOOKING_DURATION_DAYS)
    else:
        check_in_offset = 0 # Fallback if duration is too long for period

    check_in_date = START_DATE + timedelta(days=check_in_offset)
    
    nights = max(1, int(np.random.normal(AVG_BOOKING_DURATION_DAYS, AVG_BOOKING_DURATION_DAYS / 2)))
    check_out_date = check_in_date + timedelta(days=nights)

    # Convert check_out_date to datetime for comparison with END_DATE_DATETIME
    if datetime.combine(check_out_date, datetime.min.time()) > END_DATE_DATETIME:
        check_out_date = END_DATE
        nights = (check_out_date - check_in_date).days
        if nights < 1:
            continue

    # Calculate revenue based on property's base price (from dim_property) and ADR variation
    prop_base_price = dim_property[dim_property['property_id'] == property_id]['base_price'].iloc[0]
    # Revenue is influenced by property's base price, but varies like ADR
    revenue = round(nights * (prop_base_price * np.random.uniform(0.9, 1.3)), 2) # ADR will fluctuate around base_price

    damage_flag = np.random.choice([0, 1], p=[0.98, 0.02])
    damage_cost = round(np.random.uniform(50, 500), 2) if damage_flag == 1 else 0
    turnover_flag = np.random.choice([0, 1], p=[0.75, 0.25])

    # Ensure check_in_date and check_out_date are valid keys in date_to_id_map
    check_in_date_id = date_to_id_map.get(check_in_date, None)
    check_out_date_id = date_to_id_map.get(check_out_date, None)

    if check_in_date_id is not None and check_out_date_id is not None:
        bookings_data.append({
            'booking_id': booking_id_counter,
            'property_id': property_id,
            'platform_id': platform_id,
            'tenant_id': tenant_id,
            'check_in_date_id': check_in_date_id, # NEW: Add check_in_date_id
            'check_out_date_id': check_out_date_id, # NEW: Add check_out_date_id
            'check_in': check_in_date.strftime('%Y-%m-%d'),
            'check_out': check_out_date.strftime('%Y-%m-%d'),
            'nights': nights,
            'revenue': revenue,
            'purpose_of_stay': np.random.choice(BOOKING_PURPOSES),
            'damage_flag': damage_flag,
            'damage_cost': damage_cost,
            'turnover_flag': turnover_flag
        })
        booking_id_counter += 1

fact_bookings = pd.DataFrame(bookings_data)
fact_bookings = fact_bookings[fact_bookings['nights'] > 0] # Filter out 0-night bookings
fact_bookings.to_csv(os.path.join(OUTPUT_DIR, 'fact_bookings.csv'), index=False)
print(f"fact_bookings generated with {len(fact_bookings)} rows.")
print(f"Total nights generated: {fact_bookings['nights'].sum()}")
print(f"Total revenue generated: ${fact_bookings['revenue'].sum():,.2f}")


print("Generating fact_reviews...")
# --- 7. Generate fact_reviews ---
reviews_data = []
review_id_counter = 1
# Convert 'check_out' column to datetime objects for proper comparison
fact_bookings['check_out_dt'] = pd.to_datetime(fact_bookings['check_out'])

# Consider only bookings that have completed (check_out_date < END_DATE)
# Compare check_out_dt (datetime64[ns]) with END_DATE_DATETIME (datetime object)
completed_bookings = fact_bookings[fact_bookings['check_out_dt'] < END_DATE_DATETIME].copy()

# Limit the number of reviews to make it realistic (not every booking gets a review)
NUM_REVIEWS_TO_GENERATE = int(len(completed_bookings) * 0.7) # 70% of completed bookings get a review
if NUM_REVIEWS_TO_GENERATE > 0:
    bookings_for_review = completed_bookings.sample(n=NUM_REVIEWS_TO_GENERATE, random_state=42)
else:
    bookings_for_review = pd.DataFrame() # Empty if no bookings

for idx, booking_row in bookings_for_review.iterrows():
    rating = random.choices(
        list(REVIEW_RATING_DISTRIBUTION.keys()), 
        weights=list(REVIEW_RATING_DISTRIBUTION.values()), 
        k=1
    )[0]
    
    comment_pool = REVIEW_COMMENTS[rating]
    review_text = random.choice(comment_pool)
    
    # Review date is after check-out date
    # Use the datetime object directly from the DataFrame for consistency
    check_out_dt_val = booking_row['check_out_dt'].date() # Get date part from datetime object
    review_date = check_out_dt_val + timedelta(days=np.random.randint(1, 15)) # Review within 1-14 days after checkout
    
    # Ensure review_date is within the overall data range
    if datetime.combine(review_date, datetime.min.time()) > END_DATE_DATETIME:
        review_date = END_DATE
    
    # Ensure review_date is a valid key in date_to_id_map
    review_date_id = date_to_id_map.get(review_date, None)

    if review_date_id is not None:
        reviews_data.append({
            'review_id': review_id_counter,
            'booking_id': booking_row['booking_id'],
            'tenant_id': booking_row['tenant_id'], # Link to the tenant who made the booking
            'property_id': booking_row['property_id'], # Also link directly to property for easier analysis
            'review_date_id': review_date_id, # NEW: Add review_date_id
            'rating': rating,
            'review_text': review_text,
            'review_date': review_date.strftime('%Y-%m-%d')
        })
        review_id_counter += 1

fact_reviews = pd.DataFrame(reviews_data)
fact_reviews.to_csv(os.path.join(OUTPUT_DIR, 'fact_reviews.csv'), index=False)
print(f"fact_reviews generated with {len(fact_reviews)} rows.")

print("\nData generation complete! CSV files are in the 'synthetic_booking_data_v2' folder.")