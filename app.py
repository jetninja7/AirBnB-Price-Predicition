from flask import Flask, request, render_template
from src.Airbnb.pipelines.Prediction_Pipeline import CustomData, PredictPipeline

app = Flask(__name__)


def _normalize_form_value(field_name, value):
    if field_name == "room_type":
        return {
            "Shared Room": "Shared room",
            "Private Room": "Private room",
            "Entire Home/Apt": "Entire home/apt",
        }.get(value, value)

    if field_name == "cancellation_policy":
        return {
            "Flexible": "flexible",
            "Moderate": "moderate",
            "Strict": "strict",
            "Super strict": "super_strict_30",
            "Advanced Super Strict": "super_strict_60",
        }.get(value, value)

    if field_name == "cleaning_fee":
        return "True" if str(value) == "1" else "False"

    if field_name == "city":
        return {
            "New York": "NYC",
            "San Francisco": "SF",
            "Washington, D.C.": "DC",
            "Los Angeles": "LA",
        }.get(value, value)

    if field_name in {"host_has_profile_pic", "host_identity_verified", "instant_bookable"}:
        return "t" if str(value) == "1" else "f"

    return value

# Define the home route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            # Convert form values to the schema expected by the trained preprocessor
            data = CustomData(
                property_type=request.form.get("property_type"),
                room_type=_normalize_form_value("room_type", request.form.get("room_type")),
                amenities=int(request.form.get("amenities")),
                accommodates=int(request.form.get("accommodates")),
                bathrooms=int(request.form.get("bathrooms")),
                bed_type=request.form.get("bed_type"),
                cancellation_policy=_normalize_form_value("cancellation_policy", request.form.get("cancellation_policy")),
                cleaning_fee=_normalize_form_value("cleaning_fee", request.form.get("cleaning_fee")),
                city=_normalize_form_value("city", request.form.get("city")),
                host_has_profile_pic=_normalize_form_value("host_has_profile_pic", request.form.get("host_has_profile_pic")),
                host_identity_verified=_normalize_form_value("host_identity_verified", request.form.get("host_identity_verified")),
                host_response_rate=int(request.form.get("host_response_rate")),
                instant_bookable=_normalize_form_value("instant_bookable", request.form.get("instant_bookable")),
                latitude=float(request.form.get("latitude")),
                longitude=float(request.form.get("longitude")),
                number_of_reviews=int(request.form.get("number_of_reviews")),
                review_scores_rating=int(request.form.get("review_scores_rating")),
                bedrooms=int(request.form.get("bedrooms")),
                beds=int(request.form.get("beds"))
            )

            final_data = data.get_data_as_dataframe()

            # Make prediction
            predict_pipeline = PredictPipeline()
            pred = predict_pipeline.predict(final_data)
            result = round(pred[0], 2)
            return render_template("index.html", result=result)

        except Exception as e:
            # Handle exceptions gracefully
            error_message = f"Error during prediction: {str(e)}"
            return render_template("error.html", error_message=error_message)

    else:
        # Render the initial page
        return render_template("index.html")

# Execution begins
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
