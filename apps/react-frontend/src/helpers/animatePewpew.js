import {useRefWidthHeightObserver} from "../hooks/viewport";

var PewpewAnimation = function( params ){

  var PEWPEW_LINE_WIDTH = 5;
  var percent = 0;

  /*
  var project = function( lat, lon, pewpew) { // both in radians, use deg2rad if neccessary
    return params.project([lon, lat]);
  };*/


  function drawCurvePath( ctx, start, end, curveness, percent ) {

    var cp = [
         ( start[ 0 ] + end[ 0 ] ) / 2 - ( start[ 1 ] - end[ 1 ] ) * curveness,
         ( start[ 1 ] + end[ 1 ] ) / 2 - ( end[ 0 ] - start[ 0 ] ) * curveness
    ];
    
    ctx.moveTo( start[ 0 ], start[ 1 ] );
    
    for ( var t = 0; t <= percent / 100; t += 0.01 ) {

        var x = quadraticBezier( start[ 0 ], cp[ 0 ], end[ 0 ], t );
        var y = quadraticBezier( start[ 1 ], cp[ 1 ], end[ 1 ], t );
        
        ctx.lineTo( x, y );
    }
    
  }

  function quadraticBezier( p0, p1, p2, t ) {
    var k = 1 - t;
    return k * k * p0 + 2 * (1 - t) * t * p1 + t * t * p2; // this equation is a quadratic Bessel curve equation
  }


  var animate = function() {

    var g = params.canvas.getContext("2d");
    g.lineWidth = PEWPEW_LINE_WIDTH;
    g.strokeStyle = "#62B252";

    var lastFrameTime = Date.now();
    function draw() {
        var deltaMs = Date.now() - lastFrameTime;
        // 16 ms ~ 60 fps
        // if we take any longer than that, then scale the opacity
        // inversely with the time

        // reset canvas
        //g.clearRect( 0, 0,  2000, 2000);

        for (var i=0; i < params.data.length; i++) {
          var d = params.data[i];

          g.beginPath();
          drawCurvePath( 
              g,
              d.from,
              d.to,
              0.2,
              percent
          );
          g.stroke();

          percent = ( percent + 1 ) % 100;
        }

    }

    function frame() {
      lastFrameTime = Date.now();
      if (!pewpew.paused) {
        draw();
      }
      pewpew.animationRequest = requestAnimationFrame(frame);
    };

    frame();
  }

  var pewpew;

  var start = function(){

    stop();
    pewpew.started = true;
    pewpew.paused = false;

    animate();
  };

  var stop = function(){
    if (pewpew.field) pewpew.field.release();
    if (pewpew.animationRequest)
      cancelAnimationFrame(pewpew.animationRequest);
    pewpew.started = false;
    pewpew.paused = true;
  };


  pewpew = {
    params: params,
    start: start,
    stop: stop,
    started: false,
    paused: true
  };

  return pewpew;
}



// shim layer with setTimeout fallback
window.requestAnimationFrame = (function(){
  return  window.requestAnimationFrame       ||
          window.webkitRequestAnimationFrame ||
          window.mozRequestAnimationFrame    ||
          window.oRequestAnimationFrame ||
          window.msRequestAnimationFrame ||
          function( callback ){
            window.setTimeout(callback, 1000 / 20);
          };
})();
window.cancelAnimationFrame = (function(){
  return  window.cancelAnimationFrame       ||
          window.webkitCancelAnimationFrame ||
          window.mozCancelAnimationFrame    ||
          window.oCancelAnimationFrame ||
          window.msCancelAnimationFrame ||
          function( callback ){
            window.clearTimeout(callback)
          };
})();

export default PewpewAnimation;
