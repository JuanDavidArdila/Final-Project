from functions import TforheatingInside, calculate_and_store_distances, clusters, get_building_groups, hot_temperatures, cold_temperatures
from config import app, db  # Import the app instance from config.py
from flask import request, jsonify
# Import your models here
from models import BlueBuilding, RedBuilding, FixedData, BRBuildingsm, BlueBuildingDistance, Cluster, Connecttions,Cold_Temperatures,Hot_Temperatures


# I have to make 3 kinds of requests. Post a new building, delete buildings, calculate button 1,2,3.
#Th server is in which all the data is stored

@app.route("/create_blue_building", methods=["POST"])
def create_blue_building():
    buildingId =request.json.get("buildingId")     
    type=request.json.get("type") 
    latitude=request.json.get("latitude") 
    longitude=request.json.get("longitude") 
    inletTemperature=request.json.get("inletTemperature") 
    DeltaT=request.json.get("DeltaT") 
    connectionType=request.json.get("connectionType") 

    if not buildingId or not type or not latitude or not longitude or not inletTemperature or not DeltaT or not connectionType:
        return (jsonify({"message": "You must include a first name, last name and email"}),
                400,                
        )
    
    if not (isinstance(inletTemperature, (int, float)) and isinstance(DeltaT, (int, float))):
        return jsonify({"message": "Inlet temperature and exit temperature must be numerical values"}), 400
    
    new_bluebuilding=BlueBuilding(buildingId=buildingId, type=type, latitude=latitude, longitude=longitude, inletTemperature=inletTemperature, DeltaT=DeltaT, connectionType=connectionType)

    try:
        db.session.add(new_bluebuilding)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
    return jsonify({"message": "User created!"}), 201



@app.route("/create_red_building", methods=["POST"])
def create_red_building():
    buildingId =request.json.get("buildingId")     
    type=request.json.get("type")                                  ###When i click on the map it send this request with type already when the user right click the type is automatically filled
    latitude=request.json.get("latitude") 
    longitude=request.json.get("longitude") 
    flowRate=request.json.get("flowRate") 
    exitTemperature=request.json.get("exitTemperature") 

    if not buildingId or not type or not latitude or not longitude or not flowRate or not exitTemperature:
        return (jsonify({"message": "You must include a first name, last name and email"}),
                400,                
        )
    
    if not (isinstance(flowRate, (int, float)) and isinstance(exitTemperature, (int, float))):
        return jsonify({"message": "Inlet temperature and exit temperature must be numerical values"}), 400
    
    new_redbuilding=RedBuilding(buildingId=buildingId, type=type, latitude=latitude, longitude=longitude, flowRate=flowRate, exitTemperature=exitTemperature)

    try:
        db.session.add(new_redbuilding)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
    return jsonify({"message": "User created!"}), 201



@app.route("/delete_buildings", methods=["DELETE"])
def delete_buildings():
    try:
        # Delete all RedBuildings
        RedBuilding.query.delete()

        # Delete all BlueBuildings
        BlueBuilding.query.delete()

        FixedData.query.delete()

        BRBuildingsm.query.delete()

        BlueBuildingDistance.query.delete()

        Cluster.query.delete()

        Connecttions.query.delete()

        Hot_Temperatures.query.delete()

        Cold_Temperatures.query.delete()

        # Commit the changes to the database
        db.session.commit()

        return jsonify({"message": "All buildings deleted successfully."}), 200

    except Exception as e:
        # If an error occurs, rollback the session and return an error message
        db.session.rollback()
        return jsonify({"error": str(e)}), 500 

@app.route("/calculate_clusters", methods=["GET","POST"])
def calculate_clusters():
    if request.method == "POST":
    # Retrieve data from the POST request
        internalDiameter = request.json.get("internalDiameter")
        pipeThickness = request.json.get("pipeThickness")
        pipeConductivity = request.json.get("pipeConductivity")
        insulationThickness = request.json.get("insulationThickness")
        insulationConductivity = request.json.get("insulationConductivity")
        emissivity = request.json.get("emissivity")
        ambientTemperature = request.json.get("ambientTemperature")
        groundTemperature = request.json.get("groundTemperature")
        airVelocity = request.json.get("airVelocity")
        irradiance = request.json.get("irradiance")

        if not internalDiameter or not pipeThickness or not pipeConductivity or not insulationThickness or not insulationConductivity or not emissivity or not ambientTemperature or not groundTemperature or not airVelocity or not irradiance:
            return (jsonify({"message": "You must include all of the pipe parameter values"}),
                    400,                
            )
        
        if not all(isinstance(value, (int, float)) for value in [internalDiameter, pipeThickness, pipeConductivity, insulationThickness, insulationConductivity, emissivity, ambientTemperature, groundTemperature, airVelocity]):
            return jsonify({"message": "Pipe parameters must be numerical values"}), 400
        

        new_pipe_details=FixedData(internalDiameter =internalDiameter, pipeThickness=pipeThickness, pipeConductivity=pipeConductivity, insulationThickness=insulationThickness, insulationConductivity=insulationConductivity, emissivity=emissivity, ambientTemperature=ambientTemperature, groundTemperature=groundTemperature, airVelocity=airVelocity, irradiance=irradiance)

        try:
            db.session.add(new_pipe_details)
            db.session.commit()
        except Exception as e:
            return jsonify({"message": str(e)}), 400
        

        print("Calling calculate_and_store_distances()...")
        calculate_and_store_distances()
        print("Calling clusters()...")
        clusters()

        # Get building groups
        print("Calling get_building_groups()...")
        building_groups = get_building_groups()
        
        return jsonify({"message": "User created!", "building_groups": building_groups}), 201
    elif request.method == "GET":
        connections_data = Connecttions.query.all()
        connections_buildings= list(map(lambda x: x.to_json(), connections_data))
        return jsonify({"clusters": connections_buildings}), 200



@app.route("/get_hot_temperatures", methods=["GET"])
def get_hot_temperatures():

    hot_temperatures()
    hot_temperatures_data=Hot_Temperatures.query.all()
    hot=list(map(lambda x: x.to_json(), hot_temperatures_data))

    return jsonify({"Hot Temperatures": hot}), 200


@app.route("/get_cold_temperatures", methods=["GET"])
def get_cold_temperatures():

    cold_temperatures()
    cold_temperatures_data=Cold_Temperatures.query.all()
    cold=list(map(lambda x: x.to_json(), cold_temperatures_data))

    return jsonify({"Cold Temperatures": cold}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()   ##Go ahead and create all of te different models that we have define on our DataBase 
    # Run the Flask app in debug mode
    app.run(debug=True,port=5001)

