import React, {
  useState,
  useEffect,
  useMemo,
} from 'react';
import { useSelector } from 'react-redux';
import { CSSTransition } from 'react-transition-group';
import styled from 'styled-components';

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

  const datacentersData = useSelector(state => state.data.dataCenters)

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
  useEffect(() => {
    if (isVisible && node && datacentersData && width && height) {

      const ctx = node.getContext('2d');
      ctx.clearRect(0, 0, width, height);

      const d = 75;

      for (var i=0; i < datacentersData.length; i++) {

        const dc = datacentersData[i];
        const [ x, y ]= project([dc.longitude, dc.latitude]);

        var img = new Image();
        img.onload = function() {
          ctx.drawImage(img, x-(d/2) , y-d, d, d);
        }
        img.src = "/images/datacenter.svg"
      }

    }
  }, [isVisible, node, datacentersData]);

  return (
    <CSSTransition
      classNames="fade"
      in={isVisible}
      timeout={300}
    >
      <Canvas
        id="datacenters"
        width={width}
        height={height}
        ref={ref}
      />
    </CSSTransition>
  );
};
