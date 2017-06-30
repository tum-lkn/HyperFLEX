var vsdns = [];

var color_map = [];

function addVSDN(vsdn, nw, showEmbedding) {
    var showEmbedding = showEmbedding || false;
    
    // If vsdn already exists, remove it first
    if(getVSDNData(vsdn.vsdn.id)){ 
        console.log("vsdn",vsdn.vsdn.id,"already exists, removing..");
        removeVSDN(vsdn.vsdn.id, nw); 
    }
    
    console.log("addVSDN",vsdn);
    
    
    
    if(color_map.indexOf(vsdn.vsdn.id) < 0){        
        vsdn.vsdn.color = vsdn_colors[color_map.length];
        color_map.push(vsdn.vsdn.id);
    }
    else {
        vsdn.vsdn.color = vsdn_colors[color_map.indexOf(vsdn.vsdn.id)];
    }
    // Add vsdn to list
    vsdns.push(vsdn);
    
    // Color parsing
    var rgba = hexToRgb(vsdn.vsdn.color);

    var rgba_str = "rgba("+rgba.r+","+rgba.g+","+rgba.b+","+"1"+")";
    
    // Add node
    vsdn.nodes.forEach(function(vv, kk) {
        // If we already have this node, ignore it
        if(nw.nodes.get(vv.id) !== null) return;
        
        // Only change color of controller nodes
        if(vv.type === "controller"){
            var icon = {                
                color: rgba_str
            };
        }
        
        nw.addNode($.extend(vv, {
            vsdn: vsdn.vsdn.id,
            icon: icon            
            }
        ));
    });
    vsdn.edges.forEach(function(edgeData, kk) {
        var from = edgeData.from;
        var to = edgeData.to;
        // If embedding list is available, use this
        if(showEmbedding && "embedding" in edgeData && edgeData["embedding"].length > 0){
            var e_edges = edgeData.embedding;
            e_edges.forEach(function(edge_id, i) {
                var phy_edge = nw.edges.get(edge_id);                
                
                // If physical edge does actually exist
                if(phy_edge) {
                   from = phy_edge.from; 
                   to = phy_edge.to; 
                }               
                
                nw.addEdge({                        
                    vsdn: vsdn.vsdn.id,
                    color: vsdn.vsdn.color,
                    width: 3,
                    font: {color: '#777777', size: 12},
                    title: vsdn.vsdn.name,
                    physics:false,					
                    smooth: {
                        enabled: true,
                        type: "horizontal",
                        roundness: 0.1 + vsdns.length * 0.05
                    },
                    length: 100,					
                    from: from,
                    to: to					
                });
            });
        }
        // Otherwise use the actual link
        else {
            // Add vSDN link
            nw.addEdge($.extend({}, edgeData, {
                id: "l"+edgeData.id,
                vsdn: vsdn.vsdn.id,
                color: vsdn.vsdn.color,
                width: 3,
                font: {color: '#777777', size: 12},
                title: vsdn.vsdn.name,
                physics:false,
                //label:vsdn.name,
                smooth: {
                    enabled: true,
                    type: "horizontal",
                    roundness: 0.1 + vsdns.length * 0.05
                },
                length: 100,
                dashes: edgeData.cplane || false,
                from: edgeData.from,
                to: edgeData.to
                
            }));
        }

    });   
    
    // Hide dummy msg
    $(".noVSDNSDummy").css("visibility","hidden").css("height","0px").css("overflow","hidden");
    
    // Add the VSDN to the list
    addVSDNCheckbox(vsdn, nw);   
    
    nw.network.fit();

}



function vsdnSetVisible(vsdnID, nw) {
    vsdns.forEach(function(v, k) {
        if (v.vsdn.id !== vsdnID)
            return;
        nw.nodes.forEach(function(vv, kk) {
            if ("vsdn" in vv && vv.vsdn === vsdnID)
                nw.nodes.update({id: vv.id, hidden: false});
        });
        nw.edges.forEach(function(vv, kk) {
            if ("vsdn" in vv && vv.vsdn === vsdnID)
                nw.edges.update({id: vv.id, hidden: false});
        });
    });
}
function vsdnSetInvisible(vsdnID, nw, ignoreNodes, ignoreEdges) {
    var ignoreNodes = ignoreNodes || false;
    var ignoreEdges = ignoreEdges || false;
    vsdns.forEach(function(v, k) {
        if (v.vsdn.id !== vsdnID)
            return;
        if(!ignoreNodes){
            nw.nodes.forEach(function(vv, kk) {
                if ("vsdn" in vv && vv.vsdn === vsdnID)
                    nw.nodes.update({id: vv.id, hidden: true});
            });
        }
        if(!ignoreEdges){
            nw.edges.forEach(function(vv, kk) {
                if ("vsdn" in vv && vv.vsdn === vsdnID)
                    nw.edges.update({id: vv.id, hidden: true});
            });
        }
    });
}




