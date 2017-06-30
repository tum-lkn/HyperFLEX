$(function () {
    // Button: Set Link bandwidth
    $("#setLinkBW").click(function () {
        var datarate = parseFloat($("#infoEdgeBW").val());
        var selectedEdge = TEN_NW.edges.get(TEN_NW.network.getSelectedEdges()[0]);
        TEN_NW.edges.update({id: selectedEdge.id, datarate: datarate});
    });

    // Button: Set Node CPU
    $("#setNodeCPU").click(function () {
        var cpu = parseFloat($("#infoNodeCPU").val());
        var selectedNode = TEN_NW.nodes.get(TEN_NW.network.getSelectedNodes()[0]);
        TEN_NW.nodes.update({id: selectedNode.id, cpu: cpu});
    });

    // Button: Get Topo from server
    $("button#requestTopo").click(function () {
        fetchPhysicalTopo(USER,PHY_NW);
    });
	
    // Add Edge
    $("#addEdgeTenant").click(function () {
        TEN_NW.network.addEdgeMode();
        TEN_NW.addEdgeManually = true;
    });

    // Add Node from phy. network
    $("#infoNodeAddToVSDN").click(function () {
        PHY_NW.network.stabilize();
        PHY_NW.network.storePositions();
        var nodeData = PHY_NW.nodes.get(PHY_NW.network.getSelectedNodes()[0]);

        // If node_id already exists, return
        if(TEN_NW.nodes.get(nodeData.id))
            return;
        
        var nodeID = TEN_NW.addNode(nodeData);
        TEN_NW.nodes.forEach(function (v, k) {
            TEN_NW.nodes.update({id: v.id, x: v.x, fixed: true});
        });
        //TEN_NW.network.fit();   
    });

         

    // Button: Remove
    $("button#removeT").click(function () {
        var selectedNodeIDs = TEN_NW.network.getSelectedNodes();
        var selectedEdgeIDs = TEN_NW.network.getSelectedEdges();
        TEN_NW.nodes.remove(selectedNodeIDs);
        TEN_NW.edges.remove(selectedEdgeIDs);
        clearNodeInfoBox();
        clearEdgeInfoBox();
    });

    // Button: Request VSDN
    $("button#VSDNRequest").click(function () {
        requestVSDN(USER, prepVSDNData(TEN_NW), TEN_NW);
    });

    // Button: Update VSDN
    $("button#VSDNUpdateRequest").click(function () {
        updateVSDN(USER,prepVSDNData(TEN_NW),TEN_NW);
    });
    
    // Button: Remove VSDN
    $("button#VSDNRemoveRequest").click(function () {
        removeVSDN(VSDN_ID, TEN_NW);
    });
    
    // Button: New VSDN
    $("button#newVSDN").click(function () {
        // Expand vsdn parameters box
        expandBox("paramBox");
        
        TEN_NW.clear();
        VSDN_ID = null;
        $("button#VSDNRequest").removeAttr("disabled");
        $("button#infoNodeAddToVSDN").removeAttr("disabled");
    });

});
