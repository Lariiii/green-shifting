import React from 'react';
import { isFinite } from 'lodash';

import { getShortenedZoneNameWithCountry } from '../../helpers/translation';
import { useCo2ColorScale } from '../../hooks/theme';
import { flagUri } from '../../helpers/flags';
import styled from 'styled-components';

export const CarbonIntensity = ({ intensity }) => {
  const co2ColorScale = useCo2ColorScale();

  return (
    <React.Fragment>
      <div className="emission-rect" style={{ backgroundColor: co2ColorScale(intensity) }} />
      {' '}
      <b>{Math.round(intensity) || '?'}</b> gCO₂eq/kWh
    </React.Fragment>
  );
};

export const MetricRatio = ({ value, total, format }) => (
  <small>{`(${isFinite(value) ? format(value) : '?'} / ${isFinite(total) ? format(total) : '?'})`}</small>
);

const Flag = styled.img``;

export const ZoneName = ({ zone }) => (
  <React.Fragment>
    <Flag className="flag" alt="" src={flagUri(zone)} />
    {getShortenedZoneNameWithCountry(zone)}
  </React.Fragment>
);