function readVSDN(data, nw) {
    if(typeof data === "string")
        data = JSON.parse(data);
    addVSDN(data, nw);    
}

function readVSDNS(data, nw, showEmbedding) {
    // If we get an JSON string parse it
    if(typeof(data) === "string")
        data = JSON.parse(data);
    
    // Delete all VSDNs
    clearVSDNS(nw);    
    console.log(JSON.stringify(data,null,2));
    
    // Add each vsdn separately
    data.forEach(function(v, k) {
        addVSDN(v, nw, showEmbedding);
    });
}

// Remove vsdn from GUI only
function removeVSDN(vsdnID, nw){
    vsdn_edges = nw.edges.getIds({
        filter: function (item) {
            return (item.vsdn === vsdnID);
        }
    });
    nw.edges.remove(vsdn_edges);
    
    vsdn_nodes = nw.nodes.getIds({
        filter: function (item) {
            return (item.vsdn === vsdnID);
        }
    });
    nw.nodes.remove(vsdn_nodes);
    
    $("div.vsdnRow[data-vsdn='"+vsdnID+"']").remove();
    
    var removeID = null;
    for(var i = 0;i < vsdns.length; i++) {    
       if(vsdns[i].vsdn.id === vsdnID){
           removeID = i;
           break;
       } 
    };
    console.log("Removing array index",removeID);    
    
    vsdns.splice(removeID, 1);
    console.log(vsdns);
}

// Remove all VSDNs from GUI only
function clearVSDNS(nw, keepData){
    // Do we want to keep the vsdn data in vsdn list
    //  or completely delete it from the gui
    var keepData = keepData || false;
    
    if(nw){
        vsdn_edges = nw.edges.getIds({
            filter: function (item) {
                return (item.vsdn !== undefined);
            }
        });
        nw.edges.remove(vsdn_edges);

        vsdn_nodes = nw.nodes.getIds({
            filter: function (item) {
                return (item.vsdn !== undefined);
            }
        });
        nw.nodes.remove(vsdn_nodes);
    }
    
    if(!keepData){
        $("div.vsdnRow").remove();

        vsdns = [];
    }
}
removeAllVSDNS = clearVSDNS;

// Delete VSDN from database and from GUI, return if successful
function deleteVSDN(vsdnID, nw){

    var success = false;
    hyperflexRemoveVSDN(function(){
        console.info("VSDN "+vsdnID+" deleted from server");
        
        var i = color_map.indexOf(vsdnID);
        color_map.splice(i, 1);
        
        removeVSDN(vsdnID, nw);
    },[vsdnID, USER]);
}

function dumpVSDNS() {
    var json_string = JSON.stringify(vsdns);
    return json_string;
}

// Fetch specified vsdn from server
function fetchVSDN(user, vsdn_id, network_obj) {
    var senddata = {
        user: user,
        vsdn_id: vsdn_id
    };
    hyperflexGetVSDN(function(result){
        // On success: Load vsdn into network
        var data = JSON.parse(result);
        readVSDN(data["data"], network_obj);           
    },[vsdn_id, user]);
}

function fetchAllVSDN(user, network_obj, callback) {
    clearVSDNS();
    hyperflexGetAllVSDN(function(result){
            var data = JSON.parse(result)["data"];
            readVSDNS(data, network_obj, true);
            
            if(callback)
                callback(data);            
    },[ user ]);
}


// Prepare our vsdn data (header data, vsdn network) for vsdn request/update
function prepVSDNData(network_obj) {
    // Read network
    var data = network_obj.dumpNetwork(true);
    
    // Remove entry_point nodes (switches with cplane)
    for(var i = 0; i < data.nodes.length; i++){
        if(data.nodes[i].type === "switch" && data.nodes[i].cplane === true)
            data.nodes.splice(i,1);
    }
    
    // Read header fields
    data["vsdn"] = getHeaderFields();
    
    return data;
}


function vsdnSelected(vsdn_id) {
    // Expand the vsdn parameters box
    expandBox("paramBox");
    
    VSDN_ID = vsdn_id;
    
    setHeaderFields(getVSDNData(vsdn_id).vsdn);
}

function getVSDNData(vsdn_id) {
    var found_vsdn;
    vsdns.forEach(function(vsdn,k){
        if(vsdn.vsdn.id !== vsdn_id) return;
        found_vsdn = vsdn;
    });
    return found_vsdn;
}
