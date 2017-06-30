// This is a wrapper Class for the WebSocket class.
// It has some additional features:
//  * Event system
//      Call functions on certain events. 
//      E.g. 
//          Websocket.addevent("open",function(){ alert("Socket connected"); });
//          Websocket.addevent("message",function(msg){ alert("Message received: "+msg); });
//          Valid events are: open, close, message, reconnect, error
//     
//  * Subscription system
//      Subscribe to any message published by the server
//      Websocket.subscribe("cpu",function(topic,data){ alert("Topic "+topic+" was published with data: "+data) })
//      
//  * Auto-Reconnect
//      The Websocket auto-reconnects every 3 seconds if the connection is lost
//      Subscriptions are resubscribed on reconnect (so you only have to subscribe once)


function Websocket(ip, port) {
    var parentThis = this;
    this.reconnect_time = 3;
    this.ip = ip;
    this.port = port;
    this.events = {open: [], close:[], message:[], reconnect:[], error:[]};
    this.subscriptions = {};
      
    this.connect = function() {
        console.info("Websocket:","Connecting to",parentThis.ip + ":" + parentThis.port);
        var socket = new WebSocket("ws://" + parentThis.ip + ":" + parentThis.port);
        
        socket.onopen = function () {
            console.info("Websocket:","Connected to " + parentThis.ip + ":" + parentThis.port);
            parentThis.isopen = true;
            parentThis.callevent("open");
        };

        socket.onmessage = function (e) {
            if (typeof e.data === "string") {
                parentThis.callevent("message",e.data);
                console.info("Websocket:","Received:",e.data);
            }
            else {
                var arr = new Uint8Array(e.data);
                var hex = '';
                for (var i = 0; i < arr.length; i++) {
                    hex += ('00' + arr[i].toString(16)).substr(-2);
                }
                console.info("Websocket:","Binary message received: " + hex);
            }
        };

        socket.onclose = function (e) {
            console.info("Websocket:","Connection closed with code:",e.code, e.reason);
            parentThis.callevent("close ");

            parentThis.socket = null;   
            parentThis.isopen = false;
            
            // Start reconnect timer
            parentThis.start_reconnect_timer();
        };
        
        socket.onerror = function (e) {
	    console.info("error");
            console.info("Websocket:",e.data);   
            parentThis.callevent("error",e.data);
        };
        parentThis.socket = socket;
        
    };
    
    this.start_reconnect_timer = function() {
        console.info("Websocket:","Reconnecting in",this.reconnect_time,"seconds");
        setTimeout(this.connect,this.reconnect_time*1000);
    };
    
    this.addevent = function(event_name, func, once) {
        // run the event only once?
        var once = once || false;
        
        if(!event_name in this.events){
            console.info("Websocket:","Addevent:","Event "+event_name+" not found!");
            return;
        }
        this.events[event_name].push({func:func,once:once});
    };
    
    this.callevent = function(event_name, args) {
        for (var i = 0; i < parentThis.events[event_name].length; i++) {
            parentThis.events[event_name][i].func(args);
            
            if(parentThis.events[event_name][i].once === true){
                parentThis.events[event_name].pop(i);
            }
        }
    };
    
    this.subscribe = function(topic,callback_func) {
        
        if(!(topic in this.subscriptions)){
            this.subscriptions[topic] = [];
        }
        this.subscriptions[topic].push(callback_func);
        
        // Send Subscription data to server        
        var data = {
            "method": "subscribe",
            "topic": topic
        };
        var msg = JSON.stringify(data);
        
        // If connection is open, send subscribe msg
        if(this.isopen){
            console.info("Websocket:","Subscribed to "+topic);
            this.send(msg);
        }
        // Always resubscribe if the connection was closed and reopened                
        this.addevent("open", function(){ 
            parentThis.send(msg);
            console.info("Websocket:","Subscribed to "+topic);
        });
    };
    
    this.handle_subscription_message = function(msg) {        
        var parsed;
        try {        
            parsed = JSON.parse(msg);
        }
        catch(e) { return; }        
        if("topic" in parsed){
            var topic = parsed["topic"];
            if(!(topic in parentThis.subscriptions)){return;}
            
            var data = parsed["data"];
            for (var i = 0; i < parentThis.subscriptions[topic].length; i++) {
                parentThis.subscriptions[topic][i](topic,data);
            }
        }        
    };
    this.addevent("message",this.handle_subscription_message);

    this.send = function (msg) {
        if (parentThis.isopen) {
            this.socket.send(msg);
            console.info("Websocket:","Sent", msg);
            return true;
        } else {
            console.info("Websocket:","Connection not opened.");
            return false;
        }
    };

    this.sendBinary = function () {
        if (parentThis.isopen) {
            var buf = new ArrayBuffer(32);
            var arr = new Uint8Array(buf);
            for (i = 0; i < arr.length; ++i)
                arr[i] = i;
            this.socket.send(buf);
            console.info("Websocket:","Binary message sent.");
        } else {
            console.info("Websocket:","Connection not opened.");
        }
    };  
    
    this.connect(); 
}





