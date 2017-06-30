// Info Box
//// Update Node
function updateNodeInfoBox(nw, nodeData)
{
    clearEdgeInfoBox();

    var connData = nw.getConnectedNodes(nodeData.id);
    console.log("Connected nodes:",connData);
    var connIDs = connData[0];
    var ports = connData[1];
    var connNodes = nw.nodes.get(connIDs);
    var connNames = [];
    connNodes.forEach(function(v, k) {
        connNames.push(v.label);
    });
    var portTpls = [];
    for (var i = 1; i <= nodeData.num_ports; i++) {
        var cl = "nwplug-off";
        var title = "";
        var portK = $.inArray(i, ports);
        if (portK !== -1) {
            cl = "nwplug-on";
            title = connNames[portK];
        }
        var tpl = "<img src='../img/nwplug.svg' title='" + title + "' class='nwplug " + cl + "' />";
        portTpls.push(tpl);
    }

    var infos = {
        id: nodeData.id,
        name: nodeData.label,
        num_ports: nodeData.num_ports,
        portTpls: portTpls,
        vsdn: nodeData.vsdn,
        cpu: nodeData.cpu,
        addVSDN: true
    };

    // Set text fields
    $("#infoNodeName").html(infos.name || "N/A");
    $("#infoNodeID").html(infos.id || "N/A");
    $("#infoNodePorts").html(infos.num_ports || "N/A");
    $("#infoNodePortTpls").css("visibility","visible");
    $("#infoNodePortTpls").html("");    
    if (infos.portTpls) {
        infos.portTpls.forEach(function(v, k) {
            $("#infoNodePortTpls").append(v);
        });
    }
    $("#infoNodeVSDN").html(infos.vsdn || "N/A");
    $("#infoNodeCPU").val(infos.cpu || "");
    
    expandNodeInfoBox();
}
// Clear node box
function clearNodeInfoBox(collapse)
{
    $("#infoNodeName").html("");
    $("#infoNodeID").html("");
    $("#infoNodePorts").html("");
    $("#infoNodePortTpls").html("");
    $("#infoNodePortTpls").css("visibility","hidden");
    $("#infoNodeVSDN").html("");
    $("#infoNodeCPU").val("");
    
    if(collapse){
        collapseNodeInfoBox();
    }
}

function collapseNodeInfoBox()
{
    collapseBox("infoBoxNode");
}

function expandNodeInfoBox()
{
    expandBox("infoBoxNode");
}


//// Update Edge
function updateEdgeInfoBox(nw, edgeData)
{
    clearNodeInfoBox();
    // connected nodes
    var conn = [];
    var fromLabel = nw.nodes.get(edgeData.from).label;
    var toLabel = nw.nodes.get(edgeData.to).label;
    conn.push(fromLabel, toLabel);

    var infos = {
        id: edgeData.id,
        conn: conn,
        vsdn: edgeData.vsdn,
        datarate: edgeData.datarate
    };
    $("#infoEdgeID").html(infos.id || "N/A");
    $("#infoEdgeConn").html(infos.conn.join() || "N/A");
    $("#infoEdgeVSDN").html(infos.vsdn || "N/A");
    $("input#infoEdgeBW").val(infos.datarate || "");
    $("input#infoEdgeMsgRate").val(infos.msgrate || "");
    
    expandEdgeInfoBox();
}
// Clear edge box
function clearEdgeInfoBox(collapse)
{
    $("#infoEdgeID").html("");
    $("#infoEdgeConn").html("");
    $("#infoEdgeVSDN").html("");
    $("input#infoEdgeBW").val("");
    $("input#infoEdgeMsgRate").val("");
    
    if(collapse){
        collapseEdgeInfoBox();
    }
}

function collapseEdgeInfoBox()
{
    collapseBox("infoBoxEdge");
}

function expandEdgeInfoBox()
{
    expandBox("infoBoxEdge");
}

// Collapse/Expand side menu boxes
function collapseBox(boxID){
    var box = $("div#"+boxID);
    var btn = $(box).children(".sideMenuHead").children(".sideMenuCollapse");
    var body = $(box).children(".sideMenuBody");    
    
    btn.attr("class", "glyphicon glyphicon-menu-right sideMenuCollapse");
    body.css("visibility", "hidden");
    body.css("height", "0px");
    body.css("padding-bottom", "0px");
    body.css("padding-top", "0px");
    body.data("collapsed", true);
    
}

function expandBox(boxID){
    var box = $("div#"+boxID);
    var btn = $(box).children(".sideMenuHead").children(".sideMenuCollapse");
    var body = $(box).children(".sideMenuBody");
    
    btn.attr("class", "glyphicon glyphicon-menu-down sideMenuCollapse");
    body.css("height", "");
    body.css("padding-bottom", "");
    body.css("padding-top", "");
    body.css("visibility", "");
    body.data("collapsed", false);
    
}

