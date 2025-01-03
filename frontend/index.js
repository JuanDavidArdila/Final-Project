//var map = L.map('map').setView([51.505, -0.09], 13); // Set the initial view to London, UK
//var map = L.map('map').setView([4.7110, -74.0721], 13); // Set the initial view to Bogotá, Colombia
var map = L.map('map').setView([10.9800, -74.8000], 13); // Set the initial view to Barranquilla, Colombia
var mapClickable = true; // Variable to track if map is clickable
var polylines = [];
var markers = {};



// Add a tile layer (map tiles) to the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' // Attribution for the map tiles
}).addTo(map);

// Reference to the coordinates div
var coordinatesDiv = document.getElementById('coordinates');

// Event listener for click events on the map

map.on('click', function(event) {
    event.originalEvent.preventDefault()
    if (!mapClickable){ 
        alert("Please fill in all building characteristics.");
        return; // Do nothing if map is not clickable
    }
    var lat = event.latlng.lat;
    var lng = event.latlng.lng;

    var coordinatesPara = document.createElement('p');
    coordinatesPara.textContent = 'Clicked coordinates: ' + lat + ', ' + lng;

    // Append the paragraph element to the coordinates div
    coordinatesDiv.appendChild(coordinatesPara);
    
    var buildingInfo = {
        buildingId: Date.now(), // Unique ID for each marker
        latitude: lat,
        longitude: lng
    };

    var marker = L.marker([lat, lng], {icon: blueIcon, buildingId: buildingInfo.buildingId}).addTo(map);
    //markers.push(marker);
    markers[buildingInfo.buildingId] = marker; // Store the marker with its ID
    var popupContent = "<b>Add Building Characteristics</b><br>";
    popupContent += "Id " + buildingInfo.buildingId + "<br>";
    popupContent += "<label for='blueInletTemperature_" + buildingInfo.buildingId + "'>Inlet Temp:</label> <input type='number' id='blueInletTemperature_" + buildingInfo.buildingId + "'> [°C]<br>";
    popupContent += "<label for='blueDeltaT_" + buildingInfo.buildingId + "'>Delta t:</label> <input type='number' id='blueDeltaT_" + buildingInfo.buildingId + "'> [°C]<br>";
    popupContent += "<label for='blueTypeConnection_" + buildingInfo.buildingId + "'>Type of connection:</label> <input type='text' id='blueTypeConnection_" + buildingInfo.buildingId + "'><br>";
    popupContent += "<button type='button' onclick='addBuildingData(" + JSON.stringify(buildingInfo) + ", \"blue\")'>Save</button>";

    marker.bindPopup(popupContent).openPopup();

    // Disable map click events while data is being entered
    mapClickable = false;
});


// Event listener for contextmenu events on the map (right-clicks)
map.on('contextmenu', function(event) {
    event.originalEvent.preventDefault()
    if (!mapClickable){ 
        alert("Please fill in all building characteristics.");
        return; // Do nothing if map is not clickable
    }
    // Retrieve the coordinates of the clicked point
    var lat = event.latlng.lat;
    var lng = event.latlng.lng;

    // Create a new paragraph element to display the coordinates
    var coordinatesPara = document.createElement('p');
    coordinatesPara.textContent = 'Right-clicked coordinates: ' + lat + ', ' + lng;

    // Append the paragraph element to the coordinates div
    coordinatesDiv.appendChild(coordinatesPara);

    var buildingInfo = {
        buildingId: Date.now(), // Unique ID for each marker
        latitude: lat,
        longitude: lng
    };

    // Create a marker at the clicked location with a red icon
    var marker = L.marker([lat, lng], {icon: redIcon, buildingId: buildingInfo.buildingId}).addTo(map);
    //markers.push(marker);
    markers[buildingInfo.buildingId] = marker; // Store the marker with its ID
    var popupContent = "<b>Add Building Characteristics</b><br>";
    popupContent += "Id " + buildingInfo.buildingId + "<br>";
    popupContent += "<label for='redExitTemperature_" + buildingInfo.buildingId + "'>Exit Temperature:</label> <input type='number' id='redExitTemperature_" + buildingInfo.buildingId + "'> [°C]<br>";
    popupContent += "<label for='redFlowRate_" + buildingInfo.buildingId + "'>Flow Rate:</label> <input type='number' id='redFlowRate_" + buildingInfo.buildingId + "'> [m<sup>3</sup>/s]<br>";
    popupContent += "<button type='button' onclick='addBuildingData(" + JSON.stringify(buildingInfo) + ", \"red\")'>Save</button>";

    marker.bindPopup(popupContent).openPopup().addTo(map);

    

    // Disable map click events while data is being entered
    mapClickable = false;
});



