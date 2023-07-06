import sqlite3

################################ Create Connection ################################

connection = sqlite3.connect("sha.db")
cursor = connection.cursor()

################################ Create a new database ################################
# cursor.execute("DROP TABLE average")
# cursor.execute("DROP TABLE measurements")
# cursor.execute(
#     """CREATE TABLE IF NOT EXISTS measurements (id int default 0, Date varchar(255), Time varchar(255), HeartRate float default 0.0, HeartRateVariabilitySDNN float default 0.0, RespiratoryRate float default 0.0, OxygenSaturation float default 0.0, WristTemperature float default 0.0, BodyMass float default 0.0)"""
# )
# cursor.execute(
#     """CREATE TABLE IF NOT EXISTS average (id int default 0,start_id int default 0,end_id int default 0,Date varchar(255), Time varchar(255), HeartRate float default 0.0, HeartRateVariabilitySDNN float default 0.0, RespiratoryRate float default 0.0, OxygenSaturation float default 0.0, WristTemperature float default 0.0, BodyMass float default 0.0)"""
# )
# cursor.execute(
#     """CREATE TABLE IF NOT EXISTS predicted (id int default 0,diseases_name_1 varchar(255),diseases_name_2 varchar(255),diseases_name_3 varchar(255),diseases_description_1 varchar(1000),diseases_description_2 varchar(1000),diseases_description_3 varchar(1000),
#     diet_name_1_1 varchar(255),
#     diet_name_1_2 varchar(255),
#     diet_name_1_3 varchar(255),
#     diet_description_1_1 varchar(1000),
#     diet_description_1_2 varchar(1000),
#     diet_description_1_3 varchar(1000),
#     workout_name_1_1 varchar(255),
#     workout_name_1_2 varchar(255),
#     workout_name_1_3 varchar(255),
#     workout_description_1_1 varchar(1000),
#     workout_description_1_2 varchar(1000),
#     workout_description_1_3 varchar(1000),
#     medication_name_1_1 varchar(255),
#     medication_name_1_2 varchar(255),
#     medication_name_1_3 varchar(255),
#     medication_description_1_1 varchar(1000),
#     medication_description_1_2 varchar(1000),
#     medication_description_1_3 varchar(1000),
#     diet_name_2_1 varchar(255),
#     diet_name_2_2 varchar(255),
#     diet_name_2_3 varchar(255),
#     diet_description_2_1 varchar(1000),
#     diet_description_2_2 varchar(1000),
#     diet_description_2_3 varchar(1000),
#     workout_name_2_1 varchar(255),
#     workout_name_2_2 varchar(255),
#     workout_name_2_3 varchar(255),
#     workout_description_2_1 varchar(1000),
#     workout_description_2_2 varchar(1000),
#     workout_description_2_3 varchar(1000),
#     medication_name_2_1 varchar(255),
#     medication_name_2_2 varchar(255),
#     medication_name_2_3 varchar(255),
#     medication_description_2_1 varchar(1000),
#     medication_description_2_2 varchar(1000),
#     medication_description_2_3 varchar(1000),
#     diet_name_3_1 varchar(255),
#     diet_name_3_2 varchar(255),
#     diet_name_3_3 varchar(255),
#     diet_description_3_1 varchar(1000),
#     diet_description_3_2 varchar(1000),
#     diet_description_3_3 varchar(1000),
#     workout_name_3_1 varchar(255),
#     workout_name_3_2 varchar(255),
#     workout_name_3_3 varchar(255),
#     workout_description_3_1 varchar(1000),
#     workout_description_3_2 varchar(1000),
#     workout_description_3_3 varchar(1000),
#     medication_name_3_1 varchar(255),
#     medication_name_3_2 varchar(255),
#     medication_name_3_3 varchar(255),
#     medication_description_3_1 varchar(1000),
#     medication_description_3_2 varchar(1000),
#     medication_description_3_3 varchar(1000))"""
# )
# cursor.execute(
#     """CREATE TABLE IF NOT EXISTS average_predicted (id int default 0,diseases_name_1 varchar(255),diseases_name_2 varchar(255),diseases_name_3 varchar(255),diseases_description_1 varchar(1000),diseases_description_2 varchar(1000),diseases_description_3 varchar(1000),
#     diet_name_1_1 varchar(255),
#     diet_name_1_2 varchar(255),
#     diet_name_1_3 varchar(255),
#     diet_description_1_1 varchar(1000),
#     diet_description_1_2 varchar(1000),
#     diet_description_1_3 varchar(1000),
#     workout_name_1_1 varchar(255),
#     workout_name_1_2 varchar(255),
#     workout_name_1_3 varchar(255),
#     workout_description_1_1 varchar(1000),
#     workout_description_1_2 varchar(1000),
#     workout_description_1_3 varchar(1000),
#     medication_name_1_1 varchar(255),
#     medication_name_1_2 varchar(255),
#     medication_name_1_3 varchar(255),
#     medication_description_1_1 varchar(1000),
#     medication_description_1_2 varchar(1000),
#     medication_description_1_3 varchar(1000),
#     diet_name_2_1 varchar(255),
#     diet_name_2_2 varchar(255),
#     diet_name_2_3 varchar(255),
#     diet_description_2_1 varchar(1000),
#     diet_description_2_2 varchar(1000),
#     diet_description_2_3 varchar(1000),
#     workout_name_2_1 varchar(255),
#     workout_name_2_2 varchar(255),
#     workout_name_2_3 varchar(255),
#     workout_description_2_1 varchar(1000),
#     workout_description_2_2 varchar(1000),
#     workout_description_2_3 varchar(1000),
#     medication_name_2_1 varchar(255),
#     medication_name_2_2 varchar(255),
#     medication_name_2_3 varchar(255),
#     medication_description_2_1 varchar(1000),
#     medication_description_2_2 varchar(1000),
#     medication_description_2_3 varchar(1000),
#     diet_name_3_1 varchar(255),
#     diet_name_3_2 varchar(255),
#     diet_name_3_3 varchar(255),
#     diet_description_3_1 varchar(1000),
#     diet_description_3_2 varchar(1000),
#     diet_description_3_3 varchar(1000),
#     workout_name_3_1 varchar(255),
#     workout_name_3_2 varchar(255),
#     workout_name_3_3 varchar(255),
#     workout_description_3_1 varchar(1000),
#     workout_description_3_2 varchar(1000),
#     workout_description_3_3 varchar(1000),
#     medication_name_3_1 varchar(255),
#     medication_name_3_2 varchar(255),
#     medication_name_3_3 varchar(255),
#     medication_description_3_1 varchar(1000),
#     medication_description_3_2 varchar(1000),
#     medication_description_3_3 varchar(1000))"""
# )


