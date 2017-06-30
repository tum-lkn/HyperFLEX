/* global PHY_NW */

$(function() {

    // Button: Get Topo from server
    $("button#requestTopo").click(function() {
        hyperflexGetPhysicalTopo(function(result){
            var data = JSON.parse(result)["data"];
            PHY_NW.readNetwork(data);
        },[USER]);
    });

    // Button: Get VSDNS from server
    $("button#requestVSDNS").click(function() {
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

    // Button: Dump Network
    $("button#dumpNetwork").click(function() {
        var content = PHY_NW.dumpNetwork();
        $("textarea#dump").val(content);

    });
    // Button: Read Network
    $("button#readNetwork").click(function() {
        var content = $("textarea#dump").val();
        PHY_NW.readNetwork(content);
    });


    // Button: Read vSDN
    $("button#readVSDN").click(function() {
        var content = $("textarea#dump").val();
        readVSDN(content, PHY_NW);
    });

    // Button: Dump vSDNs
    $("button#dumpVSDNS").click(function() {
        var content = dumpVSDNS();
        console.log(content);

    });    


    // Add Edge
    $("#addEdge").click(function() {
        PHY_NW.network.addEdgeMode();
        PHY_NW.addEdgeManually = true;
    });

    // Button: Remove
    $("button#remove").click(function() {
        var selectedNodeIDs = PHY_NW.network.getSelectedNodes();
        var selectedEdgeIDs = PHY_NW.network.getSelectedEdges();
        PHY_NW.nodes.remove(selectedNodeIDs);
        PHY_NW.edges.remove(selectedEdgeIDs);
        clearNodeInfoBox();
        clearEdgeInfoBox();
    });
});
