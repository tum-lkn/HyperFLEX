var defaultLinkBW = 1000;

var USER = 1;
var VSDN_ID = null;
var PHY_NW;
var TEN_NW;


	
$(function () {
    // Create the physical network first
    var options = {
        nodeTypes: nodeTypes,
        edgeStyle: edgeStyle,
        network_options: network_options,
        container: "network-container"
    };
    PHY_NW = new Network(options);


    // Create the tenant network
    var options = {
        nodeTypes: nodeTypes,
        edgeStyle: edgeStyle,
        network_options: network_options,
        container: "t_network-container"
    };
    TEN_NW = new Network(options);

    // Set Edges datarate to the default one
    TEN_NW.edges.on("add", function (ev, properties) {
        var edgeID = properties.items[0];
        var params = {
            id: edgeID            
        };        
        // Set edge bw
        params.datarate = params.datarate || parseInt(defaultLinkBW);
        TEN_NW.edges.update(params);
    });
    
    // Fetch physical topo from server
    fetchPhysicalTopo(USER,PHY_NW);
    
    // Fit network on startup
    setTimeout(function(){
            PHY_NW.network.fit();
            PHY_NW.network.redraw();  
            TEN_NW.network.fit();
            TEN_NW.network.redraw();
    }, 500);    
    
	
});

// Fetch the physical topology from the server
function fetchPhysicalTopo(user,network_obj) {	
	hyperflexGetPhysicalTopo(function(result){
        network_obj.clear();
		var data = JSON.parse(result)["data"];
		network_obj.readNetwork(data);           
	},[user]);
}

// Send the VSDN request to the server
// 		On success: Server returns vsdn_id
//		On Error: Server returns error message
function requestVSDN(user,data,network_obj) {
    // Prepare our VSDN data	
    var senddata = {
            'user': user,
            'data': data            
    };
    var sendstring = JSON.stringify(senddata);
    console.log(JSON.stringify(senddata, null, 2));              
    // Open loading popup
    $('.requestVSDNPopup').modal('toggle');
    
    // artificial sleep time of 3 seconds
    setTimeout(function() { 
        // Send request to server
        hyperflexRequestVSDN(
            // On success
            function (result) {
                console.log(result);
                // Close the requesting popup
                $('.requestVSDNPopup').modal('toggle');
                var data = JSON.parse(result);
                console.log(data);
                // When we get a positive response from the server
                if ("data" in data) {      
                    // Open Request successful popup
                    $('.requestVSDNSuccess').modal('toggle');

                    var data = data["data"];

                    // Set global VSDN_ID to the one we get as response
                    VSDN_ID = parseInt(data);

                    // Clear our constructed network                                
                    TEN_NW.clear();

                    // Get the network that's actually on the server                                
                    fetchVSDN(user, VSDN_ID, TEN_NW);
                }
                else if ("error" in data) {
                    // Open error popup
                    $('.requestVSDNError').modal('toggle');
                    // Display error msg
                    $('.requestVSDNError').find("#msg").html(data["error"]);
                }
            },
            [sendstring],
            // On error
            function (error) {
                console.log("Server error!",error);
                $('.requestVSDNPopup').modal('toggle');
            }
        );},
    1500);
}

// Send VSDN Update Request to server
function updateVSDN(user,data,network_obj) {
	// Change this!
	// We are only updating the vsdn header
	data["user"] = USER;
	data.edges = [];
	data.nodes = [];
	
	console.log(JSON.stringify(data, null, 2));

	// Send request to server
	hyperflexUpdateVSDN(
		// On success
		function (result) {
                    var parsed = JSON.parse(result);
                    if(parsed["data"] === "success"){
                        console.info("Update successful!");
                        fetchVSDN(user, VSDN_ID, TEN_NW);
                    }
		},
		[JSON.stringify(data)],
		// On error
		function (error) {
			console.log(error);
		}
	);
}