function addBuildingData(buildingInfo, color) {
    var buildingId;  
    var type; 
    var latitude; 
    var longitude; 
    var inletTemperature;
    var exitTemperature;
    var connectionType;

    if (color === "blue") {
        buildingId = buildingInfo.buildingId ;     
        type="blue";
        latitude=buildingInfo.latitude;
        longitude=buildingInfo.longitude;
        inletTemperature=parseFloat(document.getElementById('blueInletTemperature_' + buildingInfo.buildingId).value);
        DeltaT=parseFloat(document.getElementById('blueDeltaT_' + buildingInfo.buildingId).value);
        connectionType=document.getElementById('blueTypeConnection_' + buildingInfo.buildingId);
    
        // Check if inputs are filled
        if (!inletTemperature || !DeltaT || !connectionType) {
            alert("Please fill in all building characteristics.");
            return;
        }

        if (!/^(Ground|Air|Inside)$/i.test(connectionType.value)) {
            alert("The type of connection only could be 'Ground', 'Air', or 'Inside'.");
            return;
        }

        const building = {
            buildingId:buildingId,
            type:type,
            latitude:latitude,
            longitude:longitude,
            inletTemperature: inletTemperature,
            DeltaT: DeltaT,
            connectionType: connectionType.value
        };

        console.log(building)

        const url ="http://127.0.0.1:5001/create_blue_building";

        const options={                
            method:"POST",
            headers:{                                 
               "Content-Type": "application/json"     /*We are specyfing we are about to submit JSON data*/  
            },
            body: JSON.stringify(building)
        }

        fetchData = async (url, options) => {
            
            try {
                const response = await fetch(url, options);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                console.log('Data sent successfully:', data);
                // Close the popup after saving
                // Re-enable map click events after data is saved
            } catch (error) {
                console.error('Error sending data:', error.message);
                // Handle error (e.g., show error message to the user)
            }
        };
        
        // Inside addBuildingData function
        fetchData(url, options);

        // Close the popup after saving
        map.closePopup();

        // Re-enable map click events after data is saved
        mapClickable = true;

    } else if (color === "red") {
        buildingId = buildingInfo.buildingId ;     
        type="red";
        latitude=buildingInfo.latitude;
        longitude=buildingInfo.longitude;
        flowRate=parseFloat(document.getElementById('redFlowRate_' + buildingInfo.buildingId).value);
        exitTemperature=parseFloat(document.getElementById('redExitTemperature_' + buildingInfo.buildingId).value);
        // Check if inputs are filled
        if (!flowRate || !exitTemperature) {
            alert("Please fill in all building characteristics.");
            return;
        }

        const building = {
            buildingId:buildingId,
            type:type,
            latitude:latitude,
            longitude:longitude,
            flowRate: flowRate,
            exitTemperature: exitTemperature
        };
        
        const url ="http://127.0.0.1:5001/create_red_building";

        const options={                
            method:"POST",
            headers:{                                 
               "Content-Type": "application/json"     /*We are specyfing we are about to submit JSON data*/  
            },
            body: JSON.stringify(building)
        }

        fetchData = async (url, options) => {
            
            try {
                const response = await fetch(url, options);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                console.log('Data sent successfully:', data);
                // Close the popup after saving
                // Re-enable map click events after data is saved
            } catch (error) {
                console.error('Error sending data:', error.message);
                // Handle error (e.g., show error message to the user)
            }
        };
        
        // Inside addBuildingData function
        fetchData(url, options);

        // Close the popup after saving
        map.closePopup();

        // Re-enable map click events after data is saved
        mapClickable = true;
    }
}


var blueIcon = L.icon({
    iconUrl: '/frontend/Icons/blue_marker_icon.png',
    iconSize: [41, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34]
});

var redIcon = L.icon({
    iconUrl: '/frontend/Icons/marker_red_icon.png',
    iconSize: [41, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34]
});



