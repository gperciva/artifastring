loadedInterfaceName = "violin";

interfaceOrientation = "portrait";

pages = [[
{
    "name": "refresh",
    "type": "Button",
    "bounds": [0, .0, .1, .1],
    "startingValue": 0,
    "isLocal": true,
    "mode": "contact",
    "ontouchstart": "interfaceManager.refreshInterface()",
    "stroke": "aaa",
    "label": "refrsh",
},
{
    "name":"st_e",
    "type":"Slider",
    "x":0.00, "y":.25,
    "width":.20, "height":.65,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
},
{
    "name":"st_a",
    "type":"Slider",
    "x":0.267, "y":.25,
    "width":.20, "height":.65,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
},
{
    "name":"st_d",
    "type":"Slider",
    "x":0.53, "y":.25,
    "width":.20, "height":.65,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
},
{
    "name":"st_g",
    "type":"Slider",
    "x":0.8, "y":.25,
    "width":.20, "height":.65,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
},
{
     "name" : "bow",
     "type" : "MultiTouchXY",
     "bounds": [0.1,0.0,0.8,0.2],
     "isMomentary": false,
     "maxTouches": 1,
    "stroke": "#e00",
    "color": "#00e",
}
]
];


