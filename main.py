from flask import Flask, redirect, url_for, render_template, request
import read_health_data as read_health_data
import sqlite3
import gradio
import json

app = Flask(__name__)
app.config["TIMEOUT"] = None
database = sqlite3.connect("sha.db", check_same_thread=False)
cursor = database.cursor()


# read_health_data.read_data(1, 0, 0)
cursor.execute(
    "SELECT  HeartRate, HeartRateVariabilitySDNN, RespiratoryRate , OxygenSaturation, WristTemperature, BodyMass FROM measurements ORDER BY id DESC LIMIT 1"
)
records = cursor.fetchone()


@app.route("/", methods=["GET", "POST"])
def home():

    return render_template(
        "index.html",
        HeartRate=records[0],
        HeartRateVariabilitySDNN=records[1],
        RespiratoryRate=records[2],
        OxygenSaturation=records[3],
        WristTemperature=records[4],
        BodyMass=records[5],
    )


@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    return redirect("http://127.0.0.1:7860")


@app.route("/analytics", methods=["GET", "POST"])
def analytics():
    read_health_data.analyze_health(1, 0, 0)

    cursor.execute("""SELECT * FROM predicted ORDER BY id DESC LIMIT 1""")
    analytics = cursor.fetchone()
    column_names = cursor.description
    column_names = [column[0] for column in column_names]
    template_variables = {}
    for i in range(len(column_names)):
        template_variables[column_names[i]] = analytics[i]
    cursor.execute(
        """
    SELECT m.id, m.Date, m.Time, m.HeartRate, m.HeartRateVariabilitySDNN, m.RespiratoryRate, m.OxygenSaturation, m.WristTemperature, m.BodyMass, p.diseases_name_1, p.diseases_name_2, p.diseases_name_3
    FROM measurements m
    LEFT JOIN predicted p ON m.id = p.id    
    ORDER BY m.id DESC
    """
    )
    database = cursor.fetchall()
    return render_template("analytics.html", **template_variables, database=database,)


@app.route("/average_analytics", methods=["GET", "POST"])
def average_analytics():
    # if request.method == "POST":
    #     # code for handling POST requests
    #     pass

    # code for handling GET requests and rendering the template
    ids_str = request.form.get("ids")
    ids = json.loads(ids_str)
    checked_ids = list(ids)
    print("CHECKED IDs = ", checked_ids)
    read_health_data.analyze_health(0, checked_ids[1], checked_ids[0])
    cursor.execute("""SELECT * FROM average_predicted ORDER BY id DESC LIMIT 1""")
    analytics = cursor.fetchone()
    column_names = cursor.description
    column_names = [column[0] for column in column_names]
    template_variables = {}
    for i in range(len(column_names)):
        template_variables[column_names[i]] = analytics[i]
    cursor.execute(
        """
        SELECT m.id, m.Date, m.Time, m.HeartRate, m.HeartRateVariabilitySDNN, m.RespiratoryRate, m.OxygenSaturation, m.WristTemperature, m.BodyMass, p.diseases_name_1, p.diseases_name_2, p.diseases_name_3
        FROM average m
        LEFT JOIN average_predicted p ON m.id = p.id    
        WHERE m.id IN ({})    
        ORDER BY m.id DESC
        """.format(
            ",".join("?" for _ in checked_ids)
        ),
        checked_ids,
    )
    database = cursor.fetchall()
    print("DONE!!!")
    return render_template(
        "average_analytics1.html",
        checked_ids=checked_ids,
        **template_variables,
        database=database,
    )


# @app.route("/average_analytics", methods=["GET", "POST"])
# def average_analytics():
#     # if request.method == "POST":
#     #     # code for handling POST requests
#     #     pass

