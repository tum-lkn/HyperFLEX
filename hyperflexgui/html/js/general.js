window.onerror = function(msg, url, line, col, error) {
   $("pre#jsError").html(msg+" ["+url+" Line: "+line+"]");
   $("#jsErrorBox").css("visibility","visible");
   return msg;
};

// Convert Hex Color string to RGB array
function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

// Number clamp function
Number.prototype.clamp = function(min, max) {
  return Math.min(Math.max(this, min), max);
};