function toggleBox(boxID){
    var box = $("div#"+boxID);    
    var body = $(box).children(".sideMenuBody");   
    
    if (body.data("collapsed")) {
        expandBox(boxID);
    }
    else {
        collapseBox(boxID);        
    }
}



function addVSDNCheckbox(vsdn, nw){
    // Add checkbox to menu
    var tpl =   "<div class='vsdnRow' data-vsdn='" + vsdn.vsdn.id + "'>" +
                    "<input type='checkbox' class='vsdnCheckbox' data-vsdn='" + vsdn.vsdn.id + "' checked/>" +
                    "<a class='vsdnLabel vsdnSelect' style='background-color: #" + vsdn.vsdn.color + ";'>" + vsdn.vsdn.name + "</a>" +
                    "<a href='#' style='float:right;' class='glyphicon glyphicon-trash vsdnDelete' data-vsdn='" + vsdn.vsdn.id + "'></a>" +
                "</div>";
    $("#vsdnList").append(tpl);
    
    // Checkbox handler
    $("input.vsdnCheckbox").unbind("change");
    $('input.vsdnCheckbox').change(function() {
        var vsdnID = parseInt($(this).data("vsdn"));
        console.log("check/uncheck "+vsdnID,$(this).is(":checked"));
        if ($(this).is(":checked")) {
            vsdnSetVisible(vsdnID, nw);
        }
        else {
            vsdnSetInvisible(vsdnID, nw, false, false);
        }
    });
    
    // VSDN select
    $(".vsdnSelect").unbind("click");
    $(".vsdnSelect").click(function() {
          var vsdn_id = parseInt($(this).parent().data("vsdn"));
          vsdnSelected(vsdn_id);
          console.log("VSDN selected:",vsdn_id);
    });
    
    // Button: Delete VSDN
    $(".vsdnDelete").unbind("click");
    $(".vsdnDelete").click(function() {
        var vsdnID = parseInt($(this).data("vsdn"));
        deleteVSDN(vsdnID, nw);
    });
    
    // Checkbox: All (VSDNS)
    // Unbind old change event
    $('input.vsdnAllCheckbox').unbind("change");
    // Add new change event
    $('input.vsdnAllCheckbox').change(function() {
        if ($(this).is(":checked")) {
            vsdns.forEach(function(vsdn, k) {
                vsdnSetVisible(vsdn.vsdn.id, nw);
            });
            // Check all vsdn checkboxes
            $('input.vsdnCheckbox').prop("checked", true);
        }
        else {
            vsdns.forEach(function(vsdn, k) {
                vsdnSetInvisible(vsdn.vsdn.id, nw);
            });
            // UnCheck all vsdn checkboxes
            $('input.vsdnCheckbox').prop("checked", false);
        }
    }); 
}

function getHeaderFields() {
    var data = {
        "name": $("input#paramName").val() || "N/A",
        "ctrl_ip": $("input#paramCtrlIP").val() || "N/A",
        "ctrl_port": parseInt($("input#paramCtrlPort").val()) || 6633,
        "subnet": $("input#paramSubnet").val() || "N/A",
        "isolation_method": parseInt($("input:radio[name='paramIsolation']:checked").val()) || 1,       
        "message_rate": parseInt($("input#paramMsgrate").val()) || 1000       
    };  
    data["id"] = VSDN_ID;
    
    // Get Controller entrypoint/access
    var ctrl_access;
    
    TEN_NW.nodes.forEach(function(node, nk){
        if(node.type === "controller"){
            if("entry_point" in node){
                ctrl_access = node.entry_point;
                return;
            }
        }
    });
    data.ctrl_access = ctrl_access;
    return data;
}

function setHeaderFields(data) {
    $("input#paramName").val(data.name);
    var c_arr = data.controller_url.split(":");
    var c_ip = c_arr[0], c_port = c_arr[1];
    $("input#paramCtrlIP").val(c_ip);
    $("input#paramCtrlPort").val(c_port);
    $("input#paramSubnet").val(data.subnet);
    $("input:radio[name='paramIsolation'][value='"+data.isolation_method+"']").attr("checked",true);      
    $("input#paramMsgrate").val(data.message_rate);
}

$(function() {

    
    
// Collapse/Expand side menu boxes on click
$(".sideMenuCollapse").click(function() {
    var boxID = $(this).parent().parent().attr('id');    
    toggleBox(boxID);  
});

// Initial collapse if data-collapsed == "1"
$(".sideMenuBody").each(function( index ) {
  if($(this).data("collapsed")) { collapseBox($(this).parent().attr("id"));}
});

});