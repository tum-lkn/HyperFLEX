/* global PHY_NW */

$(function () {
    
    
    /* Entry Point Dropdown List */
    
    //      If cplane switch is added, add it to the dropdownlist
    PHY_NW.nodes.on("add", function (ev, properties) {
        var nodeID = properties.items[0];
        var node = PHY_NW.nodes.get(nodeID);
        if (node.type === "switch" && node.cplane) {
            // Add switch   
            $("#selectEntryPoint").append($('<option>', {
                value: node.id,
                text: node.label
            }));
            
        }
    });
    
    //      If switch removed, remove it from dropdown list
    PHY_NW.nodes.on("remove", function (ev, properties) {
        var nodeID = properties.items[0];
        
        var node = PHY_NW.nodes.get(nodeID);
        if(!node) return;
        if (node.type === "switch" && node.cplane) {
            // Remove Switch            
            $("#selectEntryPoint option[value="+nodeID+"]").remove();
            
        }
    });
    
    //      If controller selected, show entrypoint dropdown list
    $("input:radio[name='chooseNode']").change(function(){
        var selected = $( "input:radio[name='chooseNode']:checked" );
        if(selected.data("type") === "controller"){
            $("#selectEntryPoint").prop('disabled', false);
        }
        else {
            $("#selectEntryPoint").prop('disabled', true);
        }
    });
    
    /* Add Button */
    $("button#addNodeTenant").click(function () {
        var type = $("input.chooseNode:checked").data("type") || "switch";
        var nodeData = {
            type: type,
            physics: false,
            label: $("#nodeLabel").val(),
            cplane: $("input#attrControlPlane").prop( "checked" )
        };
        var entrypoint_id = null;
        // Controller:
        // Set cplane and entrypoint attr
        if(type === "controller"){
            entrypoint_id = $( "#selectEntryPoint option:selected" ).val();
            nodeData.entrypoint = entrypoint_id;  
        }
        
        var nodeID = PHY_NW.addNode(nodeData);
        
        // Controller:
        // Add edge between controller node and (cplane) switch
        if(type === "controller" && entrypoint_id){                        
            var edgeData = {
              from:  nodeID,
              to: entrypoint_id,
              cplane: true
            };   
            PHY_NW.addEdge(edgeData);
        }
        
        TEN_NW.network.fit();
        
        
        
    });
});