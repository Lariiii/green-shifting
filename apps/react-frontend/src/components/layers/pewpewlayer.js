import React, {
  useState,
  useEffect,
  useMemo,
} from 'react';
import { useSelector } from 'react-redux';
import { CSSTransition } from 'react-transition-group';
import styled from 'styled-components';
import PewpewAnimation from '../../helpers/animatePewpew';

import { useRefWidthHeightObserver } from '../../hooks/viewport';

const Canvas = styled.canvas`
  top: 0;
  left: 0;
  pointer-events: none;
  position: absolute;
  transition: opacity 300ms ease-in-out;
  width: 100%;
  height: 100%;
`;

export default ({ project, unproject }) => {
  const {
    ref, width, height, node,
  } = useRefWidthHeightObserver();
  const enabled = true;

  const [pewpew, setPewpew] = useState(null);

  const datacentersData = useSelector(state => state.data.dataCenters);
  const pewpewlines = useSelector(state => state.data.pewpewlines);

  const isMapLoaded = useSelector(state => !state.application.isLoadingMap);
  const isMoving = useSelector(state => state.application.isMovingMap);
  const isVisible = enabled && isMapLoaded && !isMoving;

  const viewport = useMemo(
    () => {
      const sw = unproject([0, height]);
      const ne = unproject([width, 0]);
      return [
        [[0, 0], [width, height]],
        width,
        height,
        [sw, ne],
      ];
    },
    [unproject, width, height],
  );

  // Kill and reinitialize Windy every time the layer visibility changes, which
  // will usually be at the beginning and the end of dragging. Windy initialization
  // is currently very slow so we take it to the next render cycle so that the
  // rendering of everything else is not blocked. This will hopefully be less
  // hacky once Windy service is merged here and perhaps optimized via WebGL.
  // See https://github.com/tmrowco/electricitymap-contrib/issues/944.
  // useEffect(() => {
  //   if (isVisible && node && datacentersData && pewpewlines && width && height) {

  //     const ctx = node.getContext('2d');
  //     ctx.clearRect(0, 0, width, height);

  //     const d = 75;

  //     let fromDatacenter;
  //     let toDatacenter;

  //     for (var i=0; i < pewpewlines.length; i++) {
  //       for (var j=0; j < datacentersData.length; j++) {
  //         const datacenter = datacentersData[j];
  //         if (datacenter.name == pewpewlines[i].from) {
  //           fromDatacenter = datacenter;
  //         } else if (datacenter.name == pewpewlines[i].to) {
  //           toDatacenter = datacenter;
  //         }
  //       }

  //       if (fromDatacenter && toDatacenter) {
  //         const [ fromLon, fromLat ] = project([fromDatacenter.lon, fromDatacenter.lat]);
  //         const [ toLon, toLat ] = project([toDatacenter.lon, toDatacenter.lat]); 

  //         animate(canvas);

  //         ctx.beginPath();
  //         ctx.moveTo(fromLon, fromLat);
  //         ctx.lineTo(toLon, toLat);
  //         //ctx.bezierCurveTo(, toLon, toLat)
  //         ctx.stroke()
  //       }
  //     }

  //   }
  // }, [isVisible, node, pewpewlines, datacentersData]);


  function getCoordinates() {

    var fromDatacenter = null;
    var toDatacenter = null;

    var data = [];

    for (var i=0; i < pewpewlines.length; i++) {
      for (var j=0; j < datacentersData.length; j++) {
        const datacenter = datacentersData[j];
        if (datacenter.name == pewpewlines[i].from) {
          fromDatacenter = datacenter;
        } else if (datacenter.name == pewpewlines[i].to) {
          toDatacenter = datacenter;
        }
        if (fromDatacenter && toDatacenter) break;
      }

      if (fromDatacenter && toDatacenter) {
        data.push({ 
          'from': project([fromDatacenter.lon, fromDatacenter.lat]),
          'to': project([toDatacenter.lon, toDatacenter.lat])
        });
      }
    }

    return data
  }
  


  useEffect(() => {
    if (!pewpew && isVisible && node && pewpewlines && datacentersData) {
      const data = getCoordinates();

      const w = new PewpewAnimation({
        canvas: node,
        data: data,
        project,
        unproject,
      });
      w.start(...viewport);
      // Set in the next render cycle.
      setTimeout(() => { setPewpew(w); }, 0);
    } else if (pewpew && !isVisible) {
      pewpew.stop();
      setPewpew(null);
    }
  }, [pewpew, isVisible, node, pewpewlines, datacentersData]);

  return (
    <CSSTransition
      classNames="fade"
      in={isVisible}
      timeout={300}
    >
      <Canvas
        id="pewpew"
        width={width}
        height={height}
        ref={ref}
      />
    </CSSTransition>
  );
};
