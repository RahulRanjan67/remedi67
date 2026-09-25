from db import query
def create(uid,name,regno,city,loc):
    return query("INSERT INTO ngo_profiles (user_id,ngo_name,registration_number,city,locality) VALUES (%s,%s,%s,%s,%s)",(uid,name,regno,city,loc),commit=True)
