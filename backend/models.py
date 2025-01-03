from config import db


class BlueBuilding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buildingId =db.Column(db.Float, unique=True, nullable=False)       ##I have to be careful, Could id be the number that i want?
    type=db.Column(db.String(80), unique=False, nullable=False)
    latitude=db.Column(db.Float, unique=True, nullable=False)
    longitude=db.Column(db.Float, unique=True, nullable=False)
    inletTemperature=db.Column(db.Float, unique=False, nullable=False)
    DeltaT=db.Column(db.Float, unique=False, nullable=False)
    connectionType=db.Column(db.String(150), unique=False, nullable=False)
    BR_buildings=db.relationship('BRBuildingsm', backref='blue_building', lazy=True)
    BlueBuildingDistances=db.relationship('BlueBuildingDistance', backref='blue_building', lazy=True)
     

    def to_json(self):
        return{
            "id": self.id,
            "buildingId":self.buildingId,
            "type": self.type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "inletTemperature": self.inletTemperature,
            "DeltaT": self.DeltaT,
            "connectionType": self.connectionType,
        }

class RedBuilding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buildingId =db.Column(db.Float, unique=True, nullable=False)
    type=db.Column(db.String(80), unique=False, nullable=False)
    latitude=db.Column(db.Float, unique=True, nullable=False)
    longitude=db.Column(db.Float, unique=True, nullable=False)
    flowRate=db.Column(db.Float, unique=False, nullable=False)
    exitTemperature=db.Column(db.Float, unique=False, nullable=False) 
    BR_buildings=db.relationship('BRBuildingsm', backref='red_building', lazy=True)
    Connecttion=db.relationship('Connecttions', backref='red_building', lazy=True)
    def to_json(self):
        return{
            "id": self.id,
            "buildingId":self.buildingId,
            "type": self.type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "exitTemperature": self.exitTemperature,
            "flowRate": self.flowRate,
        }
    
class FixedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internalDiameter = db.Column(db.Float, nullable=False)
    pipeThickness = db.Column(db.Float, nullable=False)
    pipeConductivity = db.Column(db.Float)
    insulationThickness = db.Column(db.Float)
    insulationConductivity = db.Column(db.Float)
    emissivity = db.Column(db.Float)
    ambientTemperature = db.Column(db.Float)
    groundTemperature = db.Column(db.Float)
    airVelocity = db.Column(db.Float)
    irradiance = db.Column(db.Float)

    def to_json(self):
        return {
            "id": self.id,
            "internalDiameter": self.internalDiameter,
            "pipeThickness": self.pipeThickness,
            "pipeConductivity": self.pipeConductivity,
            "insulationThickness": self.insulationThickness,
            "insulationConductivity": self.insulationConductivity,
            "emissivity": self.emissivity,
            "ambientTemperature": self.ambientTemperature,
            "groundTemperature": self.groundTemperature,
            "airVelocity": self.airVelocity,
            "irradiance": self.irradiance
        }
    

class BlueBuildingDistance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building1_id = db.Column(db.Float,db.ForeignKey('blue_building.buildingId'), nullable=False)
    latitude1=db.Column(db.Float, nullable=False)
    longitude1=db.Column(db.Float, nullable=False)
    building2_id = db.Column(db.Float, nullable=False)
    latitude2=db.Column(db.Float,nullable=False)
    longitude2=db.Column(db.Float,nullable=False)
    distance=db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "building1_id": self.building1_id,
            "latitude1": self.latitude1,
            "longitude1": self.longitude1,
            "building2_id": self.building2_id,
            "latitude2": self.latitude2,
            "longitude2": self.longitude2,
            "distance": self.distance
        }



    
#Regarding to Buildingdistance as soon as the flask post is made, it will be created

