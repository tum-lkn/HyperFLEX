var USER = 2;

$(function(){
    
    setTimeout(function(){
        getAllVSDNS();
        
        //
    },100);
    
    
    // Subscribe to vsdn_changed msg   
    // Topic, Callback function when msg is published
    WSS.subscribe("vsdn_changed",function(topic,data){
        clearVSDNS();
        getAllVSDNS();
    });
});

function getAllVSDNS() {
    hyperflexGetAllVSDN(function(result){
        // Removed Dummy message
        $(".noVSDNSDummy").css("visibility","hidden").css("height","0px").css("overflow","hidden");

        var data = JSON.parse(result)["data"];
        data.forEach(function(vsdn,k){
            vsdn.vsdn.color = vsdn_colors[vsdns.length];
            
            // Add checkboxes with labels                
            var tpl =   "<div class='vsdnRow' data-vsdn='" + vsdn.vsdn.id + "'>" +
                    "<input type='checkbox' class='vsdnCheckbox' data-vsdn='" + vsdn.vsdn.id + "' />" +
                    "<a class='vsdnLabel vsdnSelect' style='background-color: #" + vsdn.vsdn.color + ";'>" + vsdn.vsdn.name + "</a>" +
                "</div>";
            $("#vsdnList").append(tpl);

            $('input.vsdnCheckbox').change(function() {
                var vsdnID = parseInt($(this).data("vsdn"));                    
            });                

            // Checkbox: All (VSDNS)
            // Unbind old change event
            $('input.vsdnAllCheckbox').unbind("change");
            // Add new change event
            $('input.vsdnAllCheckbox').change(function() {
                if ($(this).is(":checked")) {                        
                    // Check all vsdn checkboxes
                    $('input.vsdnCheckbox').prop("checked", true);
                }
                else {                        
                    // UnCheck all vsdn checkboxes
                    $('input.vsdnCheckbox').prop("checked", false);
                }
            }); 
            
            // Add the vsdn to the list
            vsdns.push(vsdn);
            // Set perfbench indices (needed for graphs, pb suffix)
            vsdns[k].pb_index = k+1;

        });
    },[ USER ]);
}


function getSelectedVSDNS(){
    // Get selected vsdn_ids
    var vsdn_ids = [];
    $('input.vsdnCheckbox:checked').each(function(){
        vsdn_ids.push(parseInt($(this).data("vsdn")));
    });
    console.log("Selected VSDNs:",vsdn_ids);
    return vsdn_ids;
}