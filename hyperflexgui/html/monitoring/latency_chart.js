/* global CanvasJS */

function LatencyChart(options) {
    
    var parentthis = this;
    this.max_data = 90;
    this.chartdata = [];
    this.chart = new CanvasJS.Chart(options.container, {
        title: {
            text: options.title
        },
        axisX:{      
            interval: 20,
            intervalType: "second",
            labelAngle : 30,
            valueFormatString: "HH:mm:ss",
            gridThickness: 1,
            gridColor: "#eee"

        },
        axisY: {
            title: "Latency in ms",
            minimum: 0,
            maximum: 40,
            lineThickness: 1,
            lineColor: "#999",
            gridThickness: 1,
            gridColor: "#eee"
        },
        backgroundColor: null,
        data: [{
                type: "area",
                dataPoints: parentthis.chartdata,
                color: "rgba(0,75,141,0.7)"
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
        
    console.log("Latency Chart initialized!");

}

var latencyCharts = [];

$(function () {
    
    // Latency chart #1
    var options = {
        container: "latencyChart1",
        title: "Control Plane Latency Slice 1"
    };
    var chart = new LatencyChart(options);
    latencyCharts.push(chart);
    chart.fill_with_zeros();
    
    WSS.subscribe("latency1",function(topic,data){
            var x = new Date();
            var y = parseFloat(data);
            latencyCharts[0].add_datapoint(x, y, true, true);            
        }
    );
    
    
    
    // Latency chart #2
    var options = {
        container: "latencyChart2",
        title: "Control Plane Latency Slice 2"
    };
    var chart = new LatencyChart(options);
    latencyCharts.push(chart);
    chart.fill_with_zeros();
    
    WSS.subscribe("latency2",function(topic,data){
            var x = new Date();
            var y = parseFloat(data);
            latencyCharts[1].add_datapoint(x, y, true, true);            
        }
    );
    
});



