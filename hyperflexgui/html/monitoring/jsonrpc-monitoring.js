function newRPC(ip, port) {
    var rpc_obj = new $.JsonRpcClient({ajaxUrl: 'http://' + ip + ':' + port + '/jsonrpc', headers: {"content-type": 'application/json'}});
    return rpc_obj;
}

function pbStart(jsonrpc_obj, callback, args, callback_error){
    var msg = 'perfbenchdispatcher.start_perfbench';
    jsonrpc_obj.call(msg, args, callback, callback_error);
}

function pbKill(jsonrpc_obj, callback, args, callback_error){
    var msg = 'perfbenchdispatcher.stop';
    jsonrpc_obj.call(msg, args, callback, callback_error);
}


