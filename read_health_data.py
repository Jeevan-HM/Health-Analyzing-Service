import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil import tz
import openai
import random
import re
import sqlite3
import zipfile
import os
import threading


sha_database = sqlite3.connect("sha.db", check_same_thread=False)
sha_cursor = sha_database.cursor()


openai.api_key = "YOUR API KEY"


def predict(input):
    messages = [{"role": "user", "content": input}]
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content
    return reply


last_id = 0


def read_data(flag, start_id, end_id):
    try:
        zip_file_path = "/Users/jeevanhn/Downloads/export.zip"
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall()
        os.remove(zip_file_path)
    except Exception as e:
        print("Failed to extract data ", str(e))
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    current_date_str = current_date.strftime("%Y-%m-%d")
    current_time_str = current_time.strftime("%H:%M:%S")
    # If new measurements
    if flag:
        tree = ET.parse("apple_health_export/export.xml")
        root = tree.getroot()
        records = [
            {
                "Record Type": child.attrib["type"]
                .replace("HKQuantityTypeIdentifier", "")
                .replace("HKCategoryTypeIdentifier", "")
                .replace("AppleSleepingWristTemperature", "WristTemperature"),
                "Value": child.attrib.get("value", None),
                "Unit": child.attrib.get("unit", None),
                "Start Time": datetime.strptime(
                    child.attrib["startDate"], "%Y-%m-%d %H:%M:%S %z"
                ).astimezone(tz.gettz("Asia/Kolkata")),
                "End Time": datetime.strptime(
                    child.attrib["endDate"], "%Y-%m-%d %H:%M:%S %z"
                ).astimezone(tz.gettz("Asia/Kolkata")),
            }
            for child in root.findall(".//Record")
        ]
        df = pd.DataFrame(records)
        df = df.sort_values(by=["Start Time"], ascending=False)
        df = df.drop_duplicates(subset=["Record Type"], keep="first")
        records_dict = df.to_dict(orient="records")
        text = "Age 21, Gender Male"
        not_required = {
            "ActiveEnergyBurned",
            "BasalEnergyBurned",
            "EnvironmentalAudioExposure",
            "AppleStandHour",
            "DistanceWalkingRunning",
            "StepCount",
            "AppleExerciseTime",
            "FlightsClimbed",
            "AudioExposureEvent",
            "EnvironmentalSoundReduction",
            "AppleWalkingSteadiness",
            "DistanceCycling",
            "SixMinuteWalkTestDistance",
            "HeadphoneAudioExposure",
            "WalkingStepLength",
            "SixMinuteWalkTestDistance",
            "AppleStandTime",
            "WalkingAsymmetryPercentage",
            "StairDescentSpeed",
            "StairAscentSpeed",
            "HKDataTypeSleepDurationGoal",
            "SleepAnalysis",
            "HighHeartRateEvent",
            "Height",
            "WalkingSpeed",
            "WalkingDoubleSupportPercentage",
            "WalkingHeartRateAverage",
            "RestingHeartRate",
        }
        records = [
            item for item in records_dict if item["Record Type"] not in not_required
        ]
        record_mapping = {
            "HeartRate": "HeartRate",
            "HeartRateVariabilitySDNN": "HeartRateVariabilitySDNN",
            "RespiratoryRate": "RespiratoryRate",
            "OxygenSaturation": "OxygenSaturation",
            "WristTemperature": "WristTemperature",
            "BodyMass": "BodyMass",
        }
        for item in records:
            variable_name = record_mapping.get(item["Record Type"])

            if variable_name == "OxygenSaturation":
                globals()[variable_name] = float(item["Value"]) * 100
            elif variable_name == "Date" or variable_name == "Time":
                continue
            elif variable_name is not None:
                globals()[variable_name] = item["Value"]
                # globals()[variable_name] = random.randint(50, 150)

        sha_cursor.execute("""SELECT id FROM measurements ORDER BY id DESC LIMIT 1""")
        row = sha_cursor.fetchone()
        if row is not None:
            last_id = row[0]
        else:
            last_id = 0
        last_id += 1

        # values = [
        #     (
        #         last_id,
        #         current_date_str,
        #         current_time_str,
        #         86,
        #         35,
        #         16,
        #         100,
        #         35,
        #         # 137,
        #         61,
        #     )
        # ]
        values = [
            (
                last_id,
                current_date_str,
                current_time_str,
                98,
                35,
                16,
                97,
                37,
                61,
            )
        ]
        sha_cursor.executemany(
            "INSERT INTO measurements (id, Date, Time, HeartRate, HeartRateVariabilitySDNN, RespiratoryRate , OxygenSaturation, WristTemperature, BodyMass) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?)",
            values,
        )
        sha_cursor.execute("SELECT * FROM measurements ORDER BY id DESC LIMIT 1")
        records = sha_cursor.fetchall()
        for row in records:
            continue
        (
            last_id_,
            current_date_str_,
            current_time_str_,
            heart_rate,
            hr_variability,
            resp_rate,
            oxygen_sat,
            wrist_temp,
            body_mass,
            # 10,
        ) = row
    else:
        sha_cursor.execute("""SELECT id FROM average ORDER BY id DESC LIMIT 1""")
        row = sha_cursor.fetchone()
        if row is not None:
            last_id = row[0]
        else:
            last_id = 0
        last_id += 1
        startid = start_id
        endid = end_id
        sha_cursor.execute("PRAGMA table_info(measurements)")
        columns = sha_cursor.fetchall()
        column_names = [
            column[1] for column in columns if column[1] not in ["id", "Date", "Time"]
        ]
        for column_name in column_names:
            # Query to retrieve the values within the id range for the current column
            query = f"SELECT {column_name} FROM measurements WHERE id >= ? AND id <= ?"
            sha_cursor.execute(query, (start_id, end_id))
            # Fetch all the values from the query result
            values = sha_cursor.fetchall()
            # Calculate the average of the values for the current column
            values_sum = sum([value[0] for value in values])
            values_count = len(values)
            average = values_sum / values_count
            average = round(average, 2)

            if column_name == "HeartRate":
                heart_rate = average
            if column_name == "HeartRateVariabilitySDNN":
                hr_variability = average
            if column_name == "RespiratoryRate":
                resp_rate = average
            if column_name == "OxygenSaturation":
                oxygen_sat = average
            if column_name == "WristTemperature":
                wrist_temp = average
            if column_name == "BodyMass":
                body_mass = average

        values = [
            (
                last_id,
                startid,
                endid,
                current_date_str,
                current_time_str,
                heart_rate,
                hr_variability,
                resp_rate,
                oxygen_sat,
                wrist_temp,
                body_mass,
            )
        ]
        sha_cursor.executemany(
            "INSERT INTO average (id, start_id, end_id, Date, Time, HeartRate, HeartRateVariabilitySDNN, RespiratoryRate, OxygenSaturation, WristTemperature, BodyMass) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            values,
        )
        sha_cursor.execute("SELECT * FROM average")
        records = sha_cursor.fetchall()
        # print(records)
        # print("Total rows for measurements:  ", len(records))
        # print("Printing each row")
        for row in records:
            #     print(row)
            continue
        (
            id_,
            start_id_,
            end_id_,
            date,
            time,
            heart_rate,
            hr_variability,
            resp_rate,
            oxygen_sat,
            wrist_temp,
            body_mass,
        ) = row
    text = f"Age 22, Gender Male, HeartRate {heart_rate} count/min, HeartRateVariabilitySDNN {hr_variability} ms, RespiratoryRate {resp_rate} count/min, OxygenSaturation {oxygen_sat} %, WristTemperature {wrist_temp} degC, BodyMass {body_mass} kg. Which readings are not normal? (Yes or no with a few words)"
    print("Collected Data Average = ", text)
    sha_database.commit()
    return text