#     # code for handling GET requests and rendering the template
#     ids_str = request.form.get("ids")
#     ids = json.loads(ids_str)
#     checked_ids = list(ids)
#     print("CHECKED IDs = ", checked_ids)
#     # read_health_data.analyze_health(0, checked_ids[1], checked_ids[0])
#     cursor.execute("""SELECT * FROM average_predicted ORDER BY id DESC LIMIT 1""")
#     analytics = cursor.fetchone()
#     column_names = cursor.description
#     column_names = [column[0] for column in column_names]
#     template_variables = {}
#     for i in range(len(column_names)):
#         template_variables[column_names[i]] = analytics[i]
#     cursor.execute(
#         """
#         SELECT m.id, m.Date, m.Time, m.HeartRate, m.HeartRateVariabilitySDNN, m.RespiratoryRate, m.OxygenSaturation, m.WristTemperature, m.BodyMass, p.diseases_name_1, p.diseases_name_2, p.diseases_name_3
#         FROM average m
#         LEFT JOIN average_predicted p ON m.id = p.id
#         WHERE m.id IN ({})
#         ORDER BY m.id DESC
#         """.format(
#             ",".join("?" for _ in checked_ids)
#         ),
#         checked_ids,
#     )
#     database = cursor.fetchall()
#     print("DONE!!!")
#     return render_template(
#         "average_analytics1.html",
#         checked_ids=checked_ids,
#         **template_variables,
#         database=database,
#     )


@app.route("/logs", methods=["GET", "POST"])
def logs():
    cursor.execute("""SELECT * FROM average_predicted ORDER BY id DESC LIMIT 1""")
    analytics = cursor.fetchone()
    column_names = cursor.description
    column_names = [column[0] for column in column_names]
    template_variables = {}
    for i in range(len(column_names)):
        template_variables[column_names[i]] = analytics[i]
    cursor.execute(
        """
    SELECT m.id, m.start_id, m.end_id, m.Date, m.Time, m.HeartRate, m.HeartRateVariabilitySDNN, m.RespiratoryRate, m.OxygenSaturation, m.WristTemperature, m.BodyMass, p.diseases_name_1, p.diseases_name_2, p.diseases_name_3,
                    p.diseases_description_1,
                    p.diseases_description_2,
                    p.diseases_description_3,
                    p.diet_name_1_1,
                    p.diet_name_1_2,
                    p.diet_name_1_3,
                    p.diet_description_1_1,
                    p.diet_description_1_2,
                    p.diet_description_1_3,
                    p.workout_name_1_1,
                    p.workout_name_1_2,
                    p.workout_name_1_3,
                    p.workout_description_1_1,
                    p.workout_description_1_2,
                    p.workout_description_1_3,
                    p.medication_name_1_1,
                    p.medication_name_1_2,
                    p.medication_name_1_3,
                    p.medication_description_1_1,
                    p.medication_description_1_2,
                    p.medication_description_1_3,
                    p.diet_name_2_1,
                    p.diet_name_2_2,
                    p.diet_name_2_3,
                    p.diet_description_2_1,
                    p.diet_description_2_2,
                    p.diet_description_2_3,
                    p.workout_name_2_1,
                    p.workout_name_2_2,
                    p.workout_name_2_3,
                    p.workout_description_2_1,
                    p.workout_description_2_2,
                    p.workout_description_2_3,
                    p.medication_name_2_1,
                    p.medication_name_2_2,
                    p.medication_name_2_3,
                    p.medication_description_2_1,
                    p.medication_description_2_2,
                    p.medication_description_2_3,
                    p.diet_name_3_1,
                    p.diet_name_3_2,
                    p.diet_name_3_3,
                    p.diet_description_3_1,
                    p.diet_description_3_2,
                    p.diet_description_3_3,
                    p.workout_name_3_1,
                    p.workout_name_3_2,
                    p.workout_name_3_3,
                    p.workout_description_3_1,
                    p.workout_description_3_2,
                    p.workout_description_3_3,
                    p.medication_name_3_1,
                    p.medication_name_3_2,
                    p.medication_name_3_3,
                    p.medication_description_3_1,
                    p.medication_description_3_2,
                    p.medication_description_3_3
    FROM average m
    LEFT JOIN average_predicted p ON m.id = p.id    
    ORDER BY m.id DESC
    """
    )
    average_database = cursor.fetchall()
    cursor.execute(
        """
        SELECT m.id, m.Date, m.Time, m.HeartRate, m.HeartRateVariabilitySDNN, m.RespiratoryRate, m.OxygenSaturation, m.WristTemperature, m.BodyMass, p.diseases_name_1, p.diseases_name_2, p.diseases_name_3,
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
                    medication_description_3_3
        FROM measurements m
        LEFT JOIN predicted p ON m.id = p.id    
        ORDER BY m.id DESC
        """
    )
    database = cursor.fetchall()
    return render_template(
        "logs.html",
        **template_variables,
        average_database=average_database,
        database=database,
    )


if __name__ == "__main__":
    app.run(debug=True,)
    database.commit()
    database.close()

