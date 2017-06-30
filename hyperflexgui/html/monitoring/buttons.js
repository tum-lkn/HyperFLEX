$(function () {
    $("#startPerfbench").click(function(){        
        var vsdn_ids = getSelectedVSDNS();
        
        // If no VSDNs available (Migration demo)
        if(vsdns.length === 0){
            var jsonrpc_ip = PERFBENCH_RPC_IPS[0];
            var jsonrpc_port = JSONRPC_PERFBENCH_PORT;
            console.log(jsonrpc_ip,jsonrpc_port);
            
            var rpc_obj = newRPC(jsonrpc_ip, jsonrpc_port);            
            
            var ctrl_port = PERFBENCH_DEFAULT_PORT;
            var ctrl_ip = PERFBENCH_DEFAULT_IP;
            var pb_parameters = {
                "ip": ctrl_ip,
                "port": ctrl_port,
                "pps": parseInt($("#messageRate").val()),
                "length": 120,
                "enable-livedata": "",
                "livedata-suffix": 1,
                "livedata-addr": JSONRPC_IP+":"+9874,
                "loss-threshold": 1000,
                "disable-logging": ""
                
            };
            
            var success_callback = function (result) {
                var data = JSON.parse(result);
                if("error" in data){
                    var error = data["error"];
                    console.log("Error:",error);
                    return;
                }            
                console.info("Perfbench successfully started!");                
            };

            var error_callback = function (error) {
                console.log("Error:",error);
            };
            
            pbStart(rpc_obj, success_callback, [JSON.stringify(pb_parameters)], error_callback);
            
            return;            
        }
        
        // If none selected, return
        if(vsdn_ids.length === 0) return;        
        
        vsdn_ids.forEach(function(vsdn_id, index){
            var vsdn_data = getVSDNData(vsdn_id);
            
            var success_callback = function (result) {
                var data = JSON.parse(result);
                if("error" in data){
                    var error = data["error"];
                    console.log("Error:",error);
                    return;
                }            
                console.info("Perfbench successfully started!");

                // Set color of graphs                
                latencyCharts[vsdn_data.pb_index-1].chart.options.data[0].color = "#"+vsdn_data.vsdn.color;
                lossCharts[vsdn_data.pb_index-1].chart.options.data[0].color = "#"+vsdn_data.vsdn.color;
            };

            var error_callback = function (error) {
                console.log("Error:",error);
            };
            
            
            
            var jsonrpc_ip = PERFBENCH_RPC_IPS[vsdn_data.pb_index-1];
            var jsonrpc_port = JSONRPC_PERFBENCH_PORT;
            console.log(jsonrpc_ip,jsonrpc_port);
            if(!vsdn_data.vsdn.rpc_obj)
                vsdn_data.vsdn.rpc_obj = newRPC(jsonrpc_ip, jsonrpc_port);            
            
            var ctrl_port = parseInt(vsdn_data.vsdn.controller_url.split(":")[1]);
            var ctrl_ip = vsdn_data.vsdn.controller_url.split(":")[0];
            var pb_parameters = {
                "ip": ctrl_ip,
                "port": ctrl_port,
                "pps": parseInt($("#messageRate").val()),
                "length": 120,
                "enable-livedata": "",
                "livedata-suffix": vsdn_data.pb_index,
                "livedata-addr": JSONRPC_IP+":"+9874,
                "loss-threshold": 1000,
                "disable-logging": ""
                
            };
            pbStart(vsdn_data.vsdn.rpc_obj, success_callback, [JSON.stringify(pb_parameters)], error_callback);
        }); 
        
    });

$("#killPerfbench").click(function(){
        var vsdn_ids = getSelectedVSDNS();
        
        // If none selected, return
        if(vsdns.length === 0){
            var jsonrpc_ip = PERFBENCH_RPC_IPS[0];
            var jsonrpc_port = JSONRPC_PERFBENCH_PORT;
            var rpc_obj = newRPC(jsonrpc_ip, jsonrpc_port);            
            console.log(jsonrpc_ip,jsonrpc_port);
        }
            
        var success_callback = function (result) {
            var data = JSON.parse(result);
            if("error" in data){
                var error = data["error"];
                console.log("Error:",error);
                return;
            }            
            console.info("Perfbench successfully killed!");
        };
        
        var error_callback = function (error) {
            console.log("Error:",error);
        };
        
        if(vsdns.length === 0){
            pbKill(rpc_obj, success_callback, [], error_callback);
        } else {
            vsdn_ids.forEach(function(vsdn_id, index){
                var vsdn_data = getVSDNData(vsdn_id);
                
                var jsonrpc_ip = PERFBENCH_RPC_IPS[vsdn_data.pb_index-1];
                var jsonrpc_port = JSONRPC_PERFBENCH_PORT;
                if(!vsdn_data.vsdn.rpc_obj)
                    vsdn_data.vsdn.rpc_obj = newRPC(jsonrpc_ip, jsonrpc_port);
                pbKill(vsdn_data.vsdn.rpc_obj, success_callback, [], error_callback);
            });
        }   
    });
    
    $("#startDitra1").click(function(){
        var ditra_id = 1;
        
        var success_callback = function (result) {
            console.info("Ditra "+ditra_id+" successfully started!");
        };
        
        var error_callback = function (error) {
            console.log("Error:",error);
        };
        
        
        hyperflexStartDitra(success_callback, [ditra_id], error_callback);
    });
    
    $("#startDitra2").click(function(){
        var ditra_id = 2;
        
        var success_callback = function (result) {
            console.info("Ditra "+ditra_id+" successfully started!");
        };
        
        var error_callback = function (error) {
            console.log("Error:",error);
        };
                
        hyperflexStartDitra(success_callback, [ditra_id], error_callback);
    });
    
    $("#stopDitra1").click(function(){
        var ditra_id = 1;
        
        var success_callback = function (result) {
            console.info("Ditra "+ditra_id+" successfully stopped!");
        };
        
        var error_callback = function (error) {
            console.log("Error:",error);
        };
        
        
        hyperflexStopDitra(success_callback, [ditra_id], error_callback);
    });
    
    $("#stopDitra2").click(function(){
        var ditra_id = 2;
        
        var success_callback = function (result) {
            console.info("Ditra "+ditra_id+" successfully stopped!");
        };
        
        var error_callback = function (error) {
            console.log("Error:",error);
        };
        
        
        hyperflexStopDitra(success_callback, [ditra_id], error_callback);
    });

    $("#resetDemo").click(function() {
        // STOP Ditra1
        // -------------
        var success_callback = function (result) {
            console.info("Ditra 1 successfully stopped");
        };
        var error_callback = function (error) {
            console.log("Error:", error);
        };
        hyperflexStopDitra(success_callback, [1], error_callback);

        // STOP Ditra2
        // -------------
        var success_callback = function (result) {
            console.info("Ditra 2 successfully stopped");
        };
        var error_callback = function (error) {
            console.log("Error:", error);
        };
        hyperflexStopDitra(success_callback, [2], error_callback);
        // STOP PERFBECH
        // -------------
        var jsonrpc_ip = PERFBENCH_RPC_IPS[0];
        var jsonrpc_port = JSONRPC_PERFBENCH_PORT;
        console.log(jsonrpc_ip,jsonrpc_port);
        var rpc_obj = newRPC(jsonrpc_ip, jsonrpc_port);            
        var success_callback = function (result) {
            console.info("Perfbench successfully stopped");
        };
        var error_callback = function (error) {
            console.log("Error:", error);
        };
        pbKill(rpc_obj, success_callback, [], error_callback);
        
        // STOP PROXY
        // ------------
        var success_callback = function (result) {
            console.info("Proxy successfully restarted");
        };
        var error_callback = function (error) {
            console.log("Error:", error);
        };
        hyperflexRestartProxy(success_callback, [], error_callback);
    });
});