def get_disease_risk(input):
    pattern_order = r"\d+\.:"
    try:
        diseases_name = []
        diseases_defn = []
        while True:
            diseases = predict(
                "List 3 diseases risk that "
                + input
                + " can lead to? With a short description (Name:description)"
            ).splitlines()
            diseases = list(filter(None, diseases))
            if "AI" in diseases[0] or "sorry" in diseases[0] or "cannot" in diseases[0]:
                continue
            for item in diseases[:3]:
                parts = re.split(":|-", item.strip())
                parts[0] = re.sub(pattern_order, "", parts[0])
                diseases_name.append(parts[0].strip())
                diseases_defn.append(parts[1].strip())
            break
        if len(diseases_name) == 3:
            return {
                "diseases_name": diseases_name,
                "diseases_description": diseases_defn,
            }
        else:
            return {
                "diseases_name": "error",
                "diseases_description": "error",
            }
    except Exception as e:
        print("An error occurred while predicting diets: ", str(e))
        return {"diseases_name": "error", "diseases_description": "error"}


def predict_diet(input):
    global diet_name, diet_defn
    diet_name = []
    diet_defn = []
    try:
        for item in input:
            diet_prediction = predict(
                "List 3 diets for "
                + item
                + "  with a short description (Name:description)"
            )
            if (
                "AI" in diet_prediction
                or "sorry" in diet_prediction
                or "cannot" in diet_prediction
            ):
                diet_name.append("Na")
                diet_name.append("Na")
                diet_name.append("Na")
                diet_defn.append("Na")
                diet_defn.append("Na")
                diet_defn.append("Na")
                print("Unable to predict diet for " + item)
                continue
            diet_prediction = re.sub(r"[\d+\.())]", "", diet_prediction)
            diet_list = re.split("\n\n", diet_prediction)
            for diet_item in diet_list:
                diet_item_list = re.split("(?<!\w)-\s+|:", diet_item)
                diet_title = diet_item_list[0].strip()
                diet_name.append(diet_title)
                diet_definition = diet_item_list[1].strip()
                diet_defn.append(diet_definition)
        while len(diet_name) != 9:
            diet_name.append("Na")
            diet_defn.append("Na")
        return {"diet_name": diet_name, "diet_description": diet_defn}
    except Exception as e:
        print("An error occurred while predicting diets: ", str(e))
        return {"diet_name": "error", "diet_description": "error"}