document.getElementById('clearCoordinates').addEventListener('click', async function() {
    // Remove polylines from the map
    polylines.forEach(function (item) {
        map.removeLayer(item);
    });

    polylines = [];

    for (const id in markers) {
        if (markers.hasOwnProperty(id)) {
            map.removeLayer(markers[id]);
        }
    }
    
    markers = {};

    var totalDistanceDiv = document.getElementById('total-distance');
    totalDistanceDiv.innerHTML = `<strong>Total Distance:</strong> 0`;

    // Send DELETE request to delete buildings
    const url = "http://127.0.0.1:5001/delete_buildings";
    const options = {
        method: "DELETE"
    };

    try {
        const response = await fetch(url, options);
        if (response.status === 200) {
            console.log("Buildings deleted successfully");
            // Provide feedback to the user (e.g., show a confirmation message)
        } else {
            console.error("Failed to delete buildings");
            // Provide feedback to the user (e.g., show an error message)
        }
    } catch (error) {
        console.error("Error deleting buildings:", error);
        // Provide feedback to the user (e.g., show an error message)
    }
});


//Multi-action button
{

    //Hide all lists when clicking elsewhere on the page
    document.addEventListener("click", e => {
        const keepOpen= (
            e.target.matches(".mab__list")
            || e.target.matches(".mab__button--menu")
            || e.target.closest(".mab__button--menu")
        );
        if(keepOpen) return;
        

        document.querySelectorAll(".mab__list").forEach(list => {
            list.classList.remove("mab__list--visible");
        });
    });
    
    //Enable all menu buttons
    document.querySelectorAll(".mab").forEach(multiaction=>{
        const menuButton=multiaction.querySelector(".mab__button--menu");
        const list=multiaction.querySelector(".mab__list");
        menuButton.addEventListener("click", () =>{
            list.classList.toggle("mab__list--visible");
        });
    });

}


document.getElementById('calculateButton').addEventListener('click', async function() {
    // Get data from textboxes
    var internalDiameter=parseFloat(document.getElementById('textbox1').value);
    var pipeThickness=parseFloat(document.getElementById('textbox2').value);
    var pipeConductivity=parseFloat(document.getElementById('textbox3').value);
    var insulationThickness=parseFloat(document.getElementById('textbox4').value);
    var insulationConductivity= parseFloat(document.getElementById('textbox5').value);
    var emissivity= parseFloat(document.getElementById('textbox6').value);
    var ambientTemperature= parseFloat(document.getElementById('textbox7').value);
    var groundTemperature= parseFloat(document.getElementById('textbox8').value);
    var airVelocity= parseFloat(document.getElementById('textbox9').value);
    var irradiance= parseFloat(document.getElementById('textbox10').value);
    
    if (isNaN(internalDiameter) || isNaN(pipeThickness) || isNaN(pipeConductivity) || isNaN(insulationThickness) || isNaN(insulationConductivity) || isNaN(emissivity) || isNaN(ambientTemperature) || isNaN(groundTemperature) || isNaN(airVelocity) | isNaN(irradiance)) {
        alert("Please fill in all pipe characteristics.");
        return;
    }
    
    var textBoxData = {
        internalDiameter: internalDiameter,
        pipeThickness: pipeThickness,
        pipeConductivity: pipeConductivity,
        insulationThickness: insulationThickness,
        insulationConductivity: insulationConductivity,
        emissivity: emissivity,
        ambientTemperature: ambientTemperature,
        groundTemperature: groundTemperature,
        airVelocity: airVelocity,
        irradiance:irradiance
    };

    
    // Send POST request to Flask backend
    const url = "http://127.0.0.1:5001/calculate_clusters"; // Adjust URL accordingly

    try {
        // Send POST request to Flask backend
        const calculateResponse = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(textBoxData)
        });

        if (!calculateResponse.ok) {
            const errorMessage = await calculateResponse.json();
            console.error("Failed to calculate clusters:", errorMessage.message);
            alert(`Error: ${errorMessage.message}`);
            return;
        }

        console.log("Calculation successful");

        // Fetch clusters data after calculation
        const clustersResponse = await fetch(url, { method: "GET" });

        if (!clustersResponse.ok) {
            const errorMessage = await clustersResponse.json();
            console.error("Failed to fetch clusters data:", errorMessage.message);
            alert(`Error: ${errorMessage.message}`);
            return;
        }

        const clustersData = await clustersResponse.json();
        console.log("Clusters data received:", clustersData);
        Connection(clustersData.clusters)
        // Handle clusters data as needed (e.g., display on the UI)
        
    } catch (error) {
        console.error("Error:", error);
        alert(`Error: ${error.message}`);
    }

    
});


