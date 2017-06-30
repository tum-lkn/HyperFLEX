var jsonrpc = new $.JsonRpcClient({ajaxUrl: 'http://' + JSONRPC_IP + ':' + JSONRPC_PORT + '/jsonrpc', headers: {"content-type": 'application/json'}});

function hyperflexGetAllVSDN(callback, args)
{
    var msg = 'hyperflexhandler.get_all_vsdn';
    jsonrpc.call(msg, args, callback, function (error) {
        console.log(error);
    });

}

function hyperflexGetVSDN(callback, args)
{
    var msg = 'hyperflexhandler.get_vsdn';
    jsonrpc.call(msg, args, callback, function (error) {
        console.log(error);
    });

}

function hyperflexRemoveVSDN(callback, args)
{
    var msg = 'hyperflexhandler.remove_vsdn';
    jsonrpc.call(msg, args, callback, function (error) {
        console.log(error);
    });

}

function hyperflexGetPhysicalTopo(callback, args)
{
    var msg = 'hyperflexhandler.get_physical_topo';
    jsonrpc.call(msg, args, callback, function (error) {
        console.log(error);
    });

}

function hyperflexRequestVSDN(callback, args, callback_error)
{
    
    var msg = 'hyperflexhandler.request_vsdn';
    jsonrpc.call(msg, args, callback, callback_error);
    
    

}

function hyperflexUpdateVSDN(callback, args, callback_error)
{
    var msg = 'hyperflexhandler.update_vsdn';
    jsonrpc.call(msg, args, callback, callback_error);
}

function hyperflexAuthenticate(callback, args, callback_error){
    var msg = 'hyperflexhandler.authenticate';
    jsonrpc.call(msg, args, callback, callback_error);
}

function hyperflexStartDitra(callback, args, callback_error){
    var msg = 'hyperflexhandler.start_ditra';
    jsonrpc.call(msg, args, callback, callback_error);
}

function hyperflexStopDitra(callback, args, callback_error){
    var msg = 'hyperflexhandler.stop_ditra';
    jsonrpc.call(msg, args, callback, callback_error);
}
function hyperflexRestartProxy(callback, args, callback_error){
    var msg = 'hyperflexhandler.restart_proxy';
    jsonrpc.call(msg, args, callback, callback_error);
}

function hyperflexStartPerfbench(callback, args, callback_error){
    var msg = 'hyperflexhandler.startperfbench';
    jsonrpc.call(msg, args, callback, callback_error);
}

function hyperflexKillPerfbench(callback, args, callback_error){
    var msg = 'hyperflexhandler.killperfbench';
    jsonrpc.call(msg, args, callback, callback_error);
}


