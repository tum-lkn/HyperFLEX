var USER = 2;
var PHY_NW;
var WSS;
$(function () {
    var options = {
        nodeTypes: nodeTypes,
        edgeStyle: edgeStyle,
        network_options: network_options,
        container: "network-container"
    };

    PHY_NW = new Network(options);
    // Fetch physical topo from server
    fetchPhysicalTopo(USER,PHY_NW); 
    
    // Fit network
    setTimeout(function(){
        PHY_NW.network.fit();
        PHY_NW.network.redraw();  
    }, 500);
    
});

    
$(function () {
    // WEBSOCKET
    WSS = new Websocket(WSS_IP, WSS_PORT);
    
    // Subscribe to vsdn_changed msg   
    // Topic, Callback function when msg is published
    WSS.subscribe("vsdn_changed",function(topic,data){
       
        var callback = function(data) {
            cpubar.clear();
            // Add vsdn to cpu bar
            for(var i = 0; i < data.length; i++){
                var vsdn_data = data[i];
                cpubar.add_vsdn(vsdn_data);
            }            
        };
        fetchAllVSDN(USER, PHY_NW, callback);
    });
    
    // Subscribe to topo_changed msg   
    // Topic, Callback function when msg is published
    WSS.subscribe("topo_changed",function(topic,data){
        // Clear the network first
        PHY_NW.clear(PHY_NW);
        // Get the physical topo from server
        fetchPhysicalTopo(USER,PHY_NW); 
        // Also retrieve the vsdns
        var callback = function(data) {
            // Add vsdn to cpu bar
            for(var i = 0; i < data.length; i++){
                var vsdn_data = data[i];
                cpubar.add_vsdn(vsdn_data);
            }            
        };
        fetchAllVSDN(USER, PHY_NW, callback);
    });

});

// Fetch physical topo from server 
//		Args: 
//			user: user-id
//			network_obj: PHY_NW [or TEN_NW]
function fetchPhysicalTopo(user,network_obj) {	
    hyperflexGetPhysicalTopo(function(result){
        var data = JSON.parse(result)["data"];
        network_obj.readNetwork(data);           
    },[user]);
}