def predict_workout(input):
    global workout_defn, workout_name
    workout_name = []
    workout_defn = []
    try:
        for item in input:
            workout_prediction = predict(
                " List 3 workout for "
                + item
                + "  with a short description (Name:description)"
            )
            if (
                "AI" in workout_prediction
                or "sorry" in workout_prediction
                or "cannot" in workout_prediction
            ):

                workout_name.append("Na")
                workout_name.append("Na")
                workout_name.append("Na")

                workout_defn.append("Na")
                workout_defn.append("Na")
                workout_defn.append("Na")

                print("Unable to predict workout for " + item)
                continue

            workout_prediction = re.sub(r"[0-9.())]", "", workout_prediction)
            workout_list = re.split("\n\n", workout_prediction)
            for workout_item in workout_list:
                workout_item_list = re.split("(?<!\w)-\s+|:", workout_item)
                workout_title = workout_item_list[0].strip()
                workout_definition = workout_item_list[1].strip()
                workout_name.append(workout_title)
                workout_defn.append(workout_definition)
        while len(workout_name) != 9:
            workout_name.append("Na")
            workout_defn.append("Na")
        return {"workout_name": workout_name, "workout_description": workout_defn}
    except Exception as e:
        print("An error occurred while predicting workouts: ", str(e))
        return {"workout_name": "error", "workout_description": "error"}

    # print("\n")


def predict_medication(input):
    global medication_name, medication_defn
    medication_name = []
    medication_defn = []
    try:
        for item in input:
            medication_prediction = predict(
                " List 3 medication for "
                + item
                + "  with a short description (Name:description)"
            )
            if (
                "AI" in medication_prediction
                or "sorry" in medication_prediction
                or "cannot" in medication_prediction
            ):
                medication_name.append("Na")
                medication_name.append("Na")
                medication_name.append("Na")
                medication_defn.append("Na")
                medication_defn.append("Na")
                medication_defn.append("Na")
                print("Unable to predict medication for " + item)
                continue

            medication_prediction = re.sub(r"[0-9.())]", "", medication_prediction)
            medication_list = re.split("\n\n", medication_prediction)
            for medication_item in medication_list:
                medication_item_list = re.split("-|:", medication_item)
                medication_title = medication_item_list[0].strip()
                medication_name.append(medication_title)
                medication_definition = medication_item_list[1].strip()
                medication_defn.append(medication_definition)
        while len(medication_name) != 9:
            medication_name.append("Na")
            medication_defn.append("Na")
        return {
            "medication_name": medication_name,
            "medication_description": medication_defn,
        }
    except Exception as e:
        print("An error occurred while predicting medications: ", str(e))
        return {"medication_name": "error", "medication_description": "error"}