class BRBuildingsm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bbuilding_id = db.Column(db.Float,db.ForeignKey('blue_building.buildingId') ,nullable=False)
    blatitude=db.Column(db.Float, nullable=False)
    blongitude=db.Column(db.Float, nullable=False)
    rbuilding_id = db.Column(db.Float,db.ForeignKey('red_building.buildingId'), nullable=False)
    rlatitude=db.Column(db.Float,nullable=False)
    rlongitude=db.Column(db.Float,nullable=False)
    distance=db.Column(db.Float, nullable=False)
    def to_json(self):
        return {
            "id": self.id,
            "bbuilding_id": self.bbuilding_id,
            "blatitude": self.blatitude,
            "blongitude": self.blongitude,
            "rbuilding_id": self.rbuilding_id,
            "rlatitude": self.rlatitude,
            "rlongitude": self.rlongitude,
            "distance": self.distance
        }





class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rbuilding_id = db.Column(db.Float,db.ForeignKey('red_building.buildingId'), nullable=False)
    rlatitude=db.Column(db.Float,nullable=False)
    rlongitude=db.Column(db.Float,nullable=False)
    bbuilding_id = db.Column(db.Float,db.ForeignKey('blue_building.buildingId') ,nullable=False)
    blatitude=db.Column(db.Float, nullable=False)
    blongitude=db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "rbuilding_id": self.rbuilding_id,
            "rlatitude": self.rlatitude,
            "rlongitude": self.rlongitude,
            "bbuilding_id": self.bbuilding_id,
            "blatitude": self.blatitude,
            "blongitude": self.blongitude,
            "distance": self.distance
        }
    

class Connecttions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mainbuilding_id=db.Column(db.Float,db.ForeignKey('red_building.buildingId'), nullable=False)
    firstbuilding_id=db.Column(db.Float, nullable=False)
    firstbuilding_type = db.Column(db.String(10), nullable=False)  # "blue" or "red"
    firstbuilding_latitude = db.Column(db.Float, nullable=False)
    firstbuilding_longitude = db.Column(db.Float, nullable=False)
    secondbuilding_id=db.Column(db.Float, nullable=False)
    secondbuilding_type = db.Column(db.String(10), nullable=False)  # "blue" or "red"
    secondbuilding_latitude = db.Column(db.Float, nullable=False)
    secondbuilding_longitude = db.Column(db.Float, nullable=False)
    distance=db.Column(db.Float, nullable=False)
    def to_json(self):
        return {
            "id": self.id,
            "firstbuilding_latitude": self.firstbuilding_latitude,
            "firstbuilding_longitude": self.firstbuilding_longitude,
            "secondbuilding_latitude": self.secondbuilding_latitude,
            "secondbuilding_longitude": self.secondbuilding_longitude,
            "distance":self.distance
        }
    

class Hot_Temperatures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id=db.Column(db.Float, nullable=False)
    building_latitude=db.Column(db.Float, nullable=False)
    building_longitude=db.Column(db.Float, nullable=False)
    inlet_temperature=db.Column(db.Float, nullable=False)
    exit_temperature=db.Column(db.Float, nullable=False)
    def to_json(self):
        return {
            "id": self.id,
            "building_id": self.building_id,
            "building_latitude": self.building_latitude,
            "building_longitude": self.building_longitude,
            "inlet_temperature": self.inlet_temperature,
            "exit_temperature":self.exit_temperature
        }


class Cold_Temperatures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id=db.Column(db.Float, nullable=False)
    building_latitude=db.Column(db.Float, nullable=False)
    building_longitude=db.Column(db.Float, nullable=False)
    inlet_temperature=db.Column(db.Float, nullable=False)
    exit_temperature=db.Column(db.Float, nullable=False)
    def to_json(self):
        return {
            "id": self.id,
            "building_id": self.building_id,
            "building_latitude": self.building_latitude,
            "building_longitude": self.building_longitude,
            "inlet_temperature": self.inlet_temperature,
            "exit_temperature":self.exit_temperature
        }