/* global CanvasJS */

function CPUChart(options) {

    var parentthis = this;
    this.max_data = 90;
    this.chartdata = [];
    this.chart = new CanvasJS.Chart(options.container, {
        title: {
            text: options.title
        },
        subtitles: options.subtitles,
        axisX: {
            interval: 20,
            intervalType: "second",
            labelAngle: 30,
            valueFormatString: "HH:mm:ss",
            gridThickness: 1,
            gridColor: "#eee"
        },
        axisY: {
            title: "CPU usage in %",
            minimum: 0,
            maximum: 100,
            lineThickness: 1,
            lineColor: "#999",
            gridThickness: 1,
            gridColor: "#eee"
        },
        backgroundColor: null,
        data: [{
                type: "area",
                dataPoints: parentthis.chartdata,
                color: "rgba(50,50,50,0.7)"
            }]
    });

    this.add_datapoint = function (x, y, render, remove_old)
    {
        render = render || true;
        this.chartdata.push({x: x, y: y});
        
        if(remove_old){
            // If time difference of first and last timestamp is too high, remove first
            for(var i = 0; i < this.chartdata.length; i++){
                if ( (this.chartdata[this.chartdata.length-1].x.getTime() - this.chartdata[i].x.getTime()) / 1000 > this.max_data) {
                    this.chartdata.shift();
                }
            }
        }
        if(render){this.chart.render();};
    };

    
    this.add_random_value = function () {
        var old_x = (this.chartdata.length >= 1) && (this.chartdata[this.chartdata.length-1].x) || new Date(); 
        var new_x = new Date(old_x.getTime() + 1000);
        
        var old_y = (this.chartdata.length >= 1) && this.chartdata[this.chartdata.length-1].y  || 25;
        var new_y = (old_y + parseInt((Math.random() - 0.5) * 2 * 10)).clamp(0, 100);
        
        this.add_datapoint(new_x, new_y,false);
        return [new_x, new_y];
    };
    
    this.fill_with_zeros = function() {
        for(var i = 0; i < this.max_data; i++){
            this.add_datapoint(new Date( Date.now() + (-this.max_data + i) *1000 ), 0, false, false);
        }
    };

    setTimeout(this.chart.render, 300);
    console.log("CPU Chart initialized!");

}

var cpucharts = [];


$(function () {
    // WEBSOCKET
    WSS = new Websocket(WSS_IP, WSS_PORT);
    
    
    // CPU chart #1
    var options = {
        container: "cpuChart1",
        title: "Hypervisor Instance",
        
    };
    var chart = new CPUChart(options);
    cpucharts.push(chart);
    chart.fill_with_zeros();
    
    
    WSS.subscribe("cpu1",function(topic,data){
            var x = new Date();
            var y = parseFloat(data);
            cpucharts[0].add_datapoint(x, y, true, true);            
        }
    );
    
    
    
    /*
    // CPU chart #2
    var options = {
        container: "cpuChart2",
        title: "Hypervisor Instance",
        subtitles: [
            {
                text: "", //"Offline",                
                fontColor: "red",
                fontSize: 20
            }
        ]
    };
    
    var chart = new CPUChart(options);
    cpucharts.push(chart);
    chart.fill_with_zeros();
    
    WSS.subscribe("cpu2",function(topic,data){
            var x = new Date();
            var y = parseFloat(data);
            cpucharts[1].add_datapoint(x, y, true, true);  
            
            // Set CPU chart #2 active if data > 0
            if(y > 0){
                cpucharts[1].chart.options.subtitles = null;
            }
        }
    );
    */
    

});