################################ Insert Values to Database ################################


# cursor.execute(
#     """INSERT INTO measurements (id, Date,Time, HeartRate, HeartRateVariabilitySDNN, RespiratoryRate , OxygenSaturation, WristTemperature, BodyMass) VALUES (1, "na", "aa",86,49.6873,16,96,35.2403,60.3277)"""
# )

################################ Update Values ################################

# cursor.execute("""Update product set id = 6 where code = 8902080000227""")

################################ Delete Values from Database ################################

# cursor.execute("""DELETE FROM prodect WHERE barcode = xxxxxx""")
# cursor.execute("DELETE FROM measurements")
# cursor.execute("DELETE FROM predicted")
# cursor.execute("DELETE FROM average_predicted")
# cursor.execute("DELETE FROM average")

################################ Display All Values in Database ################################

# cursor.execute(
#     "SELECT  HeartRate, HeartRateVariabilitySDNN, RespiratoryRate , OxygenSaturation, WristTemperature, BodyMass FROM measurements ORDER BY id DESC LIMIT 1"
# )
# records = cursor.fetchone()
cursor.execute("SELECT * FROM measurements")
# cursor.execute("""SELECT * FROM predicted """)
records = cursor.fetchall()
print("Total rows in measurements:  ", len(records))
print("Printing each row")
for row in records:
    print(row)
for i in range(1, 3):
    cursor.execute(
        "SELECT MAX(id) FROM average"
    )  # Replace 'your_table_name' with the actual name of your table
    last_inserted_id = cursor.fetchone()[0]  # Fetch the last inserted id
    cursor.execute("DELETE FROM average WHERE id=?", (last_inserted_id,))
# cursor.execute("SELECT * FROM average")
# records = cursor.fetchall()
# print("Total rows in measurements:  ", len(records))
# print("Printing each row")
# for row in records:
#     print(row)

# cursor.execute(
#     "SELECT id,diseases_name_1,diseases_name_2, diseases_name_3  FROM predicted"
# )
# cursor.execute(
#     """SELECT id, diseases_name_1,diseases_name_2,diseases_name_3 FROM average_predicted"""
# )
# records = cursor.fetchall()
# print("Total rows in predicted:  ", len(records))
# print("Printing each row")
# for row in records:
#     print(row)

# cursor.execute("SELECT * FROM average_predicted")
# records = cursor.fetchall()
# print("Total rows in predicted:  ", len(records))
# print("Printing each row")
# for row in records:
#     print(row)

################################ Close Connection ################################

connection.commit()
connection.close()

################################ END ###############################################
