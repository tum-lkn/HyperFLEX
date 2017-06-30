// Network Class
function Network(options) {
    var parentThis = this;

    // Save options
    this.nodeTypes = options.nodeTypes;
    this.edgeStyle = options.edgeStyle;
    this.network_options = options.network_options;

    this.nodes = new vis.DataSet([]);
    this.edges = new vis.DataSet([]);
    this.vis_container = document.getElementById(options.container);
    this.vis_data = {
        nodes: this.nodes,
        edges: this.edges
    };
    this.network = new vis.Network(this.vis_container, this.vis_data, this.network_options);

    // Get highest Node ID + 1
    // used for string-IDs only
    this.calcNodeID = function(type)
    {
        var max = 0;
        this.nodes.forEach(function(v, k) {
            if (v.type !== type)
                return;
            var id = parseInt(v.id.slice(this.nodeTypes[type].idPrefix.length));
            if (id > max)
                max = id;
        });
        var new_id = this.nodeTypes[type].idPrefix + (max + 1).toString();
        return new_id;
    };

    // Get highest Edge ID
    this.getHighestEdgeID = function()
    {
        var max = 1;
        if (this.edges.length >= 1)
            max = this.edges.max("id").id;
        return max;
    };

    // Get highest Node ID
    this.getHighestNodeID = function()
    {
        var max = 1;
        if (this.nodes.length >= 1)
            max = this.nodes.max("id").id;
        return max;
    };

    // Get all nodes connected to node
    //  Returns: [connectedNodes[], ports[]]
    this.getConnectedNodes = function(nodeID) {
        var connectedIDs = [];
        var ports = [];
        this.edges.forEach(function(v, k) {
            
            if (v.vsdn)
                return;
            if (v.from === nodeID) {
                connectedIDs.push(v.to);
                ports.push(v.from_port);
            }
            else if (v.to === nodeID) {
                connectedIDs.push(v.from);
                ports.push(v.to_port);
            }
        });
        return [connectedIDs, ports];
    };
    
    this.checkEdgeStyle = function(edgeData) { 
        var edgeStyle = this.edgeStyle["default"];
        return $.extend(true,{},edgeStyle,edgeData);    

    };

    this.checkNodeStyle = function(nodeData) {
        nodeData.id = nodeData.id || null;        
        var nodeStyle = $.extend({},this.nodeTypes[nodeData.type]);
        
        //  Special cases
        //// cplane attribute: makes the node smaller, diff color
        if(nodeData.type === "switch" && nodeData.cplane) {
            nodeStyle = $.extend({},this.nodeTypes["switch_cplane"]);
        }    
        //
        nodeData = $.extend(true, {}, nodeStyle, nodeData);
        return nodeData;
    };
    
    this.addNode = function(nodeData) {
        var nodeData = jQuery.extend({}, nodeData);
        nodeData.type = nodeData.type || "switch";
        nodeData.label = nodeData.label || "new_node";  
        nodeData = this.checkNodeStyle(nodeData);
        console.log("addNode",nodeData);
        var id_arr = this.nodes.add(nodeData);        
        return id_arr[0];
    };

    this.addEdge = function(edgeData) {
        var edgeData = jQuery.extend({}, edgeData);
        edgeData = this.checkEdgeStyle(edgeData);
        console.log("addEdge",edgeData);
        var id_arr = this.edges.add(edgeData);
        return id_arr[0];
    };

    this.positionNode = function(nodeID) {
        var v = this.nodes.get(nodeID);
        // Positioning
        y = v.y || 0;
        if (v.yMin && v.yMax) {
            y = v.yMin + (v.yMax - v.yMin) * Math.random();
            y = Math.round(y);
        }
        this.nodes.update({id: v.id, y: y});
    };
    this.positionNodes = function() {
        this.nodes.forEach(function(v, k) {
            this.positionNode(v.id);
        });
        this.network.stabilize();
    };

    this.dumpNetwork = function(as_object) {
        as_object = as_object || false;
        
        this.network.storePositions();
        var data = {
            nodes: [],
            edges: []
        };
        data.nodes = this.nodes.get({
            fields: ['id', 'type', 'label', 'num_ports', 'vsdn', 'x', 'y', 'cpu', 'cplane', 'entry_point']
        });
        data.edges = this.edges.get({
            fields: ['from', 'to', 'vsdn', 'from_port', 'to_port', 'datarate', 'msgrate']
        });
        
        if(as_object === false){
            data = JSON.stringify(data);
        }
        
        return data;
    };

    this.readNetwork = function(data) {
        // If we get an JSON string parse it
        if(typeof(data) === "string")
            data = JSON.parse(data);        
        console.log(JSON.stringify(data,null,2));
        this.nodes.clear();
        this.edges.clear();

        data.nodes.forEach(function(v, k) {
            parentThis.addNode(v);
        });

        data.edges.forEach(function(v, k) {
            var edgeID = parentThis.addEdge(v);
            // Add cplane field to edges connected to cplane nodes
            // Make cplane edges dashed
            if(parentThis.nodes.get(v.from).cplane || parentThis.nodes.get(v.to).cplane){
                console.log("cplane",edgeID,true);
                parentThis.edges.update({id: edgeID, cplane: true, dashes: true});
            }
        });
        
        this.network.fit();
    };
    
    this.clear = function() {
        this.nodes.clear();
        this.edges.clear();
    };

    this.network.on("selectNode", function(params) {
        updateNodeInfoBox(parentThis, parentThis.nodes.get(params.nodes[0]));
    });
    this.network.on("deselectNode", function(params) {
        clearNodeInfoBox(true);        
    });

    this.network.on("selectEdge", function(params) {
        updateEdgeInfoBox(parentThis, parentThis.edges.get(params.edges[0]));
    });
    this.network.on("deselectEdge", function(params) {
        clearEdgeInfoBox(true);
    });

    this.edges.on("add", function(ev, properties) {
        if(!parentThis.addEdgeManually) return;
        var edgeID = properties.items[0];
        //parentThis.checkEdgeStyle(edgeID);
        parentThis.addEdgeManually = false;

    });
    
    this.edges.on("remove", function(ev, properties) {
        clearEdgeInfoBox();
        clearNodeInfoBox();
        parentThis.network.selectEdges([]);
    });
    
    this.nodes.on("remove", function(ev, properties) {
        var nodeID = parseInt(properties.items[0]);
        
        // Also remove connected edges
        parentThis.edges.forEach(function(v, k){            
            if(v.to === nodeID || v.from === nodeID){ 
                parentThis.edges.remove(v.id);
            }            
        });
        
        clearEdgeInfoBox();
        clearNodeInfoBox();
        parentThis.network.selectEdges([]);
    });
    
    this.background = new Image();
    this.background.src = "../img/germany.svg";
    this.background.className = "background";
    // Background
    this.network.on("beforeDrawing", function (ctx) {        
        ctx.drawImage(parentThis.background, -446, -631,892.92,1262.84);
  });
}