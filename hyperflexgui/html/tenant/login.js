$(function () {
    // Show login popup at startup
    $('.loginPopup').modal('toggle');

    /* Login Button */
    $("form#login").submit(function (event) { 
        
        event.preventDefault();
        
        var username = $("input#loginUsername").val();
        var password = $("input#loginPassword").val();
        
        doLogin(username, password, handleLoginData);
    });
});

// Actually doing the login, calling data_callback with received data
function doLogin(username, password, data_callback) {
    var success_callback = function(data) {            
        var parsed = JSON.parse(data);
        if("data" in parsed){            
            console.info("Logged in with User ID",parsed.data.user.id);

            // Set global User ID and VSDN-ID variable
            USER = parsed.data.user.id; 

            if(data_callback)
                data_callback(parsed);            
            
        }
        else {
            console.log("Login failed with Error:",parsed.error);
        }        
    }; 
    
    var error_callback = function(error) { 
        console.log("Authentication Error:",error);
    };
    
    // Sending data to server
    hyperflexAuthenticate(success_callback, [username, password], error_callback );
}

// Handles data returned from the server
function handleLoginData(data) {
    // Close login popup
    $('.loginPopup').modal('toggle');
    
    if( ("vsdns" in data.data) && data.data.vsdns.length > 0 ) {
        var vsdns = data.data.vsdns;

        console.log("Received vSDNS:",vsdns.length);

        // Read vsdns
        readVSDNS(vsdns, TEN_NW);

        TEN_NW.network.fit();
    }
}