function Connection(buildinggroups) {
    if (!Array.isArray(buildinggroups)) {
        console.error("buildinggroups is not an array:", buildinggroups);
        return;
    }
    var connections=[];
    var totaldistance=0;
    for (const x of buildinggroups){
        var first_lat=parseFloat(x.firstbuilding_latitude);
        var first_long=parseFloat(x.firstbuilding_longitude);
        var second_lat=parseFloat(x.secondbuilding_latitude);
        var second_long=parseFloat(x.secondbuilding_longitude);
        var distance=parseFloat(x.distance);
        totaldistance+=distance
        connections.push([[first_lat,first_long],[second_lat,second_long]]);
    }
    console.log("Connections:", connections);
    //Draw all the lines
    for (var i = 0; i < connections.length; i++){
        var lineCoordinates =connections[i];
        // Create a polyline with the coordinates and set color to green
        var lyne =L.polyline(lineCoordinates, {color: 'green'}).addTo(map);
        polylines.push(lyne);
    }
    console.log("Total distance:", totaldistance);
    var totalDistanceDiv = document.getElementById('total-distance');
    totalDistanceDiv.innerHTML = `<strong>Total Distance:</strong> ${totaldistance.toFixed(2)} m`;
}



document.getElementById('heating').addEventListener('click', async function() {

    console.log("Calculating Temperatures ... ");

    const url = "http://127.0.0.1:5001/get_hot_temperatures"; // Adjust URL accordingly
    
    try {

        const clustersResponse = await fetch(url, { method: "GET" });
        if (!clustersResponse.ok) {
            const errorMessage = await clustersResponse.json();
            console.error("Failed to fetch clusters data:", errorMessage.message);
            alert(`Error: ${errorMessage.message}`);
            return;
        }

        const Data = await clustersResponse.json();
        console.log("Temperatures received:", Data);
        // Handle clusters data as needed (e.g., display on the UI)

        const temperaturesData = Data["Hot Temperatures"];
        console.log("Temperatures extracted:", temperaturesData);

        if (Array.isArray(temperaturesData)) {
            temperaturesData.forEach(entry => {

                var marker = markers[entry.building_id]; // Find the marker by building_id

                if (marker) {
                    var popupContent = "Inlet Temperature: " + entry.inlet_temperature + "°C" +
                                       "<br>Exit Temperature: " + entry.exit_temperature + "°C";
                    marker.bindPopup(popupContent).openPopup(); // Bind popup and open it
                } else {
                    console.warn(`Marker with building_id ${entry.building_id} not found`);
                }
            });
        } else {
            console.error("Data is not an array:", temperaturesData);
        }

    } catch (error) {
        console.error("Error:", error);
        alert(`Error: ${error.message}`);
    }

});
    
    
document.getElementById('cooling').addEventListener('click', async function() {

    console.log("Calculating Temperatures ... ");

    const url = "http://127.0.0.1:5001/get_cold_temperatures"; // Adjust URL accordingly
    
    try {

        const clustersResponse = await fetch(url, { method: "GET" });
        if (!clustersResponse.ok) {
            const errorMessage = await clustersResponse.json();
            console.error("Failed to fetch data:", errorMessage.message);
            alert(`Error: ${errorMessage.message}`);
            return;
        }

        const Data = await clustersResponse.json();
        console.log("Temperatures received:", Data);

        const temperaturesData = Data["Cold Temperatures"];
        console.log("Temperatures extracted:", temperaturesData);

        if (Array.isArray(temperaturesData)) {
            temperaturesData.forEach(entry => {

                var marker = markers[entry.building_id]; // Find the marker by building_id

                if (marker) {
                    var popupContent = "Inlet Temperature: " + entry.inlet_temperature + "°C" +
                                       "<br>Exit Temperature: " + entry.exit_temperature +"°C" ;
                    marker.bindPopup(popupContent).openPopup(); // Bind popup and open it
                } else {
                    console.warn(`Marker with building_id ${entry.building_id} not found`);
                }
            });
        } else {
            console.error("Data is not an array:", temperaturesData);
        }

    } catch (error) {
        console.error("Error:", error);
        alert(`Error: ${error.message}`);
    }

});

