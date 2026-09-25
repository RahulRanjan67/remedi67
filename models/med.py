from db import query
def every():
    return query("SELECT m.*,c.category_name FROM medicines m LEFT JOIN medicine_categories c ON m.category_id=c.category_id ORDER BY m.medicine_name")
def cats():
    return query("SELECT * FROM medicine_categories ORDER BY category_name")
def getid(name,cat):
    row=query("SELECT medicine_id FROM medicines WHERE LOWER(medicine_name)=LOWER(%s)",(name,),one=True)
    if(row):
        return row["medicine_id"]
    return query("INSERT INTO medicines (medicine_name,category_id) VALUES (%s,%s)",(name,cat),commit=True)
