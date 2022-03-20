/* eslint-disable react/jsx-no-target-blank */
/* eslint-disable jsx-a11y/anchor-has-content */
// TODO: re-enable rules
import React from 'react';
import { connect } from 'react-redux';
import styled from 'styled-components';

import { dispatchApplication } from '../../store';
import { useConditionalZoneHistoryFetch } from '../../hooks/fetch';
import {
  useCurrentZoneHistoryDatetimes,
  useCurrentZoneHistoryStartTime,
  useCurrentZoneHistoryEndTime,
} from '../../hooks/redux';
import TimeSlider from '../../components/timeslider';

import CountryPanel from './countrypanel';
import { useLocation } from 'react-router-dom';

const handleZoneTimeIndexChange = (timeIndex) => {
  dispatchApplication('selectedZoneTimeIndex', timeIndex);
};

const mapStateToProps = (state) => ({
  selectedZoneTimeIndex: state.application.selectedZoneTimeIndex,
});

const SocialButtons = styled.div`
  @media (max-width: 767px) {
    display: ${(props) => (props.pathname !== '/map' ? 'none !important' : 'block')};
  }
`;

const ZoneDetailsPanel = ({ selectedZoneTimeIndex }) => {
  const datetimes = useCurrentZoneHistoryDatetimes();
  const startTime = useCurrentZoneHistoryStartTime();
  const endTime = useCurrentZoneHistoryEndTime();
  const location = useLocation();

  // Fetch history for the current zone if it hasn't been fetched yet.
  useConditionalZoneHistoryFetch();

  return (
    <div className="left-panel-zone-details">
      <CountryPanel />
      
    </div>
  );
};

export default connect(mapStateToProps)(ZoneDetailsPanel);
