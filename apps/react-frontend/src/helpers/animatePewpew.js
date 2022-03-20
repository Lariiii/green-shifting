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
    g.fillStyle = "#62B252";

    var lastFrameTime = Date.now();
    function draw() {
        var deltaMs = Date.now() - lastFrameTime;
        // 16 ms ~ 60 fps
        // if we take any longer than that, then scale the opacity
        // inversely with the time
        var b = deltaMs < 16 ? 1 : 16 / deltaMs;

        // // Fade existing particle trails.
        // g.globalCompositeOperation = "destination-in";
        // // This is the parameter concerning the fade property/bug
        // g.globalAlpha = Math.pow(0.9, b);
        // g.fillRect(bounds.x, bounds.y, bounds.width, bounds.height);
        // // Prepare for drawing a new particle
        // g.globalCompositeOperation = "source-over";
        // g.globalAlpha = 1;

        // // Draw new particle trails.
        // buckets.forEach(function(bucket, i) {
        //     if (bucket.length > 0) {
        //         g.beginPath();
        //         g.strokeStyle = colorStyles[i];
        //         g.lineWidth = 1 + 0.25 * i;
        //         bucket.forEach(function(particle) {
        //             g.moveTo(particle.x, particle.y);
        //             g.lineTo(particle.xt, particle.yt);
        //             particle.x = particle.xt;
        //             particle.y = particle.yt;
        //         });
        //         g.stroke();
        //     }
        // });

        g.clearRect( 0, 0, 800, 800 );

        for (var i=0; i< params.data.length; i++) {
          var d = params.data[i];

          const [ fromX, fromY ] = d.from;
          const [ toX, toY ] = d.to;


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
        

          /*g.beginPath();
          g.moveTo(fromX, posY);
          g.lineTo(toX, posY+lineLength);
          g.stroke();*/

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
