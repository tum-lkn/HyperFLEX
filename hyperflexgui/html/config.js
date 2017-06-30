/*  Hyperflex core RPC ip and port */
var JSONRPC_IP = "10.162.149.124";
var JSONRPC_PORT = 9469;

/*  Hyperflex core WebSocketServer ip and port */
var WSS_IP = "10.162.149.124";
var WSS_PORT = 9000;

/*  Perfbench RPC Dispatcher IPs and Port
    * Important: First RPC IP is used if no VSDNs are available (e.g. Migration demo)
*/
var JSONRPC_PERFBENCH_PORT = 8778;
var PERFBENCH_RPC_IPS = [
    "10.162.149.239", //"192.168.56.151",
    "10.162.149.100" //"192.168.57.160"
];

/*  Perfbench listening ip, port
    * Only used if no VSDN is available (Migration demo)
*/
var PERFBENCH_DEFAULT_IP = "192.168.57.101";
var PERFBENCH_DEFAULT_PORT = 6635;

var vsdn_colors = ["19bbd6","d7543d","bb19d6"];





var nodeTypes = {
    "hypervisor": {
        shape: 'icon',
        icon: {
            face: 'FontAwesome',
            code: '\uf1c0',
            size: 50,
            color: '#FF6A00'
        },
        font: {color: '#111', size: 16, background: "#eee"},
        physics: false,
        idPrefix: "hv",
        size: 30
    },
    "switch": {
        shape: 'icon',
        icon: {
            face: 'FontAwesome',
            code: '\uf0e8',
            size: 30,
            color: '#2B7CE9'
        },
        size: 15,
        physics: false,
        font: {color: '#111', size: 16, background: "#eee"},
        idPrefix: "s"
    },
    "switch_cplane": {
        shape: 'icon',
        icon: {
            face: 'FontAwesome',
            code: '\uf0e8',
            size: 20,
            color: '#999'
        },
        size: 15,
        physics: false,
        font: {color: '#111', size: 12, background: "#eee"},
        idPrefix: "s"
    },
    "host": {shape: 'image', image: '../img/pc.png', physics: false, font: {color: '#111', size: 10}, scaling: {min: 1, max: 50}, value: 10, idPrefix: "h"},
    "server": {shape: 'image', image: '../img/server.png', physics: false, idPrefix: "srv"},
    "controller": {
        shape: 'icon',
        icon: {
            face: 'FontAwesome',
            code: '\uf013',
            size: 20, //50,
            color: '#090'
        },
        size: 15,
        physics: false,
        font: {color: '#111', size: 12},
        idPrefix: "c"
    }
};
var edgeStyle = {
    controller: {
        width: 3,
        smooth: {enabled: false},
        color: {
            color: "#000033",
        },
        length: 100,
    },
    hypervisor: {
        width: 3,
        smooth: {enabled: false},
        color: {
            color: "#000033",
        },
        length: 150,
        physics: false
    },
    switch : {
        width: 1,
        smooth: {enabled: false},
        color: {
            color: "#333333",
        },
        selectionWidth: 3,
        length: 150,
    },
    tenant: {
        width: 3,
        smooth: {enabled: false, roundness: 0.3, type: "horizontal", },
        color: {
            color: "#ff9999",
        },
        physics: false,
        length: 150,
    },
    default: {
        width: 1,
        smooth: {enabled: false},
        color: {
            color: "#21436C",
        },
        physics: false,
        length: 150,
    }
};

var network_options = {
    autoResize: true,
    height: '100%',
    width: '100%',
    layout: {
        hierarchical: {
            enabled: false,
            levelSeparation: 100,
            direction: 'UD', // UD, DU, LR, RL
            sortMethod: 'directed' // hubsize, directed
        }
    },
    manipulation: {
        enabled: false,
        initiallyActive: false,
    },
    physics: {
        barnesHut: {
            gravitationalConstant: -1500,
            centralGravity: 0.1,
            springLength: 90,
            springConstant: 0.3,
            damping: 1,
        },
        repulsion: {
            centralGravity: -0.1,
            springLength: 100,
            springConstant: 0.05,
            nodeDistance: 50,
            damping: 0.2
        },
        hierarchicalRepulsion: {
            centralGravity: 0.0,
            springLength: 100,
            springConstant: 0.5,
            nodeDistance: 80,
            damping: 0.5
        },
        solver: "barnesHut",
    },
    edges: {
        color: {
            highlight: "#519090",
        },
        selectionWidth: 3,
    },
    nodes: {
    },
    interaction: {
        selectConnectedEdges: false
    }
};
