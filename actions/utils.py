import sqlite3
def query_yelp_db(db,location,**kwargs):
    query = "SELECT * from business WHERE city='" +location+"'"
    activity_synonyms = {'tours':['Beer Tours','Architectural Tours', 'ATV Tours', 'Food Tours','Wine Tours', 'Art Tours'],
                         'drink':['Bistros', 'Beer Bar', 'Brewpubs', 'Bartenders', 'Bars', 
                         'Whiskey Bars','Wine Tasting Room', 'Wine Tours', 'Wineries'],
                         'relax':['Massage', 'Ski Resorts', 'Hot Springs', 'Scuba Diving', 'Boating', 'Kayaking/Rafting', 'Meditation Centers'],
                         'exploring':['Bike Rentals', 'Local Flavor', 'Souvenir Shops', 'Kayaking', 'Traditional Clothing', 'Nightlife'],
                         'adventurous':['Skydiving','Kickboxing', 'Rafting', 'Horseback Riding', 'Skiing', 'Mountain Biking',
                         'Racing Experience', 'Paragliding', 'Surfing', 'Rock Climbing',
                         'Snorkeling', 'Hydro-jetting', 'Free Diving']
                         }
    cuisine = kwargs.get('cuisine')
    activities = kwargs.get('activity') #ANDing these
    ambience = kwargs.get('ambience') #NOT A COLUMN
    outdoor_seating = kwargs.get('outdoor_seating')

    if activities:
        if 'Restaurants' not in activities:
            cuisine = None
            ambience = None
            outdoor_seating = None

        for i in range(len(activities)):
            if activities[i] in activity_synonyms:
                activities[i] = activity_synonyms[activities[i]] #ORing activities
    
    age_allowed = kwargs.get('age_allowed')
    noise_level = kwargs.get('noise_level')
    accept_credit_card = kwargs.get('accept_credit_card')
    price_range = kwargs.get('price_range')
    wifi = kwargs.get('wifi')

    if outdoor_seating:
        query += " AND OutdoorSeating = 'True'"
    if age_allowed == 'adult':
        query += " AND (AgesAllowed = 'u'18plus'' OR AgesAllowed = 'u'19plus'' OR AgesAllowed = 'u'21plus'')"
    if noise_level=='quiet':
        query += " AND (NoiseLevel = 'u'quiet'' OR NoiseLevel = 'quiet')"
    if noise_level=='loud':
        query += " AND (NoiseLevel = 'u'loud'' OR NoiseLevel = ''loud'' OR NoiseLevel = 'u'very_loud'' OR NoiseLevel = ''very_loud'')"
    if accept_credit_card:
        query += " AND BusinessAcceptsCreditCards = 'True'"
    if price_range == 'low price':
        query += " AND RestaurantsPriceRange2 = '1'"
    if price_range == 'medium price':
        query += " AND RestaurantsPriceRange2 = '2'"
    if price_range == 'high price':
        query += " AND RestaurantsPriceRange2 = '3'"
    if price_range == 'very high price':
        query += " AND RestaurantsPriceRange2 = '4'"
    if wifi ==  'free wifi':
        query += " AND (WiFi = 'u'free'' OR WiFi =  ''free'')"
    if wifi ==  'no wifi':
        query += " AND (WiFi = 'u'no'' OR WiFi =  ''no'')"

    query += ' ORDER BY stars DESC, review_count DESC'

    print(query,activities,cuisine)
    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    if rows == []:
        return "No businesses match the search"
    
    new_rows = []
    for row in rows:
        #cat: 12, Amb: 24
        if activities:
            for activity in activities:
                if isinstance(activity,str) and activity in row[12]:
                    if cuisine: 
                        if cuisine in row[12]:    
                            if ambience:
                                ambs = row[24]
                                if ambs[0] == '{':
                                    ambs = eval(ambs)
                                else:
                                    ambs = None
                                if ambs:
                                    if ambs[ambience]:
                                        new_rows.append(row)
                                        break
                            else:
                                new_rows.append(row)
                    else:
                        new_rows.append(row)
                        break
                elif isinstance(activity,list):
                    for a in activity:
                        if a in row[12]:
                            new_rows.append(row)
                            break
        else:
            return rows
    return list(set(new_rows))
    #RUN_QUERY
    #FILTER ACTIVITIES
    #GET TOP N Results
    #SEND NAME OF TOP RESULTS To TWITTER
    
if __name__ == '__main__':
    conn = sqlite3.connect('datasets/Yelp.db')

    for row in query_yelp_db(conn,'Boulder',activity=['Restaurants'],cuisine='Mexican',outdoor_seating=True):
        print(row)
        break
            

