loadedInterfaceName = "violin";

interfaceOrientation = "portrait";

pages = [
  [
{
    "name": "refresh",
    "type": "Button",
    "bounds": [0, .0, .1, .1],
    "startingValue": 0,
    "isLocal": true,
    "mode": "contact",
    "ontouchstart": "interfaceManager.refreshInterface()",
    "stroke": "aaa",
    "label": "refresh",
},
{
    "name":"st_e",
    "type":"Slider",
    "x":0.00, "y":.45,
    "width":.20, "height":.45,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
    "backgroundColor": "#fff",
},
{
    "name":"st_a",
    "type":"Slider",
    "x":0.267, "y":.45,
    "width":.20, "height":.45,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
    "backgroundColor": "#fff",
},
{
    "name":"st_d",
    "type":"Slider",
    "x":0.53, "y":.45,
    "width":.20, "height":.45,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
    "backgroundColor": "#fff",
},
{
    "name":"st_g",
    "type":"Slider",
    "x":0.8, "y":.45,
    "width":.20, "height":.45,
    "isVertical" : true,
    "stroke": "#e00",
    "color": "#0e0",
    "backgroundColor": "#fff",
},
{
     "name" : "bow",
     "type" : "MultiTouchXY",
     "bounds": [0.1,0.0,0.8,0.4],
     "isMomentary": false,
     "maxTouches": 1,
    "stroke": "#e00",
    "color": "#00e",
    "backgroundColor": "#ddd",
}
]
];


