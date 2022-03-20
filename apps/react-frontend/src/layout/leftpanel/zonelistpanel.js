import React from 'react';
import styled from 'styled-components';

import { __ } from '../../helpers/translation';
import { dispatchApplication } from '../../store';

import SearchBar from '../../components/searchbar';
import ZoneList from '../../components/zonelist';

const documentSearchKeyUpHandler = (key, searchRef) => {
  if (key === '/') {
    // Reset input and focus
    if (searchRef.current) {
      searchRef.current.value = '';
      searchRef.current.focus();
    }
  } else if (key && key.match(/^[A-z]$/)) {
    // If input is not focused, focus it and append the pressed key
    if (searchRef.current && searchRef.current !== document.activeElement) {
      searchRef.current.value += key;
      searchRef.current.focus();
    }
  }
};

/*const ZoneListPanel = () => (
  <div className="left-panel-zone-list">
    <div className="zone-list-header">
      <div className="title">
        {' '}
        {__('left-panel.zone-list-header-title')}
      </div>
      <div className="subtitle">{__('left-panel.zone-list-header-subtitle')}</div>
    </div>

    <SearchBar
      className="zone-search-bar"
      placeholder={__('left-panel.search')}
      documentKeyUpHandler={documentSearchKeyUpHandler}
      searchHandler={query => dispatchApplication('searchQuery', query)}
    />

    <ZoneList />

    <InfoText />
  </div>
);*/

export const StyledInput = styled.input`
  height: 32px;
  font-size: 16px;
`;

export const RangeInput = styled.input`
  height: 32px;
  background: #62B252;
`;


export const Spacer = styled.div`
  padding-top: 20px;
  width: 12px;
`;

export const Row = styled.div`
`;


export const Button = styled.button`
  height: 48px;
  background: #62B252;
  border-style: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: 20px;
  color: #fff;
`;
/*
const [location, setLocation] = useState('');
const [company, setCompany] = useState('');
const [pvSize, setpvSize] = useState(0);
const [vmNumber, setVmNumber] = useState(0);
const [windSize, setWindSize] = useState(0);
const [lat, setLat] = useState(0);
const [lon, setLon] = useState(0);*/ 

const ZoneListPanel = ({
  //onChange, locationName, companyName, pvSize, vmNumber, windSize, lat, lon 
}) => {


  function sendData() {
    console.log("not yet implemented")
  }

  function dummy() {}

  return(
    <div className="left-panel-zone-list">
      <div className="zone-list-header">
        <div className="title">
          {' '}
          {__('left-panel.zone-list-header-title')}
        </div>
        <div className="subtitle">{__('left-panel.zone-list-header-subtitle')}</div>
      </div>

      <h3>Location name</h3>
      <StyledInput type="text" onChange={dummy} onInput={dummy} value={''}></StyledInput>
      <Spacer />

      <h3>Company</h3>
      <StyledInput type="text" onChange={dummy} onInput={dummy} value={''}></StyledInput>
      <Spacer />

      <h3>Location</h3>
      <Row>
        <StyledInput placeholder="Latitude" type="text" onChange={dummy} onInput={dummy} value={''}></StyledInput><Spacer />
        <StyledInput placeholder="Longitude" type="text" onChange={dummy} onInput={dummy} value={''}></StyledInput>
      </Row>
      <Spacer />

      <h3>Number of VMs: 500</h3>
      <RangeInput type="range" min="0" max="10000" value={''} onChange={dummy} onInput={dummy}></RangeInput> { '' }
      <Spacer />

      <h3>Size of photovoltaics: 500 kWh</h3>
      <RangeInput type="range" value={''} onChange={dummy} onInput={dummy}></RangeInput> 
      <Spacer />

      <h3>Size of wind turbines: 500 kWh</h3>
      <RangeInput type="range" value={''} onChange={dummy} onInput={dummy}></RangeInput> 
      <Spacer />

      <Button onClick={sendData}>
        Send
      </Button>

    </div>

  );
};

export default ZoneListPanel;