def analyze_health(flag, start_id, end_id):
    # try:
    input = read_data(flag, start_id, end_id)
    print("\n" + "=" * 200)
    print("Completed Collecting Data")
    print("\nChecking if normal")
    is_normal = predict(input)
    # if flag:
    #     sha_cursor.execute(
    #         "SELECT MAX(id) FROM measurements"
    #     )  # Replace 'your_table_name' with the actual name of your table
    #     last_inserted_id = sha_cursor.fetchone()[0]  # Fetch the last inserted id
    #     sha_cursor.execute("DELETE FROM measurements WHERE id=?", (last_inserted_id,))
    # else:
    #     sha_cursor.execute(
    #         "SELECT MAX(id) FROM average"
    #     )  # Replace 'your_table_name' with the actual name of your table
    #     last_inserted_id = sha_cursor.fetchone()[0]  # Fetch the last inserted id
    #     sha_cursor.execute("DELETE FROM average WHERE id=?", (last_inserted_id,))
    print(is_normal)
    if "not" in is_normal:
        print("\nCompleted Checking if normal")
        print("\n" + "=" * 200)
        print("\nPredicting Diseases")
        print("\n")
        attempts = 0
        diseases = get_disease_risk(is_normal)
        print(diseases["diseases_name"])
        print("\n" + "-" * 150)
        print("Total Number of Diseases predicted = ", len(diseases["diseases_name"]))
        while attempts < 2 and len(diseases["diseases_name"]) != 3:
            print("Retrying Diseases Prediction Attempt = ", attempts + 1)

            if diseases["diseases_name"] == "error":
                print("Error getting disease risk.")
                diseases = get_disease_risk(is_normal)
            elif diseases["diseases_name"] == "You are healthy":
                print("You are healthy")
                break
            attempts += 1
        print("Completed Predicting Diseases")
        print("\n" + "=" * 200)
        if len(diseases["diseases_name"]) == 3:
            attempts = 0
            print("Predicted Diseases = ")
            print(diseases["diseases_name"])
            print("\n" + "-" * 150)
            print("\n" + "=" * 200)
            print("Predicting Diets, Workouts and Medications")

            t1 = threading.Thread(
                target=predict_diet, args=(diseases["diseases_name"],)
            )
            t2 = threading.Thread(
                target=predict_workout, args=(diseases["diseases_name"],)
            )
            t3 = threading.Thread(
                target=predict_medication, args=(diseases["diseases_name"],)
            )
            t1.start()
            t2.start()
            t3.start()
            t1.join()
            t2.join()
            t3.join()
            diet = {"diet_name": diet_name, "diet_description": diet_defn}
            workout = {
                "workout_name": workout_name,
                "workout_description": workout_defn,
            }
            medication = {
                "medication_name": medication_name,
                "medication_description": medication_defn,
            }
            print("Completed predicting Diets, Workouts and Medications")
            print("\n" + "-" * 150)
            print("\nPredicted Diet = ")
            print(diet_name)
            print("Total Number of Diets predicted = ", len(diet["diet_name"]))
            print("\n" + "-" * 150)
            print("\nPredicted Workout = ")
            print(workout_name)
            print("Total Number of Workout predicted = ", len(workout["workout_name"]))
            print("\n" + "-" * 150)
            print("\nPredicted Medication = ")
            print(medication_name)
            print(
                "Total Number of Workout predicted = ",
                len(medication["medication_name"]),
            )
            print("\n" + "-" * 150)
            print("\n" + "=" * 100)
            # diet = predict_diet(diseases["diseases_name"])
            # while len(diet["diet_name"]) != 9:
            #     diet["diet_name"].append("Na")
            #     diet["diet_description"].append("Na")
            # print("Done Predicting Diets")
            # print("\n" + "=" * 200)
            # print("Predicting Workout")

            # workout = predict_workout(diseases["diseases_name"])
            # while len(workout["workout_name"]) != 9:
            #     workout["workout_name"].append("Na")
            #     workout["workout_description"].append("Na")
            # print("Done Predicting Workout")
            # print("\n" + "=" * 200)
            # print("Predicting Medication")

            # medication = predict_medication(diseases["diseases_name"])

            # while len(medication["medication_name"]) != 9:
            #     medication["medication_name"].append("Na")
            #     medication["medication_description"].append("Na")
            # print("Done Predicting Medication")

            # Construct the SQL query dynamically
            # Calculate lengths of the lists
            if flag:
                sha_cursor.execute(
                    """SELECT id FROM measurements ORDER BY id DESC LIMIT 1"""
                )
                # print(sha_cursor.fetchone())
                last_id = sha_cursor.fetchone()[0]
                # Construct the SQL query dynamically
                values = [
                    (
                        last_id,
                        diseases["diseases_name"][0],
                        diseases["diseases_name"][1],
                        diseases["diseases_name"][2],
                        diseases["diseases_description"][0],
                        diseases["diseases_description"][1],
                        diseases["diseases_description"][2],
                        diet["diet_name"][0],
                        diet["diet_name"][1],
                        diet["diet_name"][2],
                        diet["diet_description"][0],
                        diet["diet_description"][1],
                        diet["diet_description"][2],
                        workout["workout_name"][0],
                        workout["workout_name"][1],
                        workout["workout_name"][2],
                        workout["workout_description"][0],
                        workout["workout_description"][1],
                        workout["workout_description"][2],
                        medication["medication_name"][0],
                        medication["medication_name"][1],
                        medication["medication_name"][2],
                        medication["medication_description"][0],
                        medication["medication_description"][1],
                        medication["medication_description"][2],
                        diet["diet_name"][3],
                        diet["diet_name"][4],
                        diet["diet_name"][5],
                        diet["diet_description"][3],
                        diet["diet_description"][4],
                        diet["diet_description"][5],
                        workout["workout_name"][3],
                        workout["workout_name"][4],
                        workout["workout_name"][5],
                        workout["workout_description"][3],
                        workout["workout_description"][4],
                        workout["workout_description"][5],
                        medication["medication_name"][3],
                        medication["medication_name"][4],
                        medication["medication_name"][5],
                        medication["medication_description"][3],
                        medication["medication_description"][4],
                        medication["medication_description"][5],
                        diet["diet_name"][6],
                        diet["diet_name"][7],
                        diet["diet_name"][8],
                        diet["diet_description"][6],
                        diet["diet_description"][7],
                        diet["diet_description"][8],
                        workout["workout_name"][6],
                        workout["workout_name"][7],
                        workout["workout_name"][8],
                        workout["workout_description"][6],
                        workout["workout_description"][7],
                        workout["workout_description"][8],
                        medication["medication_name"][6],
                        medication["medication_name"][7],
                        medication["medication_name"][8],
                        medication["medication_description"][6],
                        medication["medication_description"][7],
                        medication["medication_description"][8],
                    )
                ]
                sha_cursor.executemany(
                    """INSERT INTO predicted (
                        id,
                        diseases_name_1,
                        diseases_name_2,
                        diseases_name_3,
                        diseases_description_1,
                        diseases_description_2,
                        diseases_description_3,
                        diet_name_1_1,
                        diet_name_1_2,
                        diet_name_1_3,
                        diet_description_1_1,
                        diet_description_1_2,
                        diet_description_1_3,
                        workout_name_1_1,
                        workout_name_1_2,
                        workout_name_1_3,
                        workout_description_1_1,
                        workout_description_1_2,
                        workout_description_1_3,
                        medication_name_1_1,
                        medication_name_1_2,
                        medication_name_1_3,
                        medication_description_1_1,
                        medication_description_1_2,
                        medication_description_1_3,
                        diet_name_2_1,
                        diet_name_2_2,
                        diet_name_2_3,
                        diet_description_2_1,
                        diet_description_2_2,
                        diet_description_2_3,
                        workout_name_2_1,
                        workout_name_2_2,
                        workout_name_2_3,
                        workout_description_2_1,
                        workout_description_2_2,
                        workout_description_2_3,
                        medication_name_2_1,
                        medication_name_2_2,
                        medication_name_2_3,
                        medication_description_2_1,
                        medication_description_2_2,
                        medication_description_2_3,
                        diet_name_3_1,
                        diet_name_3_2,
                        diet_name_3_3,
                        diet_description_3_1,
                        diet_description_3_2,
                        diet_description_3_3,
                        workout_name_3_1,
                        workout_name_3_2,
                        workout_name_3_3,
                        workout_description_3_1,
                        workout_description_3_2,
                        workout_description_3_3,
                        medication_name_3_1,
                        medication_name_3_2,
                        medication_name_3_3,
                        medication_description_3_1,
                        medication_description_3_2,
                        medication_description_3_3)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    values,
                )

                # print("Disease descriptions = ")
                # print(diseases_defn)
                # use fetchone() instead of fetchall()
                # sha_cursor.execute("SELECT * FROM predicted")
                sha_cursor.execute(
                    """SELECT id, diseases_name_1, diseases_name_2, diseases_name_3, diet_name_1_1, diet_name_1_2, diet_name_1_3, workout_name_1_1, workout_name_1_2, workout_name_1_3, diet_name_2_1, diet_name_2_2, diet_name_2_3, workout_name_2_1, workout_name_2_2, workout_name_2_3, diet_name_3_1, diet_name_3_2, diet_name_3_3, workout_name_3_1, workout_name_3_2, workout_name_3_3,medication_name_3_1, medication_name_3_2, medication_name_3_3 FROM predicted"""
                )
                records = sha_cursor.fetchall()
                print("Total rows for predicted: ", len(records))
                for row in records:
                    print(row)
            else:
                sha_cursor.execute(
                    """SELECT id FROM average ORDER BY id DESC LIMIT 1"""
                )
                # print(sha_cursor.fetchone())
                last_id = sha_cursor.fetchone()[0]
                # Construct the SQL query dynamically
                values = [
                    (
                        last_id,
                        diseases["diseases_name"][0],
                        diseases["diseases_name"][1],
                        diseases["diseases_name"][2],
                        diseases["diseases_description"][0],
                        diseases["diseases_description"][1],
                        diseases["diseases_description"][2],
                        diet["diet_name"][0],
                        diet["diet_name"][1],
                        diet["diet_name"][2],
                        diet["diet_description"][0],
                        diet["diet_description"][1],
                        diet["diet_description"][2],
                        workout["workout_name"][0],
                        workout["workout_name"][1],
                        workout["workout_name"][2],
                        workout["workout_description"][0],
                        workout["workout_description"][1],
                        workout["workout_description"][2],
                        medication["medication_name"][0],
                        medication["medication_name"][1],
                        medication["medication_name"][2],
                        medication["medication_description"][0],
                        medication["medication_description"][1],
                        medication["medication_description"][2],
                        diet["diet_name"][3],
                        diet["diet_name"][4],
                        diet["diet_name"][5],
                        diet["diet_description"][3],
                        diet["diet_description"][4],
                        diet["diet_description"][5],
                        workout["workout_name"][3],
                        workout["workout_name"][4],
                        workout["workout_name"][5],
                        workout["workout_description"][3],
                        workout["workout_description"][4],
                        workout["workout_description"][5],
                        medication["medication_name"][3],
                        medication["medication_name"][4],
                        medication["medication_name"][5],
                        medication["medication_description"][3],
                        medication["medication_description"][4],
                        medication["medication_description"][5],
                        diet["diet_name"][6],
                        diet["diet_name"][7],
                        diet["diet_name"][8],
                        diet["diet_description"][6],
                        diet["diet_description"][7],
                        diet["diet_description"][8],
                        workout["workout_name"][6],
                        workout["workout_name"][7],
                        workout["workout_name"][8],
                        workout["workout_description"][6],
                        workout["workout_description"][7],
                        workout["workout_description"][8],
                        medication["medication_name"][6],
                        medication["medication_name"][7],
                        medication["medication_name"][8],
                        medication["medication_description"][6],
                        medication["medication_description"][7],
                        medication["medication_description"][8],
                    )
                ]
                sha_cursor.executemany(
                    """INSERT INTO average_predicted (
                        id,
                        diseases_name_1,
                        diseases_name_2,
                        diseases_name_3,
                        diseases_description_1,
                        diseases_description_2,
                        diseases_description_3,
                        diet_name_1_1,
                        diet_name_1_2,
                        diet_name_1_3,
                        diet_description_1_1,
                        diet_description_1_2,
                        diet_description_1_3,
                        workout_name_1_1,
                        workout_name_1_2,
                        workout_name_1_3,
                        workout_description_1_1,
                        workout_description_1_2,
                        workout_description_1_3,
                        medication_name_1_1,
                        medication_name_1_2,
                        medication_name_1_3,
                        medication_description_1_1,
                        medication_description_1_2,
                        medication_description_1_3,
                        diet_name_2_1,
                        diet_name_2_2,
                        diet_name_2_3,
                        diet_description_2_1,
                        diet_description_2_2,
                        diet_description_2_3,
                        workout_name_2_1,
                        workout_name_2_2,
                        workout_name_2_3,
                        workout_description_2_1,
                        workout_description_2_2,
                        workout_description_2_3,
                        medication_name_2_1,
                        medication_name_2_2,
                        medication_name_2_3,
                        medication_description_2_1,
                        medication_description_2_2,
                        medication_description_2_3,
                        diet_name_3_1,
                        diet_name_3_2,
                        diet_name_3_3,
                        diet_description_3_1,
                        diet_description_3_2,
                        diet_description_3_3,
                        workout_name_3_1,
                        workout_name_3_2,
                        workout_name_3_3,
                        workout_description_3_1,
                        workout_description_3_2,
                        workout_description_3_3,
                        medication_name_3_1,
                        medication_name_3_2,
                        medication_name_3_3,
                        medication_description_3_1,
                        medication_description_3_2,
                        medication_description_3_3)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    values,
                )

                # print("Disease descriptions = ")
                # print(diseases_defn)
                # use fetchone() instead of fetchall()
                # sha_cursor.execute("SELECT * FROM predicted")
                sha_cursor.execute(
                    """SELECT id, diseases_name_1, diseases_name_2, diseases_name_3, diet_name_1_1, diet_name_1_2, diet_name_1_3, workout_name_1_1, workout_name_1_2, workout_name_1_3, diet_name_2_1, diet_name_2_2, diet_name_2_3, workout_name_2_1, workout_name_2_2, workout_name_2_3, diet_name_3_1, diet_name_3_2, diet_name_3_3, workout_name_3_1, workout_name_3_2, workout_name_3_3,medication_name_3_1, medication_name_3_2, medication_name_3_3 FROM average_predicted"""
                )
                records = sha_cursor.fetchall()
                print("Total rows for average_predicted: ", len(records))
                for row in records:
                    print(row)
            sha_database.commit()

        else:
            print("Failed")
    else:
        print("You are healthy")
        try:
            if flag:
                sha_cursor.execute(
                    """SELECT id FROM predicted ORDER BY id DESC LIMIT 1"""
                )
            else:
                sha_cursor.execute(
                    """SELECT id FROM average_predicted ORDER BY id DESC LIMIT 1"""
                )
            # print(sha_cursor.fetchone())
            last_id = sha_cursor.fetchone()[0]
        except:
            last_id = 1

        values = [
            (
                last_id,
                "You are healthy",
                "You are healthy",
                "You are healthy",
                "You are healthy",
                "You are healthy",
                "You are healthy",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
            )
        ]
        # Construct the SQL query dynamically
        if flag:
            sha_cursor.executemany(
                """INSERT INTO predicted (
                id,
                diseases_name_1,
                diseases_name_2,
                diseases_name_3,
                diseases_description_1,
                diseases_description_2,
                diseases_description_3,
                diet_name_1_1,
                diet_name_1_2,
                diet_name_1_3,
                diet_description_1_1,
                diet_description_1_2,
                diet_description_1_3,
                workout_name_1_1,
                workout_name_1_2,
                workout_name_1_3,
                workout_description_1_1,
                workout_description_1_2,
                workout_description_1_3,
                medication_name_1_1,
                medication_name_1_2,
                medication_name_1_3,
                medication_description_1_1,
                medication_description_1_2,
                medication_description_1_3,
                diet_name_2_1,
                diet_name_2_2,
                diet_name_2_3,
                diet_description_2_1,
                diet_description_2_2,
                diet_description_2_3,
                workout_name_2_1,
                workout_name_2_2,
                workout_name_2_3,
                workout_description_2_1,
                workout_description_2_2,
                workout_description_2_3,
                medication_name_2_1,
                medication_name_2_2,
                medication_name_2_3,
                medication_description_2_1,
                medication_description_2_2,
                medication_description_2_3,
                diet_name_3_1,
                diet_name_3_2,
                diet_name_3_3,
                diet_description_3_1,
                diet_description_3_2,
                diet_description_3_3,
                workout_name_3_1,
                workout_name_3_2,
                workout_name_3_3,
                workout_description_3_1,
                workout_description_3_2,
                workout_description_3_3,
                medication_name_3_1,
                medication_name_3_2,
                medication_name_3_3,
                medication_description_3_1,
                medication_description_3_2,
                medication_description_3_3)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                values,
            )
        else:
            sha_cursor.executemany(
                """INSERT INTO average_predicted (
                    id,
                    diseases_name_1,
                    diseases_name_2,
                    diseases_name_3,
                    diseases_description_1,
                    diseases_description_2,
                    diseases_description_3,
                    diet_name_1_1,
                    diet_name_1_2,
                    diet_name_1_3,
                    diet_description_1_1,
                    diet_description_1_2,
                    diet_description_1_3,
                    workout_name_1_1,
                    workout_name_1_2,
                    workout_name_1_3,
                    workout_description_1_1,
                    workout_description_1_2,
                    workout_description_1_3,
                    medication_name_1_1,
                    medication_name_1_2,
                    medication_name_1_3,
                    medication_description_1_1,
                    medication_description_1_2,
                    medication_description_1_3,
                    diet_name_2_1,
                    diet_name_2_2,
                    diet_name_2_3,
                    diet_description_2_1,
                    diet_description_2_2,
                    diet_description_2_3,
                    workout_name_2_1,
                    workout_name_2_2,
                    workout_name_2_3,
                    workout_description_2_1,
                    workout_description_2_2,
                    workout_description_2_3,
                    medication_name_2_1,
                    medication_name_2_2,
                    medication_name_2_3,
                    medication_description_2_1,
                    medication_description_2_2,
                    medication_description_2_3,
                    diet_name_3_1,
                    diet_name_3_2,
                    diet_name_3_3,
                    diet_description_3_1,
                    diet_description_3_2,
                    diet_description_3_3,
                    workout_name_3_1,
                    workout_name_3_2,
                    workout_name_3_3,
                    workout_description_3_1,
                    workout_description_3_2,
                    workout_description_3_3,
                    medication_name_3_1,
                    medication_name_3_2,
                    medication_name_3_3,
                    medication_description_3_1,
                    medication_description_3_2,
                    medication_description_3_3)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                values,
            )
        sha_database.commit()
    # sha_database.close()

    # print("Disease descriptions = ")
    # print(diseases_defn)
    # use fetchone() instead of fetchall()
    # sha_cursor.execute("SELECT * FROM predicted")
    # except Exception as e:
    #     print("An error occurred while  analyzing your health!", str(e))


# for i in range(0, 4):
# analyze_health(0, 3, 4)
# analyze_health(0, 5, 6)
# i = 1
# while i < 12:
# read_data(1, 0, 0)
# read_data(0, 1, 10)
#     i += 1

